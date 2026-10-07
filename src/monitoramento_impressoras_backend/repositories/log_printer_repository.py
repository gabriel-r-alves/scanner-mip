
class LogChangePrinterRepository:
    def __init__(self, session) -> None:
        self.session = session
    
    def save(self, log_change):
        self.session.add(log_change)
        
    
    def save_all(self, list_logs):
        self.session.add_all(list_logs)