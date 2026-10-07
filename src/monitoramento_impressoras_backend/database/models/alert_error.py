from __future__ import annotations

from datetime import datetime
import enum

from typing     import Optional

from sqlalchemy     import Integer, String, ForeignKey, Index, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types   import Enum as SQLEnum

from monitoramento_impressoras_backend.database.base              import Base


class AlertError(Base):
    __tablename__ = "alerts_errors"

    


