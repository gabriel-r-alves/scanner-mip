from monitoramento_impressoras_backend.database.models import Position

from sqlalchemy import select

class PositionRepository:
    def __init__(self, session):
        self.session = session
        
    def get_all_positions(self):
        stmt = select(Position)
        return self.session.execute(stmt).scalars().all()
            
            
    def get_by_ip(self, ip: str):
        stmt = select(Position).where(Position.ip == ip)
        return self.session.execute(stmt).scalar_one_or_none()
    

    def save(self, position: Position):
        self.session.add(position)
        
    def save_all(self, position: Position):
        self.session.add_all(position)
        
    