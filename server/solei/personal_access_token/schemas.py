from datetime import datetime

from pydantic import UUID4

from solei.auth.scope import Scope
from solei.kit.schemas import Schema, TimestampedSchema


class PersonalAccessToken(TimestampedSchema):
    id: UUID4
    scopes: list[Scope]
    expires_at: datetime | None
    comment: str
    last_used_at: datetime | None


class PersonalAccessTokenCreateResponse(Schema):
    personal_access_token: PersonalAccessToken
    token: str
