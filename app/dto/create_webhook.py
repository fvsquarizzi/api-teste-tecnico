from ..dto.webhook_event import WebhookPayloadDTO

class CreateWebhookDTO(WebhookPayloadDTO):
    event_id: str
