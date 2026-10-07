from typing import Optional

from .printer_sync_conext import PrinterSyncContext

from monitoramento_impressoras_backend.database.models.printer import StatusPrinter
from monitoramento_impressoras_backend.database.models import Printer

from monitoramento_impressoras_backend.utils.loggin import log_error, log_info


class PrinterSynchronizer:
    def __init__(self, printer_repository, position_repository) -> None:
        self.printers_repo = printer_repository
        self.position_repo = position_repository
    
    
    def sync_printer_success(self, context: PrinterSyncContext) -> None:
        """
        Resolve qual impressora usar, atualiza dados SNMP e salva.
        Consolidado para manter coesão: estão intimamente ligados.
        """
        log_info("Sincronização de impressora online...")
        self._obtain_printers(context)
        log_info("Sucesso ao obter a impressora...")
        self._resolve_printer(context)
        log_info("Sucesso ao resolver a impressora...")
        self._update_with_printer_data(context)
        log_info("Sucesso ao atualizar as impressoras...")
        self._save_to_db(context)
    

    def sync_printer_status(self, context: PrinterSyncContext):
        """Trata impressora que estava offline ou com algum erro na coleta, atualizando apenas o status"""
        log_info("Sincronização de impressora offline ou com erro de coleta...")
        
        if context.printer_by_ip is None:
            log_error(f"[X] IP não cadastrado: {context.scan_data.ip}")
            return None

        printer = context.printer_by_ip
        
        log_info(
            f"[X] Status da Impressora: {printer.num_serial} IP: {context.scan_data.ip}"
            f"Conexão: {context.scan_data.connection}, Status do Scan:  {context.scan_data.status}"
        )

        # Atualizar status e salvar
        printer.status = StatusPrinter.from_scan(context.scan_data)
        
        context.printer = printer
        context.is_new = False
    
        self.printers_repo.save(printer)
        
    
    def _obtain_printers(self, context: PrinterSyncContext):
        """Obtém impressora por IP e Serial do BD"""
        scan_data = context.scan_data
        context.printer_by_ip = self.printers_repo.get_by_ip(scan_data.ip)
        context.printer_by_serial = self.printers_repo.get_by_serial(scan_data.printer_data.num_serial) if scan_data.printer_data is not None else None
    
     
    def _resolve_printer(self, context: PrinterSyncContext) -> None:
        """Valida qual impressora usar e marca se é nova"""
        printer_ip = context.printer_by_ip
        printer_serial = context.printer_by_serial
        
        # Caso 1: Serial existe no BD
        if printer_serial is not None:
            context.printer = printer_serial
            context.is_new = False
            
            # Se há conflito de IP, limpar o outro
            if printer_ip and printer_ip.num_serial != printer_serial.num_serial:
                self._clear_conflicting_printer(printer_ip)

        # Caso 2: Só IP existe (impressora nova com serial agora conhecida)
        elif printer_ip is not None:
            context.printer = printer_ip
            context.is_new = False

        # Caso 3: Nenhum existe (impressora totalmente nova)
        else:
            context.printer = Printer.from_scan_data(context.scan_data)
            context.is_new = True
                
    
    def _update_with_printer_data(self, context: PrinterSyncContext) -> None:
        """Atualiza dados SNMP na impressora"""
        printer = context.printer
        
        scan_data = context.scan_data

        if printer is None:
            log_error("Erro ao carregar impressora no Synchronizer, impressora está vazia")
            raise # corrigir aqui
        
        # Aplicar dados SNMP
        if not context.is_new: printer.apply_scan_data(scan_data=scan_data)

        # Atualizar posição se disponível
        self._update_position(printer, scan_data.ip)


    def _save_to_db(self, context: PrinterSyncContext) -> None:
        """Persiste impressora no BD"""
        self.printers_repo.save(context.printer)


    def _clear_conflicting_printer(self, conflicting_printer: Printer) -> None:
        """Remove IP de impressora em conflito"""
        log_error(f"[!] Limpando IP {conflicting_printer.ip} de {conflicting_printer.num_serial}")
        conflicting_printer.clear_network_info()
        self.printers_repo.save(conflicting_printer)


    def _update_position(self, printer: Printer, ip: str) -> None:
        """Atualiza posição se disponível"""
        position = self.position_repo.get_by_ip(ip)
        
        if position and not printer.position:
            log_info(f"[✓] Posição atualizada para {ip}")
            printer.apply_position(position.name)
        elif not position:
            log_error(f"[!] Posição não encontrada para {ip}")

