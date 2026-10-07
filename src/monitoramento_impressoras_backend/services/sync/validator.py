from dataclasses import dataclass
from typing import Optional

from monitoramento_impressoras_backend.domain.enums import CollectorType, ConnectionStatus
from monitoramento_impressoras_backend.domain.dtos import ScanData, PrinterData
from .printer_sync_conext import PrinterSyncContext



@dataclass
class ValidResult:
    valid: bool
    error: str | None = None


class SyncValidator:
    def validate_network_scan_response(self, sync_data: ScanData) -> ValidResult:
        """Valida estrutura básica da resposta SNMP"""
        validations = [
        (isinstance(sync_data.connection, ConnectionStatus), "Conexão não definida"),
        (sync_data.ip is not None, "IP não fornecido"),
        (sync_data.branch_id is not None, "Id da filial não fornecido"),
        (sync_data.network_id is not None, "Id da rede não fornecido")
    ]

        for valid, error in validations:
            if not valid:
                return ValidResult(valid=False, error=error)

        return ValidResult(valid=True)


    def validate_scan_data_syncable(self, context: PrinterSyncContext) -> ValidResult:
        """Valida se a resposta é sincronizável (pré-sync)"""
        scan_data: ScanData = context.scan_data
        printer_data = scan_data.printer_data
        printer_by_ip = context.printer_by_ip
        printer_by_serial = context.printer_by_serial
        
        # Sem serial E IP não cadastrado = ignorar
        if (printer_data is None or printer_data.num_serial is None) and printer_by_ip is None:
            return ValidResult(False, f"Sincronização ignorada: Sem serial ou dados de coleta da impressora e IP {scan_data.ip} não cadastrado")
        
        if printer_by_serial is not None and printer_by_serial.collector_type == CollectorType.MANUAL:
            return ValidResult(
                False,
                f"Sincronização ignorada: impressora {printer_by_serial.num_serial} possui coleta manual."
            )
        
        if printer_by_ip is not None and printer_by_ip.collector_type == CollectorType.MANUAL:
            return ValidResult(
                False,
                f"Sincronização ignorada: IP {scan_data.ip} pertence à impressora {printer_by_ip.num_serial}, cadastrada como coleta manual."
            )
        
        return ValidResult(True)
    
    