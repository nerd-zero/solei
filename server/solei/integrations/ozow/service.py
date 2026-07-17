import time

import httpx
import structlog

from solei.config import settings
from solei.exceptions import SoleiError
from solei.logging import Logger

log: Logger = structlog.get_logger()


class OzowError(SoleiError): ...


class OzowService:
    def __init__(self) -> None:
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    @property
    def _base_url(self) -> str:
        return (
            settings.OZOW_STAGING_API_URL
            if settings.OZOW_IS_TEST
            else settings.OZOW_PRODUCTION_API_URL
        )

    @property
    def _token_url(self) -> str:
        if settings.OZOW_IS_TEST:
            return "https://stagingone.ozow.com/v1/token"
        return "https://one.ozow.com/v1/token"

    async def _get_access_token(self) -> str:
        # Return cached token if still valid (with 60s safety buffer)
        if self._access_token and time.monotonic() < self._token_expires_at - 60:
            return self._access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._token_url,
                data={
                    "client_id": settings.OZOW_CLIENT_ID,
                    "client_secret": settings.OZOW_CLIENT_SECRET,
                    "scope": "payments",
                    "grant_type": "client_credentials",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0,
            )

        if response.status_code != 200:
            log.error(
                "Ozow token request failed",
                status_code=response.status_code,
                response_body=response.text,
            )
            raise OzowError("Failed to obtain Ozow access token")

        data = response.json()
        self._access_token = data["access_token"]
        self._token_expires_at = time.monotonic() + float(data.get("expires_in", 3600))

        if not self._access_token:
            raise OzowError("Failed to obtain Ozow access token")

        return self._access_token

    async def create_payment_request(
        self,
        *,
        amount_cents: int,
        merchant_reference: str,
        return_url: str,
        notify_url: str,
        expire_at: str,
        payer_name: str | None = None,
        payer_email: str | None = None,
    ) -> dict[str, str]:
        token = await self._get_access_token()

        payload: dict[str, object] = {
            "siteCode": settings.OZOW_SITE_CODE,
            "region": "ZA",
            "amount": {
                "currency": "ZAR",
                "value": round(amount_cents / 100, 2),
            },
            "merchantReference": merchant_reference,
            "returnUrl": return_url,
            "notifyUrl": notify_url,
            "expireAt": expire_at,
        }

        if payer_name:
            payer: dict[str, object] = {
                "id": merchant_reference,
                "name": payer_name[:200],
            }
            if payer_email:
                payer["email"] = payer_email
            payload["payer"] = payer

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/payments",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                json=payload,
                timeout=30.0,
            )

        if response.status_code not in (200, 201):
            log.error(
                "Ozow create_payment_request failed",
                status_code=response.status_code,
                response_body=response.text,
            )
            raise OzowError(
                f"Ozow payment request failed: HTTP {response.status_code}",
            )

        data = response.json()
        return {
            "id": data["id"],
            "redirectUrl": data.get("redirectUrl", ""),
        }

    async def get_payment(self, payment_id: str) -> dict[str, object]:
        token = await self._get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self._base_url}/payments/{payment_id}",
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                timeout=30.0,
            )

        if response.status_code != 200:
            raise OzowError(
                f"Ozow get_payment failed: HTTP {response.status_code}",
            )

        return response.json()  # type: ignore[no-any-return]


ozow_service = OzowService()
