import asyncio
import ipaddress

from .scan_ping import async_scan_ping
from .scan_snmp import ScanSnmp
from .scan_sgd import ScanSgd
from .validator import ScanValidator
from .post_scan import PostScan

from monitoramento_impressoras_backend.database.models import BranchNetwork, ErrorCounter, Printer
from monitoramento_impressoras_backend.domain.dtos import ScanData, PrinterData
from monitoramento_impressoras_backend.domain.enums import CollectorType, ConnectionStatus, ScanStatus, ScanErrorType

from monitoramento_impressoras_backend.utils.loggin import log_error, log_info


class Scanner:
    def __init__(self, printer_repository = None, branch_repository = None, branch_network_repository = None, error_repository= None) -> None:
            self.semaphore = asyncio.Semaphore(70)
    
            self.printer_repository = printer_repository
            self.branch_repository = branch_repository
            self.network_repository = branch_network_repository
            self.error_repository = error_repository
    
            self.validator = ScanValidator()
            self.post_scan = PostScan()
    
            self.scan_snmp = ScanSnmp()
            self.scan_sgd = ScanSgd()
    
            self.scanners = {
                CollectorType.SNMP: self.scan_snmp.async_snmp,
                CollectorType.SGD: self.scan_sgd.async_collect
            }
            
            self.MAX_IPS_PER_NETWORK = 4096
    
    
    async def scan_db(self) -> list[ScanData]:
        log_info("Verificando repositório de impressoras...")
        if self.printer_repository is None:
            log_error("[X] ERRO CRITICO. REPOSITORY NÃO CARREGADO.")
            return []
        log_info("SUCESSO!")

        log_info("Verificando repositório de erros...")
        if self.error_repository is None:
            log_error("[X] ERRO CRITICO. REPOSITORY NÃO CARREGADO.")
            return []
        log_info("SUCESSO!")

        printers_db = self.printer_repository.get_all_printers()

        log_info("Obtendo impressoras do Banco de Dados...")
        if not printers_db:
            log_error("[X] Sem impressoras cadastrada no Banco de Dados.")
            return []

        tasks_list = [
            asyncio.create_task(self._printer_ping_and_scan(printer))
            for printer in printers_db
        ]

        snmp_scan_result = await asyncio.gather(*tasks_list, return_exceptions=False) if tasks_list else []
        log_info(f"Impressoras para scan sendo enviadas: {len(snmp_scan_result)}")

        return snmp_scan_result if snmp_scan_result else []


    async def scan_branches(self) -> list[ScanData]:
        log_info("Verificando repositório de Filiais...")
        if self.branch_repository is None:
            log_error("[X] ERRO CRITICO. REPOSITORY NÃO CARREGADO.")
            return []
        log_info("SUCESSO!")

        log_info("Verificando repositório de Redes das filais...")
        if self.network_repository is None:
            log_error("[X] ERRO CRITICO. REPOSITORY NÃO CARREGADO.")
            return []
        log_info("SUCESSO!")

        log_info("Obtendo filiais do db...")
        branches_db = self.branch_repository.get_all_branches()

        if not branches_db:
            log_error("[X] Lista vazia! Nenhuma filial cadastrada.")
            return []

        results_snmp_branch = []

        for branch in branches_db:
            log_info(f"Obtendo redes da filial {branch.id} {branch.name}")

            networks = self.network_repository.get_by_filial(branch.id)
            if not networks:
                log_error("[X] Não possui rede cadastrada!")
                continue

            for network in networks:
                if not network.active:
                    continue

                results_snmp_branch.extend(await self._scan_network(network))

        return results_snmp_branch


    async def _scan_network(self, network: BranchNetwork) -> list[ScanData]:
        try:
            # Converte os endereços legíveis de volta para objetos de IP
            start_addr = ipaddress.ip_address(network.start_readable)
            end_addr = ipaddress.ip_address(network.end_readable)

            if start_addr.version != end_addr.version:
                log_error(
                    f"[X] Rede {network.id}: IPs de versões diferentes: "
                    f"{start_addr} -> {end_addr}"
                )
                return []

            total_ips = int(end_addr) - int(start_addr) + 1

            if total_ips <= 0:
                log_error(
                    f"[X] Rede {network.id}: range inválido: "
                    f"{start_addr} -> {end_addr}"
                )
                return []

            if total_ips > self.MAX_IPS_PER_NETWORK:
                log_error(
                    f"[X] Rede {network.id}: range muito grande: "
                    f"{start_addr} -> {end_addr} "
                    f"({total_ips} IPs)"
                )
                return []

            log_info(
                f"[SCAN] Rede {network.id} - {network.description}: "
                f"{start_addr} -> {end_addr} "
                f"({total_ips} IPs)"
            )
            
            ips_to_scan = [
                str(ipaddress.ip_address(ip_int))
                for ip_int in range(int(start_addr), int(end_addr) + 1)
            ]

            log_info(
                f"[SCAN] Lista de {len(ips_to_scan)} IPs criada."
            )

            network_task_list = [
                self._network_ping_and_scan(
                    network=network,
                    ip=ip
                )
                for ip in ips_to_scan
            ]
            
            log_info(
                f"[SCAN] Iniciando {len(network_task_list)} tarefas."
            )

        except Exception as e:
            log_error(
                f"Erro ao processar range da rede {network.id}: {e}"
            )
            return []

        results = await asyncio.gather(
            *network_task_list,
            return_exceptions=False,
        )

        log_info(
            f"[SCAN] Finalizada rede {network.id}."
        )

        return results


    async def _printer_ping_and_scan(self, printer: Printer) -> ScanData:
        """Pipeline por impressora — prepara validação e metadata e chama o pipeline genérico."""
        log_info(f"Inciando o agendamento do scan da impressora {printer.num_serial} {printer.ip} {printer.branch_current_id}")

        # Validação específica da impressora
        log_info("Iniciando validação da impressora...")
        valid, error = self.validator.validate_printer(printer)
        log_info("Validação concluida!")

        if not valid:
            log_error(f"[X] Scan cancelado! Impressora invalida! motivo: {error}")
            scan_resp = ScanData(
                ip=printer.ip,
                network_id=printer.network_id,
                branch_id=printer.branch_current_id,
                connection=ConnectionStatus.INITIALIZED,
                status=ScanStatus.INVALID_PRINTER,
                collector_type=None,
                printer_data=self._printer_to_data(printer)
            )
            return scan_resp

        # Não sobrescrever o objeto original — converte localmente
        collector_type = CollectorType(printer.collector_type)

        return await self._ping_and_scan(
            ip=printer.ip,
            branch_id=printer.branch_current_id,
            network_id=printer.network_id,
            collector_type=collector_type,
            is_printer=True,
            printer=printer
        )


    async def _network_ping_and_scan(self, network: BranchNetwork, ip: str) -> ScanData:
        """Pipeline por rede de filial — prepara metadata e chama pipeline genérico."""
        return await self._ping_and_scan(
            ip=ip,
            branch_id=network.branch_id,
            network_id=network.id,
            collector_type=network.collector_type,
            is_printer=False,
            printer=None
        )


    async def _ping_and_scan(
        self,
        *,
        ip: str,
        branch_id: int | None = None,
        network_id: int | None = None,
        collector_type,
        is_printer: bool = False,
        printer: Printer | None = None,
        PING_TIMEOUT: float = 2.0
    ) -> ScanData:
        """Pipeline unificado: ping -> (opcional) scan.
        O timeout do scanner agora é responsabilidade do próprio scanner.
        """
        scan_resp = ScanData(
            ip=ip,
            network_id=network_id,
            branch_id=branch_id,
            connection=ConnectionStatus.INITIALIZED,
            status=ScanStatus.INITIALIZED,
            collector_type=collector_type,
            printer_data=None
        )

        log_info(f"Iniciando validação da necessidade de coleta... Coletor: {collector_type}")

        # Normaliza o collector_type para CollectorType (aceita enum ou raw value)
        try:
            collector_type = CollectorType(collector_type)
        except Exception as e:
            log_error(f"[X] Tipo de coletor inválido para {ip}: {e}")
            scan_resp.status = ScanStatus.INVALID_SCANNER
            return scan_resp

        if not collector_type.requires_collector:
            log_info("Coleta não habilitada.")
            scan_resp.status = ScanStatus.COLLECTION_NOT_REQUIRED
            return scan_resp

        log_info("Coleta habilitada!")

        # Ping
        log_info("Pingando o ip...")
        try:
            is_online = await asyncio.wait_for(async_scan_ping(ip), timeout=PING_TIMEOUT)
        except asyncio.TimeoutError:
            scan_resp.connection = ConnectionStatus.OFFLINE
            scan_resp.status = ScanStatus.PING_TIMEOUT
            log_error(f"[X] Ping timeout {ip}")
            return scan_resp
        
        except Exception as e:
            scan_resp.connection = ConnectionStatus.OFFLINE
            scan_resp.status = ScanStatus.INTERNAL_ERROR
            log_error(f"[X] Erro no ping {ip}: {e}")
            return scan_resp

        if not is_online:
            scan_resp.connection = ConnectionStatus.OFFLINE
            scan_resp.status = ScanStatus.PING_SUCCESS
            log_info(f"[X] IP {ip} OFFLINE")
            return scan_resp

        scan_resp.connection = ConnectionStatus.ONLINE
        scan_resp.status = ScanStatus.PING_SUCCESS
        log_info(f"[✓] IP {ip} online")        

        # Se o coletor não precisa varrer dados, devolve sucesso só do ping
        if not collector_type.requires_scan:
            log_info("Coletor sem coleta de dados, somente PING.")            
            return scan_resp

        # ============================================================================
        
        # Obtém scanner
        scanner = self.scanners.get(collector_type)
        
        if scanner is None:
            log_error(f"[X] Scanner não encontrado para tipo {collector_type}")
            scan_resp.status = ScanStatus.INVALID_SCANNER
            return scan_resp

        log_info(f"Coletor com coleta de dados. Iniciando coleta pelo scanner {collector_type}")

        # IMPORTANT: o timeout do scanner foi movido para dentro do scanner.
        async with self.semaphore:
            # chama o scanner sem wait_for; o scanner controla seu timeout internamente
            result = await scanner(ip=ip)
            if result.success:
                scan_resp.status = ScanStatus.COLLECT_SUCCESS
                scan_resp.printer_data = result.printer_data

            elif result.error_type is ScanErrorType.TIMEOUT:
                log_error(f"[X] Timeout no scanner para {ip}")
                scan_resp.status = ScanStatus.SCANNER_TIMEOUT

            elif result.error_type is ScanErrorType.NO_DATA:
                log_error(f"[X] Scanner {collector_type} não retornou dados para {ip}")
                scan_resp.status = ScanStatus.COLLECT_EMPTY

            else:
                log_error(f"[X] Erro no scanner {ip}: {result.error} {result.error_type}")
                scan_resp.status = ScanStatus.INTERNAL_ERROR
        
            return scan_resp

    # mover para validator antes de sync
    def _generate_scan_error(self, printer, error):
        error = ErrorCounter(
            num_serial=printer.num_serial,
            branch_id=printer.branch_current_id,
            ip=printer.ip,
            status=printer.status,
            named_error=error
        )
        return error


    def _printer_to_data(self, printer:Printer):
        return PrinterData(
            num_serial=printer.num_serial,
            model=printer.model,
            counter=str(printer.counter)
        )