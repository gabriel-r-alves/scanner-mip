from monitoramento_impressoras_backend.utils.loggin import log_error, log_info
from monitoramento_impressoras_backend.domain.dtos import ScanData

from .scanner import Scanner


class ScanService:
    def __init__(self, printer_repository = None, branch_repository = None, branch_network_repository = None, error_repository= None) -> None:
        self.printer_repository = printer_repository
        self.branch_repository = branch_repository
        self.network_repository = branch_network_repository
        self.error_repository = error_repository
        
        self.scanner = Scanner(
            printer_repository=printer_repository,
            branch_repository=branch_repository,
            branch_network_repository=branch_network_repository,
            error_repository=error_repository
        )
    
    
    async def collect_scan_data(self, type_scan):
        scan_data_list = []
        if type_scan == "db": # temporario
            scan_data_list = await self.scanner.scan_db()
        
        elif type_scan == "branch": # temporario
            scan_data_list = await self.scanner.scan_branches()
        
        filtrered_scan_data = self._filter_scan_data(scan_data_list)
        return filtrered_scan_data

    
    def _filter_scan_data(self, scan_data_list: list[ScanData]) -> list[ScanData]:
        return scan_data_list
    