from collections import defaultdict, Counter

from .printer_sync_conext import PrinterSyncContext
from .validator import SyncValidator
from .printer_synchronizer import PrinterSynchronizer
from .post_sync import PostSync

from monitoramento_impressoras_backend.utils.loggin import log_error, log_info

from monitoramento_impressoras_backend.domain.dtos import ScanData
from monitoramento_impressoras_backend.repositories import (
    PrinterRepository,
    RawCounterRepository,
    LogChangePrinterRepository,
    ErrorCounterRepository,
    PositionRepository
)


class SyncService:
    def __init__(self,
        printers_repository: PrinterRepository,
        counters_repository: RawCounterRepository,
        errors_repository: ErrorCounterRepository,
        logs_repository: LogChangePrinterRepository,
        position_repository: PositionRepository
    ):
        self.printers_repository = printers_repository
        self.counters_repository = counters_repository
        self.errors_repository = errors_repository
        self.logs_repository = logs_repository
        self.position_repository = position_repository
        
        self.validator = SyncValidator()
        self.printer_synchronizer = PrinterSynchronizer(self.printers_repository, self.position_repository)
        self.post_sync = PostSync(counters_repository, errors_repository, logs_repository)
    
    
    def sync_printers(self, scan_data_list: list[ScanData]):
        """
        FLUXO PRINCIPAL:
        1. Validar resposta scan_data
        2. Sincronizar (ou tratar offline)
        3. Pós-sync (detectar mudanças, persistir)
        4. Commit (automático via ORM)
        """
        
        log_info("Iniciando sincronização das impressoras...")
        
        stats = defaultdict(int)
                
        for scan_data in scan_data_list:
            log_info(f"SINCRONIZAÇÃO - {scan_data.ip} - {scan_data.connection} - {scan_data.num_serial}")
            
            if scan_data.printer_data is not None:
                log_info(f"[DEBUG] {scan_data.printer_data.num_serial} - {scan_data.printer_data.model} - {scan_data.printer_data.counter}")
            else:
                log_info("[DEBUG] Sem dados de coleta")

            # ========== LOOP POR IMPRESSORA ==========
            self._sync_single_printer(scan_data, stats)
        
        log_info("[✓] Sincronização concluída")
        
        # Log final
        self._log_summary(stats, scan_data_list)
            
            
    def _sync_single_printer(self, scan_data: ScanData, stats: dict) -> None:
        """
        Sincroniza UMA impressora.
        Segue o fluxo: validar → sincronizar → pós-sync
        """
        
        # ========== [1] VALIDAÇÃO ==========
        valid_result = self.validator.validate_network_scan_response(scan_data)
        
        if not valid_result.valid:
            log_error(f"[X] Resposta inválida ({scan_data.ip}): {valid_result.error}")
            return None
        
        log_info(f"[!] Resposta válida.")
        
        sync_context = PrinterSyncContext(
            scan_data=scan_data,
            printer_by_ip=self.printers_repository.get_by_ip(scan_data.ip),
            printer_by_serial=self.printers_repository.get_by_serial(scan_data.num_serial) if scan_data.num_serial is not None else None
        )
        
        valid_result = self.validator.validate_scan_data_syncable(sync_context)
        
        if not valid_result.valid:
            log_error(f"[!] Não sincronizável ({scan_data.ip}): {valid_result.error}")
            return None
        
        log_info(f"[!] Resposta sincronizavel.")
        # log_info(valid_result)
        # log_info(sync_context)
        
        # ========== [2] SINCRONIZAÇÃO ==========
        
        if scan_data.is_syncable:
            self.printer_synchronizer.sync_printer_success(sync_context)
        
        else:
            self.printer_synchronizer.sync_printer_status(sync_context)

        # ========== [3] PÓS-SYNC ==========
        
        action_label, increment = self.post_sync.detect_and_persist_changes(sync_context)

        if increment:
            stats[action_label] = stats.get(action_label, 0) + increment

        if scan_data.has_error:
            self.post_sync.save_error(sync_context)
        

    def _log_summary(self, stats: dict, scan_data_list: list[ScanData]) -> None:
        """Log de resumo final"""
        log_info("")
        log_info("[>] Exibindo Log de Resumo")
        log_info("")
        log_info("[!] Exibindo Resumo de Scan")
        connections = Counter()
        status_por_connection = defaultdict(Counter)
            
        for scan in scan_data_list:  # lista de ScanData
            # log_info(scan)
            conn = scan.connection.value
            status = scan.status.value
    
            connections[conn] += 1
            status_por_connection[conn][status] += 1
        
        log_info("Connections")
            
        for conn, total in connections.items():
            log_info(f"{conn}: {total}")
    
            log_info("  Status:")
            for status, qtd in status_por_connection[conn].items():
                log_info(f"    - {status}: {qtd}")
        log_info("")            
        log_info("[!] Exibindo Resumo de Sync")
        for action, count in stats.items():
            log_info(f"{action}: {count}")
        
        all_printers = self.printers_repository.get_all_printers()
        log_info(f"Total de impressoras no BD: {len(all_printers)}")
        log_info("")
        
        
        
        