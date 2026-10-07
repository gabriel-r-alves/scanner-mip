import pandas as pd

from datetime import date

from collections import defaultdict

from monitoramento_impressoras_backend.repositories import DailyCounterRepository


class ReportService:
    def __init__(self, daily_counters_repository: DailyCounterRepository):
        self._daily_counters_repo = daily_counters_repository
    
    @staticmethod
    def _group_readings_by_branch(counters_daily):
        counters_by_branch = defaultdict(list)
        
        for counter in counters_daily:
            counters_by_branch[counter.branch_id].append(counter)
        
        return counters_by_branch
        
    
    def generate_daily_summary(self, date):
        counters_daily = self._daily_counters_repo.get_by_data(date)
        counters_by_branch = self._group_readings_by_branch(counters_daily)
        
        for branch in counters_by_branch:
            print('\n',branch)
            counters_list = counters_by_branch[branch]
            
            for counter in counters_list:
                #print(counter)
                print(f'     {counter.num_serial} - {counter.ip} - {counter.status_counter} - {counter.errors} - {counter.ini_counter} - {counter.end_counter} - {counter.date}')
                
                data = [
                    {
                        'num_serial': counter.num_serial,
                        'filial': counter.branch_id,
                        'ip': counter.ip,
                        'status_counter': counter.status_counter,
                        'errors': counter.errors,
                        'ini_counter': counter.ini_counter,
                        'end_counter': counter.end_counter,
                        'date_reading': counter.date
                    }
                    for counter in counters_daily
                ]
                df = pd.DataFrame(data)
                df = df.sort_values(by='branch', ascending=False)
                df = df.sort_values(by='ip', ascending=False)
                
                df.to_excel(f'src/monitoramento_impressoras_backend/data_exported/{date.replace('/','_')}_summary.xlsx', index=False)
        
        print(counters_by_branch.keys())
        
  
    def generate_summary_by_date_range(self, init_date: date, end_date:date):
        counters_daily = self._daily_counters_repo.get_by_date_range(init_date=init_date, end_date=end_date)
        counters_by_branch = self._group_readings_by_branch(counters_daily)
        
        for branch in counters_by_branch:
            print('\n',branch)
            counters_list = counters_by_branch[branch]
            
            for counter in counters_list:
                print(f'     {counter.num_serial} - {counter.ip} - {counter.status_counter} - {counter.errors} - {counter.ini_counter} - {counter.end_counter} - {counter.date}')
                
                data = [
                    {
                        'num_serial': counter.num_serial,
                        'filial': counter.branch_id,
                        'ip': counter.ip,
                        'status_counter': counter.status_counter,
                        'errors': counter.errors,
                        'ini_counter': counter.ini_counter,
                        'end_counter': counter.end_counter,
                        'date_reading': counter.date
                    }
                    for counter in counters_daily
                ]
                df = pd.DataFrame(data)
                df = df.sort_values(by='filial', ascending=False)
                
                df.to_excel(f'src/monitoramento_impressoras_backend/data_exported/{str(init_date).replace('/','_')}_{str(end_date).replace('/','_')}_summary.xlsx', index=False)
        
        
    def generate_month_summary(self, init_date: date, end_date:date):
        return
        counters_daily = self._daily_counters_repo.get_by_date_range(init_date=init_date, end_date=end_date)
    