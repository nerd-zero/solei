from datetime import datetime
from uuid import UUID

from sqlalchemy import CHAR, TIMESTAMP, ForeignKey, Text, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from solei.auth.scope import Scope
from solei.config import settings
from solei.kit.db.models.base import RecordModel
from solei.kit.extensions.sqlalchemy import StringEnum
from solei.kit.utils import utc_now
from solei.models.user import User


def get_expires_at() -> datetime:
    return utc_now() + settings.USER_SESSION_TTL


class UserSession(RecordModel):
    __tablename__ = "user_sessions"

    token: Mapped[str] = mapped_column(CHAR(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, index=True, default=get_expires_at
    )
    user_agent: Mapped[str] = mapped_column(Text, nullable=False)
    scopes: Mapped[list[Scope]] = mapped_column(
        ARRAY(StringEnum(Scope)), nullable=False, default=list
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="cascade"), nullable=False
    )

    @declared_attr
    def user(cls) -> Mapped[User]:
        return relationship(User, lazy="joined")
