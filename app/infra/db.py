import os

from typing import Generator
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel,create_engine, Session
from ..models.clientes import Cliente
from ..models.webhook import Webhook

load_dotenv()

PG_USER = os.getenv("POSTGRES_USER")
PG_PWD = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = f"postgresql://{PG_USER}:{PG_PWD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)

def init() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()
