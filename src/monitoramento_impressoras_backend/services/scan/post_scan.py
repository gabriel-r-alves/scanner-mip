from monitoramento_impressoras_backend.domain.dtos import ScanData
from monitoramento_impressoras_backend.domain.enums import ScanStatus


class PostScan:
    def __int__(self):
        pass
    
    def filter_data(self, scan_data_list: list[ScanData]) -> list[ScanData]:
        for resp in scan_data_list:
            if resp.status is ScanStatus.INVALID_PRINTER:
                # Gera um erro resitravel no ErrorCounter
                pass
            
        
        filtered_scan_data = scan_data_list
        return filtered_scan_data
    
    