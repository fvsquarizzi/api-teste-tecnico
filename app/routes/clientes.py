from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..dto.create_client import CreateClientDTO
from ..infra.db import get_session
from ..service.clientes import ClienteService

router = APIRouter()
service = ClienteService()

@router.post("")
def clientes(data: CreateClientDTO, session: Session = Depends(get_session)):
    cliente = service.create(
        session=session,
        data=data
    )

    return cliente
