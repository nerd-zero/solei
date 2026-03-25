import structlog
from sqlalchemy import select

from solei.config import settings
from solei.enums import TokenType
from solei.kit.crypto import get_token_hash
from solei.kit.services import ResourceServiceReader
from solei.logging import Logger
from solei.models import OAuth2AuthorizationCode
from solei.postgres import AsyncSession

log: Logger = structlog.get_logger()


class OAuth2AuthorizationCodeService(ResourceServiceReader[OAuth2AuthorizationCode]):
    async def revoke_leaked(
        self,
        session: AsyncSession,
        token: str,
        token_type: TokenType,
        *,
        notifier: str,
        url: str | None = None,
    ) -> bool:
        statement = select(OAuth2AuthorizationCode).where(
            OAuth2AuthorizationCode.code
            == get_token_hash(token, secret=settings.SECRET)
        )

        result = await session.execute(statement)
        authorization_code = result.unique().scalar_one_or_none()

        if authorization_code is None:
            return False

        authorization_code.set_deleted_at()
        session.add(authorization_code)

        log.info(
            "Revoke leaked authorization code",
            id=authorization_code.id,
            notifier=notifier,
            url=url,
        )

        return True


oauth2_authorization_code = OAuth2AuthorizationCodeService(OAuth2AuthorizationCode)
