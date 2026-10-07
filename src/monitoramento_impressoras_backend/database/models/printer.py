from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from typing import Optional

from sqlalchemy       import ForeignKey, String, Integer, TIMESTAMP, Text, text, Boolean
from sqlalchemy.sql   import func
from sqlalchemy.orm   import Mapped, mapped_column, relationship

from monitoramento_impressoras_backend.domain.enums import CollectorType, ConnectionStatus, ScanStatus
from monitoramento_impressoras_backend.domain.dtos import ScanData

from ..base import Base


class PrinterType(StrEnum):
    TERMIC = "termica"
    LASER = "laser"


class ConnectionType(StrEnum):
    IP = "ip"
    USB = "usb"


class StatusPrinter(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    SCAN_ERROR = "scan_error"
    SCAN_TIMEOUT = "scan_timeout"
    DESCONHECIDO = "desconhecido" # sistema
    MANUTENCAO = "manutencao" # manualmente 
    TRANSPORTE = "transporte" # Manualmente
    
    @classmethod
    def from_scan(cls, scan_data: ScanData):
        if scan_data.status == ScanStatus.PING_TIMEOUT:
            return cls.OFFLINE

        if scan_data.status == ScanStatus.SCANNER_TIMEOUT:
            return cls.SCAN_TIMEOUT

        if scan_data.has_error:
            return cls.SCAN_ERROR

        if scan_data.connection == ConnectionStatus.ONLINE:
            return cls.ONLINE

        return cls.OFFLINE


class PrinterFunction(StrEnum):
    OPERACIONAL = "operacional"
    BACKUP = "backup"


class Printer(Base):
    __tablename__ = "printers"

    num_serial: Mapped[str] = mapped_column(String(100), primary_key=True)

    branch_native_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id"))
    branch_current_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id"))
    network_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("branch_networks.id"))

    model: Mapped[Optional[str]] = mapped_column(String(100))
    
    printer_type: Mapped[Optional[PrinterType]] = mapped_column(String(30), server_default=text(f"'{PrinterType.LASER}'"))
    
    position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    ip: Mapped[Optional[str]] = mapped_column(String(18), nullable=True)
    
    connection_type: Mapped[ConnectionType] = mapped_column(String(30), server_default=text(f"'{ConnectionType.IP}'"))
    
    status: Mapped[StatusPrinter] = mapped_column(String(30), server_default=text(f"'{StatusPrinter.ONLINE}'"))
    
    collector_type: Mapped[CollectorType] = mapped_column(String(30), server_default=text(f"'{CollectorType.SNMP}'"))
    
    counter: Mapped[Optional[int]] = mapped_column(Integer, server_default=text("0"))
    
    printer_function: Mapped[PrinterFunction] = mapped_column(String(30), server_default=text(f"'{PrinterFunction.OPERACIONAL}'"))

    last_modify: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    active: Mapped[bool] = mapped_column(Boolean, server_default=text("1"), )
     
    info_additional: Mapped[str] = mapped_column(Text, nullable=True)

    # Relacionamentos
    native_branch: Mapped["Branch"] = relationship(
        "Branch", 
        foreign_keys=[branch_native_id],
        back_populates="native_printers"        
    )

    current_branch: Mapped["Branch"] = relationship(
        "Branch",
        foreign_keys=[branch_current_id],
        back_populates="current_printers"
    )
    
    current_network: Mapped["BranchNetwork"] = relationship( back_populates="printer")
    
    data_raw_counters: Mapped[list["RawCounter"]] = relationship(back_populates="printer")

    data_errors: Mapped[list["ErrorCounter"]] = relationship(back_populates="printer")

    daily_counters: Mapped[list["DailyCounter"]] = relationship(back_populates="printer")


    def __repr__(self) -> str:
        return f"Printer(num_serial='{self.num_serial}', model='{self.model}', status='{self.status}', ip='{self.ip}', counter='{self.counter}', function='{self.printer_function}', last_modify='{self.last_modify}')"

    # conflito de ip
    def clear_network_info(self):
        '''usado para limpar os dados da impressora antiga que estava no ip com conflito'''    
        self.ip = None
        self.status = StatusPrinter.DESCONHECIDO


    def _apply_updated_fields(self, scan_data):
        self.ip = scan_data.ip
        self.status = StatusPrinter.from_scan(scan_data)
        self.branch_current_id = scan_data.branch_id
        self.network_id = scan_data.network_id
        self.model = scan_data.model
        self.counter = int(scan_data.counter) if scan_data.counter is not None else 0
    
    
    def apply_position(self, position):
        self.position = position
    
    
    def apply_scan_data(self, scan_data):
        self._apply_updated_fields(scan_data)
        
        
    @classmethod
    def from_scan_data(cls, scan_data) -> Printer:
        printer = cls(
            num_serial=scan_data.num_serial,
            branch_native_id=scan_data.branch_id,
            connection_type=ConnectionType.IP,
            collector_type=scan_data.collector_type,
        )

        printer._apply_updated_fields(scan_data)

        return printer

