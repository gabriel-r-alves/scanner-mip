from monitoramento_impressoras_backend.database.models    import DailyCounter

from sqlalchemy     import select, and_, delete

from datetime       import date

class DailyCounterRepository():
    def __init__(self, session):
        self.session = session


    def get_all_counters(self) -> list[DailyCounter]:
        stmt = select(DailyCounter)
        return self.session.execute(stmt).scalars().all()
    
    
    def get_by_data(self, date: date) -> list[DailyCounter]:
        stmt = select(DailyCounter).where(DailyCounter.date == date)
        return self.session.execute(stmt).scalars().all()
    
    
    def get_by_date_range(self, init_date: date, end_date: date) -> list[DailyCounter]:
        stmt = select(DailyCounter).where(
            DailyCounter.date>=init_date,
            DailyCounter.date<=end_date
        )
        
        return self.session.execute(stmt).scalars().all()
    
    
    def delete_by_date(self, date: date):
        stmt = delete(DailyCounter).where(DailyCounter.date == date)
        self.session.execute(stmt)


    def save(self, daily_counter):
        self.session.add(daily_counter)
        
    
    def save_all(self, list_daily_counters):
        self.session.add_all(list_daily_counters)
    
    