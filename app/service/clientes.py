from fastapi import HTTPException
from sqlmodel import Session

from ..models.clientes import Cliente
from ..repository.clientes import ClienteRepository
from ..dto.create_client import CreateClientDTO
from .pipefy import PipefyService

pipefy_service = PipefyService()

class ClienteService:
    def __init__(self):
        self.repository = ClienteRepository()

    def create(self, session: Session, data: CreateClientDTO) -> Cliente:
        existe = self.repository.get_by_email(
            session=session,
            email=data.cliente_email
        )
        if existe is not None:
            raise HTTPException(
                status_code=409,
                detail="Já existe um cliente com este e-mail"
            )

        cliente = Cliente(
            nome=data.cliente_nome,
            email=data.cliente_email,
            tipo_solicitacao=data.tipo_solicitacao,
            valor_patrimonio=data.valor_patrimonio
        )

        pipefy_service.create_card(cliente=cliente)

        return self.repository.create(
            session=session,
            cliente=cliente
        )
