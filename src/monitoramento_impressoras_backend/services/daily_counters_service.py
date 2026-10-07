from collections    import defaultdict
from datetime       import date, datetime, timedelta

from monitoramento_impressoras_backend.database.models.daily_counters import DailyCounter, StatusCounter

from monitoramento_impressoras_backend.repositories   import PrinterRepository, RawCounterRepository, ErrorCounterRepository, DailyCounterRepository

from monitoramento_impressoras_backend.utils.loggin   import log_info, log_error


class DailyCountersService:
    def __init__(
        self,
        printer_repo,
        raw_counters_repo,
        errors_repo,
        daily_counters_repo
    ):
        self.printers_repository = printer_repo
        self.raw_counters_repository = raw_counters_repo
        self.errors_repository = errors_repo
        self.daily_counters_repository = daily_counters_repo
    
    
    def generate_daily_summary(self, target_date: date, force: bool = True):
        log_info(f"--- PROCESSANDO: {target_date} (Force: {force}) ---")

        try:
            # 1. VERIFICAÇÃO DE STATUS
            existing_records = self.daily_counters_repository.get_by_data(date=target_date)
            
            if existing_records:
                
                if any(r.is_closed for r in existing_records):
                    log_error(f"DIA BLOQUEADO: {target_date} já está fechado e faturado.")
                    return False
                
                # Se existe mas não foi forçado, pula para não gastar processamento
                if not force:
                    log_info(f"PULANDO: {target_date} já possui dados. Use force=True para atualizar.")
                    return True
                
                
                self.daily_counters_repository.delete_by_date(target_date)

            # 2. CARREGAMENTO DE DADOS
            printers = self.printers_repository.get_all_printers()
            raw_counters = self.raw_counters_repository.get_by_date(target_date)
            errors = self.errors_repository.get_by_date(target_date)
            
            entries_to_save = []

            if not raw_counters and not errors:
                entries_to_save = self._process_day_off(target_date=target_date, printers=printers)
            else:
                entries_to_save = self._process_sumary_daily(
                    target_date=target_date,
                    printers=printers,
                    raw_counters=raw_counters,
                    errors=errors
                )

            if entries_to_save:
                self.daily_counters_repository.save_all(entries_to_save)
                log_info(f"--- RESUMO FINALIZADO: {len(entries_to_save)} registros inseridos ---")
                return True

        except Exception as ex:
            log_error(f"ERRO CRÍTICO no processamento de {target_date}: {str(ex)}")
            return False
            
    
    def generate_summaries_date_range(self,ini_date, end_date, force=True):
        if ini_date is None and end_date is None:
            log_error("")
            return []
        
        delta = timedelta(days=1)
        current_date = ini_date
        while current_date <= end_date:
            self.generate_daily_summary(current_date, force)
            current_date += delta


    def _process_sumary_daily(self, target_date, printers, raw_counters, errors):
        log_info(f"Dados carregados: {len(printers)} impressoras, {len(raw_counters)} leituras, {len(errors)} erros.")

        # Agrupamento eficiente
        counters_by_sn = defaultdict(list)
        for c in raw_counters: counters_by_sn[c.num_serial].append(c)

        errors_by_sn = defaultdict(list)
        for e in errors: errors_by_sn[e.num_serial].append(e)

        # 3. PROCESSAMENTO INDIVIDUAL
        entries_to_save = []
        for printer in printers:
            sn = printer.num_serial
            printer_raw = counters_by_sn[sn]
            printer_err = errors_by_sn[sn]
            
            daily = None

            if printer_raw:
                daily = self._process_raw_counters_for_printer(
                    raw_counters=printer_raw,
                    target_date=target_date,
                    error_records=printer_err
                )
            
            elif printer_err:
                log_info(f"[{sn}] Apenas erros encontrados. Gerando registro de falha.")
                daily = self._process_errors_for_printer(
                    errors=printer_err, 
                    target_date=target_date
                )
            
            else:
                daily = DailyCounter(
                    num_serial=sn,
                    branch_id=printer.branch_current_id,
                    ip=printer.ip,
                    status_counter=StatusCounter.NO_CHANGES,
                    ini_counter=printer.counter,
                    ini_date=target_date,
                    end_counter=printer.counter,
                    end_date=target_date,
                    date=target_date
                )

            if daily:
                entries_to_save.append(daily)
            
        return entries_to_save


    def _process_day_off(self, target_date, printers):
        entries_to_save = []        
        
        for printer in printers:
            last_Counter = self.raw_counters_repository.get_last_counter_by_serial_date(
            serial=printer.num_serial,
            limit_date=target_date
            )
            
            counter = last_Counter.counter if last_Counter is not None else 0
        
            daily = DailyCounter(
                num_serial=printer.num_serial,
                branch_id=printer.branch_current_id,
                ip=printer.ip,
                status_counter=StatusCounter.WITHOUT_OPERATION,
                date=target_date,
                errors=None,
                ini_counter=counter,
                end_counter=counter,
                ini_date=target_date,
                end_date=target_date,
            )

            entries_to_save.append(daily)
        return entries_to_save


    def _process_raw_counters_for_printer(self, raw_counters, target_date, error_records=None):
        raw_counters.sort(key=lambda c: c.date_reading)
        sn = raw_counters[0].num_serial
        
        daily = DailyCounter(
            num_serial=sn,
            branch_id=raw_counters[0].branch_id,
            ip=raw_counters[0].ip,
            status_counter=StatusCounter.SUCCESS,
            ini_counter=raw_counters[0].counter,
            ini_date=raw_counters[0].date_reading,
            end_counter=raw_counters[-1].counter,
            end_date=raw_counters[-1].date_reading,
            date=target_date
        )

        if error_records:
            log_info(f"[{sn}] Leitura OK, mas com {len(error_records)} alertas técnicos.")
            daily = self._process_errors_for_printer(errors=error_records, target_date=target_date, daily=daily)

        else:
            log_info(f"[{sn}] Sucesso: {daily.ini_counter} -> {daily.end_counter} (Prod: {daily.end_counter - daily.ini_counter})")

        return daily


    def _process_errors_for_printer(self, errors, target_date, daily=None):
        # Normalização de nomes de erro para evitar conflitos no MariaDB
        unique_names = {
            str(e.named_error).lower().replace(" ", "_").split('.')[-1] 
            for e in errors if e.named_error
        }
        status_list = sorted(list(unique_names))
        errors_str = "; ".join(status_list)[:200]

        # Se já existe (veio de process_raw), apenas complementa
        if daily:
            daily.status_counter = StatusCounter.COUNTER_AND_ERROR if len(status_list) == 1 else StatusCounter.VERIFY
            daily.errors = errors_str
            return daily

        # Se é apenas erro puro
        first = errors[0]
        chosen_status = StatusCounter.MULTIPLE_ERRORS if len(status_list) > 1 else StatusCounter.ERROR
        
        # Tenta mapear o erro único para um status conhecido do Enum
        if len(status_list) == 1:
            try:
                chosen_status = StatusCounter(status_list[0])
            except ValueError:
                pass # Mantém VERIFY

        last_Counter = self.raw_counters_repository.get_last_counter_by_serial_date(
            serial=first.num_serial,
            limit_date=target_date
        )
        
        counter = last_Counter.counter if last_Counter is not None else 0
        
        return DailyCounter(
            num_serial=first.num_serial,
            branch_id=first.branch_id,
            ip=first.ip,
            status_counter=chosen_status,
            date=target_date,
            errors=errors_str,
            ini_counter=counter,
            end_counter=counter,
            ini_date=target_date,
            end_date=target_date,
        )

    