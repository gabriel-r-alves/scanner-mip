from ..base import Base

from typing import Optional

from sqlalchemy     import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Position(Base):
    __tablename__ = 'positions'
    
    ip: Mapped[str] = mapped_column(String(18), primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    
    