from monitoramento_impressoras_backend.database.models import Branch
from monitoramento_impressoras_backend.database.session import SessionLocal
from sqlalchemy import select


class BranchRepository:
    def __init__(self, session):
        self.session = session


    def get_by_id(self, id) -> Branch | None:
        stmt = select(Branch).where(Branch.id == id)
        return self.session.execute(stmt).scalar_one_or_none()


    def get_all_branches(self) -> list[Branch]:
        stmt = select(Branch)
        return self.session.execute(stmt).scalars().all()


    def delete_by_id(self, id):
        stmt = select(Branch).where(Branch.id == id)
        branch = self.session.scalar_one_or_none(stmt)
        if not branch:
            return False
        self.session.delete(branch)
        return True   

