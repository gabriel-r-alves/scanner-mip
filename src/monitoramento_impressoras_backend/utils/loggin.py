import logging
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'monitoramento.log')

class ImmediateFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()


logger = logging.getLogger()
logger.setLevel(logging.INFO)


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


file_handler = ImmediateFileHandler(LOG_FILE, mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def log_info(msg):
    logging.info(msg)

def log_error(msg):
    logging.error(msg)

def log_debug(msg):
    logging.debug(msg)