from sqlmodel import Field, SQLModel
from datetime import datetime, UTC

class Webhook(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    event_id: str
    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
