from __future__ import annotations

from typing import Optional
from enum   import StrEnum

from sqlalchemy     import ForeignKey, String, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

class TypeBranch(StrEnum):
    MATRIZ = "matriz"
    FILIAL = "filial"
    

class Branch(Base):
    __tablename__ = 'branches'

    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"))
    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    
    type_branch: Mapped[TypeBranch] = mapped_column(String(10), nullable=False, server_default=text(f"'{TypeBranch.FILIAL}'"))
    
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[Optional[str]] = mapped_column(String(250))
    
    # Relacionamentos
    company: Mapped["Company"] = relationship(back_populates="branches")

    native_printers: Mapped[list["Printer"]] = relationship(
        "Printer",
        foreign_keys="Printer.branch_native_id",
        back_populates="native_branch"
    )

    current_printers: Mapped[list["Printer"]] = relationship(
        "Printer",
        foreign_keys="Printer.branch_current_id",
        back_populates="current_branch"
    )

    branch_networks: Mapped[list["BranchNetwork"]] = relationship(back_populates="branch")

    data_raw_counters: Mapped[list["RawCounter"]] = relationship(back_populates="branch")

    data_errors: Mapped[list["ErrorCounter"]] = relationship(back_populates="branch")

    daily_counters: Mapped[list["DailyCounter"]] = relationship(back_populates="branch")


    def __repr__(self) -> str:
        return f"Branch(id={self.id}, name='{self.name}', company_id={self.company_id})"