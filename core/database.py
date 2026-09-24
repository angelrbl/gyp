import contextlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from core.config import DATABASE_URL

engine_kwargs = {} if "postgresql" in DATABASE_URL else {"connect_args": {"check_same_thread": False}}

engine = create_engine(DATABASE_URL, echo=False, **engine_kwargs)

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