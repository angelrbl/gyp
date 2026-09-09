import contextlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

@contextlib.contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def init_db():
    Base.metadata.create_all(bind=engine)