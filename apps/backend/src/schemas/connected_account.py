from datetime import datetime
from pydantic import BaseModel


class ConnectedAccountOut(BaseModel):
    provider: str
    provider_email: str | None
    display_name: str | None
    avatar_url: str | None
    scopes: list[str]
    connected_at: datetime | None
    last_used_at: datetime | None
    has_gmail: bool
    has_calendar: bool

    model_config = {'from_attributes': True}


class ConnectUrlResponse(BaseModel):
    url: str
