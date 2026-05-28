from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..dto.webhook_event import WebhookPayloadDTO
from ..infra.db import get_session
from ..service.webhook import WebhookService

router = APIRouter()
service = WebhookService()

@router.post("/card-updated")
def webhook_card_updated(data: WebhookPayloadDTO, session: Session = Depends(get_session)):
    return service.process_webhook(session=session, data=data)
