from contextlib import contextmanager

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker

from monitoramento_impressoras_backend.settings import settings


engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

@contextmanager
def get_session():
    with SessionLocal() as session:
        yield session