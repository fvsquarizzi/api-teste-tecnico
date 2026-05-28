from sqlmodel import Field, SQLModel

class Cliente(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(unique=True)
    tipo_solicitacao: str
    valor_patrimonio: float
    status: str = Field(default="Aguardando Análise")
    prioridade: str | None = Field(default=None)
