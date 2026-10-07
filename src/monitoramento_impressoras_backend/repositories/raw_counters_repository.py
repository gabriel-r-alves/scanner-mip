from sqlalchemy.sql import select
from sqlalchemy import and_, func

from datetime import date

from monitoramento_impressoras_backend.database.models.data_raw_counters  import RawCounter


class RawCounterRepository:
    def __init__(self, session):
        self.session = session


    def get_by_num_serial(self, num_serial: str) -> list[RawCounter]:
        stmt = select(RawCounter).where(RawCounter.num_serial == num_serial)
        return self.session.execute(stmt).scalars().all()


    def get_by_branch_id(self, branch_id: int) -> list[RawCounter]:
        stmt = select(RawCounter).where(RawCounter.branch_id == branch_id)
        return self.session.execute(stmt).scalars().all()
    
    
    def get_all_counters(self) -> list[RawCounter]:
        stmt = select(RawCounter)
        return self.session.execute(stmt).scalars().all()


    def get_by_date(self, date) -> list[RawCounter]:
        stmt = select(RawCounter).where(func.date(RawCounter.date_reading) == date)
        return self.session.execute(stmt).scalars().all()
    

    def get_by_date_range(self, start_date: str | None = None, end_date: str | None = None) -> list[RawCounter]:

        if start_date is None and end_date is None:
            return []
        
        elif start_date is None:
            stmt = select(RawCounter).where(RawCounter.date_reading <= end_date)

        elif end_date is None:
            stmt = select(RawCounter).where(RawCounter.date_reading >= start_date)
            
        else:
            stmt = select(RawCounter).where(
                and_(
                    RawCounter.date_reading >= start_date,
                    RawCounter.date_reading <= end_date
                )
            )
        return self.session.execute(stmt).scalars().all()
    
    
    def get_last_counter_by_serial_date(self, serial, limit_date) -> RawCounter | None:
        stmt = (
            select(RawCounter)
            .where(RawCounter.num_serial == serial, RawCounter.date_reading <= limit_date)
            .order_by(RawCounter.date_reading.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    
    def save(self, counter):
        self.session.add(counter)
        
        
    def save_all(self, counter):
        self.session.add_all(counter)