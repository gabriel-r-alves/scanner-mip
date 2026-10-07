from sqlalchemy import select, func, and_

from monitoramento_impressoras_backend.database.models.data_error_counters import ErrorCounter

class ErrorCounterRepository:
    def __init__(self, session):
        self.session = session
    

    def get_by_date(self, date) -> list[ErrorCounter]:
        stmt = (
            select(ErrorCounter)
            .where(func.date(ErrorCounter.date_error) == date)
        )
        
        return self.session.execute(stmt).scalars().all()
    
    
    def get_by_date_range(self, start_date: str | None = None, end_date: str | None = None) -> list[ErrorCounter]:

        if start_date is None and end_date is None:
            return []
        
        elif start_date is None:
            stmt = select(ErrorCounter).where(ErrorCounter.date_error <= end_date)

        elif end_date is None:
            stmt = select(ErrorCounter).where(ErrorCounter.date_error >= start_date)
            
        else:
            stmt = select(ErrorCounter).where(
                and_(
                    ErrorCounter.date_error >= start_date,
                    ErrorCounter.date_error <= end_date
                )
            )
            
        return self.session.execute(stmt).scalars().all()


    def save(self, error_counter: ErrorCounter):
        self.session.add(error_counter)


    def save_all(self, list_errors: list[ErrorCounter]):
        self.session.add_all(list_errors)
