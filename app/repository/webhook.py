from sqlmodel import Session, select
from ..models.webhook import Webhook

class WebhookRepository:
    def create(self, session: Session, webhook: Webhook) -> Webhook:
        session.add(webhook)
        session.commit()
        session.refresh(webhook)
        return webhook

    def get_by_event_id(self, session: Session, event_id: str) -> Webhook | None:
        statement = select(Webhook).where(
            Webhook.event_id == event_id
        )

        return session.exec(statement).first()
