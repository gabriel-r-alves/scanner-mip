from __future__ import annotations

import ipaddress

from typing import Optional

from sqlalchemy                 import ForeignKey, String, Integer, Boolean, text
from sqlalchemy.orm             import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql  import BINARY

from monitoramento_impressoras_backend.domain.enums import CollectorType, IpVersion

from ..base import Base


class BranchNetwork(Base):
    __tablename__ = "branch_networks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id"))

    ip_version: Mapped[IpVersion] = mapped_column(String(10), nullable=False, server_default=text(f"'{IpVersion.IPV4}'"))

    description: Mapped[Optional[str]] = mapped_column(String(100))
    collector_type: Mapped[CollectorType] = mapped_column(String(30), server_default=text(f"'{CollectorType.SNMP}'"))
    priority: Mapped[Optional[int]] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))

    # BINARY(16) é excelente para buscas por range (BETWEEN)
    ip_start: Mapped[bytes] = mapped_column(BINARY(16), nullable=False, index=True)
    ip_end: Mapped[bytes] = mapped_column(BINARY(16), nullable=False, index=True)

    def _bytes_to_ip(self, b_data: bytes) -> str:
        """Converte BINARY(16) para string de IP respeitando a versão."""

        if not b_data:
            return ""

        version = (
            self.ip_version.value
            if isinstance(self.ip_version, IpVersion)
            else str(self.ip_version)
        )

        if version == IpVersion.IPV4.value:
            return str(ipaddress.IPv4Address(b_data[:4]))

        if version == IpVersion.IPV6.value:
            return str(ipaddress.IPv6Address(b_data[:16]))

        raise ValueError(
            f"Versão IP inválida: {self.ip_version!r}"
        )


    @property
    def start_readable(self) -> str:
        return self._bytes_to_ip(self.ip_start)


    @start_readable.setter
    def start_readable(self, ip_str: str):
        addr = ipaddress.ip_address(ip_str)
        self.ip_start = addr.packed
        # Atualiza a versão automaticamente conforme o input
        self.ip_version = IpVersion.IPV4 if addr.version == 4 else IpVersion.IPV6


    @property
    def end_readable(self) -> str:
        return self._bytes_to_ip(self.ip_end)


    @end_readable.setter
    def end_readable(self, ip_str: str):
        addr = ipaddress.ip_address(ip_str)

        if self.ip_version:
            current_version = (
                self.ip_version.value
                if isinstance(self.ip_version, IpVersion)
                else self.ip_version
            )

            if addr.version == 4 and current_version != IpVersion.IPV4.value:
                raise ValueError(
                    "ip_end é IPv4, mas ip_version está configurado como IPv6"
                )

            if addr.version == 6 and current_version != IpVersion.IPV6.value:
                raise ValueError(
                    "ip_end é IPv6, mas ip_version está configurado como IPv4"
                )

        self.ip_end = addr.packed

    # Relacionamentos
    branch: Mapped["Branch"] = relationship(back_populates="branch_networks")
    printer: Mapped["Printer"] = relationship(back_populates="current_network")

    def __repr__(self):
        return (f"<BranchNetwork(id={self.id}, range={self.start_readable}-{self.end_readable}, "
                f"active={self.active})>")
        
        