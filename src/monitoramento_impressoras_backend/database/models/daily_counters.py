from __future__ import annotations

from enum import StrEnum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Index, ForeignKey, Date, UniqueConstraint, Boolean, text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class StatusCounter(StrEnum):
    SUCCESS = "success"
    COUNTER_AND_ERROR = "counter and error"
    VERIFY = "verify"
    NO_CHANGES = "no_changes"
    ERROR = "error"
    MULTIPLE_ERRORS = "multiple_errors"
    WITHOUT_OPERATION = "without_operation"


class DailyCounter(Base):
    __tablename__ = "daily_counters"
    __table_args__ = (
        UniqueConstraint("num_serial", "date", "branch_id", name="uq_daily_serial_branch_date"),
        Index("ix_serial_date", "num_serial", "date"),
        Index("ix_branch_date", "branch_id", "date"),
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    num_serial: Mapped[str] = mapped_column(String(100), ForeignKey("printers.num_serial"), nullable=False)
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id"), nullable=False)
    
    ip: Mapped[Optional[str]] = mapped_column(String(18), nullable=True)
    
    status_counter: Mapped[StatusCounter] = mapped_column(String(30), nullable=False)
    
    errors: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    ini_counter: Mapped[int] = mapped_column(Integer, nullable=False)

    ini_date: Mapped[datetime] = mapped_column(Date, nullable=False)

    end_counter: Mapped[int] = mapped_column(Integer, nullable=False)
    
    end_date: Mapped[datetime] = mapped_column(Date, nullable=False)

    date: Mapped[datetime] = mapped_column(
        Date,
        server_default=func.current_timestamp()
        , nullable=False
    )

    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))

    # Relacionamentos
    printer: Mapped["Printer"] = relationship(back_populates="daily_counters")

    branch: Mapped["Branch"] = relationship(back_populates="daily_counters")

    def __repr__(self) -> str:
        return (
            f"DailyCounter(num_serial='{self.num_serial}', branch='{self.branch_id}', "
            f"date='{self.date}', ini={self.ini_counter}, end={self.end_counter}, "
            f"status='{self.status_counter}', ip='{self.ip}')"
        )

    