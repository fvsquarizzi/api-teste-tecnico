from ..repository.webhook import WebhookRepository
from ..dto.webhook_event import WebhookPayloadDTO
from ..models.webhook import Webhook
from ..repository.clientes import ClienteRepository
from ..service.pipefy import PipefyService

service = PipefyService()

from sqlmodel import Session
from fastapi import HTTPException
class WebhookService:
    def __init__(self):
        self.repository = WebhookRepository()
        self.cliente_repository = ClienteRepository()

    def process_webhook(self, session: Session, data: WebhookPayloadDTO):
        event_exists = self.repository.get_by_event_id(session=session, event_id=data.event_id)

        if event_exists is not None:
            raise HTTPException(
                status_code=409,
                detail="Webhook já foi processado"
            )

        webhook = Webhook(event_id = data.event_id)

        cliente = self.cliente_repository.get_by_email(session=session, email=data.cliente_email)

        if cliente is None:
            raise HTTPException(
                status_code=404,
                detail="Cliente não encontrado com o email"
            )

        if cliente.valor_patrimonio >= 200000:
            cliente.prioridade = "prioridade_alta"
        else:
            cliente.prioridade = "prioridade_normal"

        cliente.status = "Processado"

        self.cliente_repository.update(session=session, cliente=cliente)

        self.repository.create(session=session, webhook=webhook)

        mutation = service.update_card_field(cliente=cliente, payload=data)

        print("=== SIMULANDO ENVIO PIPEFY ===")
        print(mutation)

        return {
            "success": True,
            "message": "Webhook processado"
        }
