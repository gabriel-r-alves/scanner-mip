from __future__ import annotations

from datetime import datetime
from typing import Optional
from enum import StrEnum

from sqlalchemy import String, Integer, DateTime, Text, Index, text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class TypeAction(StrEnum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    NO_CHANGES = "no_changes"


class NamedEvent(StrEnum):
    PRINTER_DISCOVERED = "printer_discovered"
    ERROR = "error"
    #SNMP_TIMEOUT = "snmp_timeout"
    #IP_CLONFLICT = "ip_conflict"
    STATUS_CHANGE = "status_change"
    IP_CHANGE = "ip_change"
    BRANCH_CHANGE = "branch_change"
    NETWORK_CHANGE = "network_change"


class LogPrinter(Base):
    __tablename__ = "log_printers"

    __table_args__ = (
        Index("ix_log_serial", "num_serial"),
        #Index("ix_log_event", "named_event"),
        Index("ix_log_date", "action_date")
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    num_serial: Mapped[str] = mapped_column(String(100))
    
    type_action: Mapped[TypeAction] = mapped_column(String(30))

    origin_action: Mapped[str] = mapped_column(Text)
    
    named_event: Mapped[Optional[NamedEvent]] = mapped_column(String(30), nullable=True)
    
    field_name: Mapped[str] = mapped_column(String(30))
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    action_date: Mapped[datetime] = mapped_column( DateTime, default=func.now())
    user_action: Mapped[str] = mapped_column(String(100), nullable=False, server_default=func.current_user())
    detail: Mapped[Optional[str]] = mapped_column(Text)
