from __future__ import annotations

from datetime import datetime

from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, Index, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

class RawCounter(Base):
    __tablename__ = "data_raw_counters"

    __table_args__ = (
        Index("ix_raw_serial_date", "num_serial", "date_reading"),
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    num_serial: Mapped[str] = mapped_column(String(100), ForeignKey("printers.num_serial"), nullable=False)

    ip: Mapped[str] = mapped_column(String(18), nullable=False)
    
    position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id"), nullable=False)

    counter: Mapped[int]= mapped_column(Integer, nullable=False)

    date_reading: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        default=func.current_timestamp(),
        nullable=False
    )

    # Relacionamentos
    branch: Mapped["Branch"] = relationship(back_populates="data_raw_counters")

    printer: Mapped["Printer"] = relationship(back_populates="data_raw_counters")


    def __repr__(self) -> str:
        return (
            f"RawCounter(num_serial='{self.num_serial}', ip='{self.ip}', branch='{self.branch_id}', "
            f"counter='{self.counter}', date='{self.date_reading}')"
        )

