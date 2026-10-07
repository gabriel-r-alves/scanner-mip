from typing import Tuple, Optional, List

from .printer_sync_conext import PrinterSyncContext

import inspect as py_inspect

from monitoramento_impressoras_backend.utils.loggin import log_error, log_info
from monitoramento_impressoras_backend.database.models import RawCounter, Printer, LogPrinter, ErrorCounter
from monitoramento_impressoras_backend.database.models.log_printers import TypeAction

from sqlalchemy import inspect as sa_inspect


class PostSync:
    def __init__(self,
                 counters_repository,
                 errors_repository,
                 logs_repository
                 ) -> None:
        self.counters_repo = counters_repository
        self.errors_repo = errors_repository
        self.logs_repo = logs_repository
        
    
    
    def detect_and_persist_changes(self, context: PrinterSyncContext) -> Tuple[str, int]:
        """
        Detecta mudanças, persiste logs/contadores.
        Retorna: (action_label, stats_increment)
        """
        
        if context.printer is None:
            log_error(f"Erro no Printer do SyncContext: {context.printer}")
            raise
            
        self._detect_changes(context)
        
        action_type, action_label = self._classify_action(context.is_new, context.detected_changes)

        # Log das mudanças
        log_info(f"[SINCRONIZAÇÃO IMPRESSORA] {action_label} - S/N: {context.printer.num_serial}")
        
        for field, (old, new) in context.detected_changes.items():
            log_info(f"\tCampo: {field} OLD: {old} - NEW: {new}")

        # Persister apenas se houver mudanças reais
        if action_type:
            self._persist_changes(context.printer, context.detected_changes, action_type)

        return action_label, 1 if action_type else 0


    def _detect_changes(self, context: PrinterSyncContext) -> None:
        """Extrai mudanças reais do printer"""
        state = sa_inspect(context.printer)
        changes = {}

        for attr in state.attrs:
            history = attr.history
            if history.has_changes():
                old = history.deleted[0] if history.deleted else None
                new = history.added[0] if history.added else None

                if old != new:
                    changes[attr.key] = (old, new)

        context.detected_changes = changes


    @staticmethod
    def _classify_action(is_new: bool, changes: dict) -> Tuple[Optional[TypeAction], str]:
        """Classifica a ação (INSERT, UPDATE, SEM_ALTERAÇÕES)"""
        if is_new:
            return TypeAction.INSERT, "INSERIDA"
        
        if changes:
            return TypeAction.UPDATE, "ATUALIZADA"
        
        return None, "SEM_ALTERAÇÕES"


    def _persist_changes(
        self,
        printer: Printer,
        changes: dict,
        type_action: TypeAction
    ) -> None:
        """Persiste logs de auditoria e contadores"""
        # Extrair e salvar contador se mudou
        if "counter" in changes:
            old, new = changes.pop("counter")
            self._save_counter(printer, new)

        # Salvar logs de auditoria para mudanças restantes
        if changes:
            logs = self._generate_audit_logs(printer, changes, type_action)
            self.logs_repo.save_all(logs)


    def _save_counter(self, printer: Printer, counter_value: int) -> None:
        """Salva novo valor de contador"""
        raw_counter = RawCounter(
            num_serial=printer.num_serial,
            ip=printer.ip,
            branch_id=printer.branch_current_id,
            counter=counter_value
        )
        
        self.counters_repo.save(raw_counter)
        log_info(f"[✓] Contador registrado: {printer.num_serial} = {counter_value}")


    @staticmethod
    def _generate_audit_logs(
        printer: Printer,
        changes: dict,
        type_action: TypeAction
    ) -> List[LogPrinter]:
        """Gera logs de auditoria para mudanças"""
        stack = py_inspect.stack()
        call_path = " -> ".join([frame.function for frame in stack])

        logs = []
        for field, (old, new) in changes.items():
            logs.append(
                LogPrinter(
                    num_serial=printer.num_serial,
                    type_action=type_action,
                    origin_action=call_path,
                    field_name=field,
                    old_value=old,
                    new_value=new
                )
            )

        return logs


    def save_error(self, context):
        """
        Gera o ErrorCounter e persiste no db
        """
        printer = context.printer
        scan_data = context.scan_data
        
        error = ErrorCounter(
            num_serial=printer.num_serial,
            branch_id=printer.branch_current_id or context.snmp.branch_id,
            ip=scan_data.ip,
            status=scan_data.connection,
            named_error=scan_data.status
        )
        
        self.errors_repo.save(error)
        log_info(f"[✓] Erro registrado: {printer.num_serial} {printer.ip} {error}")