from monitoramento_impressoras_backend.database.models import Printer

from sqlalchemy import select


class PrinterRepository:
    def __init__(self, session):
        self.session = session
    

    def get_all_printers(self) -> list[Printer]:
        stmt = select(Printer)
        return self.session.execute(stmt).scalars().all()
    
    
    def get_by_serial(self, num_serial) -> Printer | None:
        stmt = select(Printer).where(Printer.num_serial == num_serial)
        return self.session.execute(stmt).scalar_one_or_none()

    
    def get_by_ip(self, ip) -> Printer | None:
        stmt = select(Printer).where(Printer.ip==ip)        
        return self.session.execute(stmt).scalar_one_or_none()
    

    def delete_by_serial(self, num_serial):
        stmt = select(Printer).where(Printer.num_serial == num_serial)
        printer = self.session.scalar_one_or_none(stmt)
        if not printer:
            return False
        self.session.delete(printer)
        return True


    def save(self, printer):
        self.session.add(printer)
    
    
    def save_all(self, list_printers):
        self.session.add_all(list_printers)

