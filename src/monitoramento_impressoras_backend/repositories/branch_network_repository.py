from monitoramento_impressoras_backend.database.models import BranchNetwork
from monitoramento_impressoras_backend.database.models.branch_network import IpVersion
from monitoramento_impressoras_backend.database.session import SessionLocal
from monitoramento_impressoras_backend.utils.loggin import log_error


from sqlalchemy import select


class BranchNetworkRepository:
    def __init__(self, session):
        self.session = session
        

    def get_all_networks(self) -> list[BranchNetwork]:
        stmt = select(BranchNetwork)
        return self.session.execute(stmt).scalars().all()


    def get_by_id(self, id) -> BranchNetwork | None:
        stmt = select(BranchNetwork).where(BranchNetwork.id == id)
        return self.session.execute(stmt).scalar_one_or_none()


    def get_by_filial(self, branch_id) -> list[BranchNetwork]:
        stmt = select(BranchNetwork).where(BranchNetwork.branch_id == branch_id)
        return self.session.scalars(stmt).all()
    
    
