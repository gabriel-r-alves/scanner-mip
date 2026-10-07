from dataclasses import dataclass, field
from monitoramento_impressoras_backend.domain.dtos import ScanData
from monitoramento_impressoras_backend.database.models import Printer
from typing import Optional


@dataclass
class PrinterSyncContext:
    """Contexto mantido durante sincronização de uma impressora"""
    scan_data: ScanData
    printer_by_ip: Optional[Printer] = None
    printer_by_serial: Optional[Printer] = None
    printer: Optional[Printer] = None
    is_new: bool = False
    detected_changes: dict = field(default_factory=dict)
    synchronized: bool = False