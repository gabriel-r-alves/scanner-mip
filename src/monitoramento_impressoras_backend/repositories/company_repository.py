from sqlalchemy import select
from monitoramento_impressoras_backend.database.session import SessionLocal
from monitoramento_impressoras_backend.database.models import Company


class CompanyRepository:
    def __init__(self, session):
        self.session = session
        

    def get_by_id(self, id) -> Company | None:
        stmt = select(Company).where(Company.id == id)
        return self.session.execute(stmt).scalar_one_or_none()


    def get_all_branches(self) -> list[Company]:
        stmt = select(Company)
        return self.session.execute(stmt).scalars().all()


    def delete_by_id(self, id) -> bool:
        stmt = select(Company).where(Company.id == id)
        company = self.session.scalar_one_or_none(stmt)
        if not company:
            return False
        self.session.delete(company)
        return True        

