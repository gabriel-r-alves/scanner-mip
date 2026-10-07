from dataclasses import dataclass
from typing import Optional
from monitoramento_impressoras_backend.domain.enums import ConnectionStatus, ScanStatus, CollectorType
from .printer_data import PrinterData


@dataclass
class ScanData:
    ip: str | None
    
    connection: ConnectionStatus
    status: ScanStatus
    
    branch_id: int
    network_id: int | None
    
    collector_type: CollectorType | None
    printer_data: PrinterData | None
    
    @property
    def num_serial(self) -> Optional[str]:
        return self.printer_data.num_serial if self.printer_data else None
    
    @property
    def model(self) -> Optional[str]:
        return self.printer_data.model if self.printer_data else None
    
    @property
    def counter(self) -> Optional[str]:
        return self.printer_data.counter if self.printer_data else None
        
    @property
    def has_printer_data(self):
        return self.printer_data is not None

    @property
    def is_online(self) -> bool:
        return self.connection == ConnectionStatus.ONLINE
    
    @property
    def is_syncable(self) -> bool:
        return (
            self.status == ScanStatus.COLLECT_SUCCESS
            and self.has_printer_data
            and self.printer_data.is_valid
        )
    
    @property
    def has_error(self) -> bool:
        if self.status == ScanStatus.PING_SUCCESS:
            return self.connection != ConnectionStatus.ONLINE

        if (
            self.status == ScanStatus.COLLECT_SUCCESS
            and self.is_syncable
        ):
            return False

        return True