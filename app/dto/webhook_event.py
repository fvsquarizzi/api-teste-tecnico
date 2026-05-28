from sqlmodel import SQLModel, Field
from pydantic import EmailStr

from datetime import datetime, UTC

class WebhookPayloadDTO(SQLModel):
    event_id: str
    card_id: str
    cliente_email: EmailStr
    timestamp: datetime
