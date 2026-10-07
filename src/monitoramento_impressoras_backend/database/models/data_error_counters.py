from __future__ import annotations

from datetime import datetime

from typing     import Optional

from sqlalchemy     import Integer, String, ForeignKey, Index, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class ErrorCounter(Base):
    __tablename__ = "data_error_counters"

    __table_args__ = (
        UniqueConstraint("num_serial", "branch_id", "date_error",
                         name="uq_error_serial_branch_date"),
        Index("ix_error_serial_date", "num_serial", "date_error"),
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    num_serial: Mapped[str] = mapped_column(String(100), ForeignKey("printers.num_serial"), nullable=False)

    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id"), nullable=False)

    ip: Mapped[str] = mapped_column(String(18), nullable=True)
    
    position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    named_error: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    date_error: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        default=func.current_timestamp(),
        nullable=False
    )

    # Relacionamentos
    branch: Mapped["Branch"] = relationship(back_populates="data_errors")

    printer: Mapped["Printer"] = relationship(back_populates="data_errors")


    def __repr__(self):
        return (
            f"Error(num_serial='{self.num_serial}', ip='{self.ip}', status='{self.status}', "
            f"branch='{self.branch_id}', error='{self.named_error}', date='{self.date_error}')"
        )
    
