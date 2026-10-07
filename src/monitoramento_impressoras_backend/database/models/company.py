from __future__ import annotations

from typing import Optional

from sqlalchemy     import String, Text, Boolean, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class Company(Base):
    __tablename__ = 'companies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    cnpj: Mapped[Optional[str]] = mapped_column(String(14))
    config_json: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, server_default=text("1"))

    branches: Mapped[list["Branch"]] = relationship(back_populates="company")

    
    def __repr__ (self):
        return f"Company(id={self.id}, name='{self.name}', active={self.active})"