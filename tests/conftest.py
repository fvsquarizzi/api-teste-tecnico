"""
Fixtures compartilhadas para os testes automatizados.

OBJETIVO GERAL:
    Permitir que os testes rodem sem precisar de um banco PostgreSQL real.
    Em vez disso, usa SQLite em memória.

COMO FUNCIONA (visão geral):
    1) Cria um engine SQLAlchemy apontando para "sqlite:///:memory:".
    2) Cria todas as tabelas nesse banco em memória.
    3) Substitui a dependência get_session do FastAPI por uma versão
       que devolve uma Session ligada a esse engine de teste.
       Isso é feito via app.dependency_overrides[], que é o mecanismo
       oficial do FastAPI para trocar dependências em testes.
    4) Entrega um TestClienta já configurado para os testes.

DETALHE IMPORTANTE (StaticPool):
    SQLite em memória cria um banco diferente para cada conexão por padrão.
    Como o FastAPI/SQLAlchemy podem abrir mais de uma conexão durante uma
    requisição, força todas  as conexões a usarem a mesma
    instância de banco. Para isso é usado poolclass=StaticPool e
    check_same_thread=False.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.infra.db import get_session


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(engine):
    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
