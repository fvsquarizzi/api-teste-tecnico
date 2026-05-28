from sqlmodel import SQLModel
from pydantic import EmailStr

class CreateClientDTO(SQLModel):
    cliente_nome: str
    cliente_email: EmailStr
    tipo_solicitacao: str
    valor_patrimonio: float
