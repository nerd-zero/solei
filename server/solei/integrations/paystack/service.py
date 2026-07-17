import hashlib
import hmac
from typing import TYPE_CHECKING, Any

import httpx
import structlog

from solei.config import settings
from solei.exceptions import SoleiError

if TYPE_CHECKING:
    from solei.models import User

log = structlog.get_logger()

PAYSTACK_BASE_URL = "https://api.paystack.co"


class PaystackError(SoleiError): ...


def _parse_error_message(response: httpx.Response, fallback: str) -> str:
    try:
        return response.json().get("message", fallback)
    except Exception:
        return response.text or fallback


class PaystackService:
    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self._headers, timeout=30.0)

    async def create_customer(self, user: "User") -> dict[str, Any]:
        payload: dict[str, Any] = {"email": user.email}
        if user.first_name:
            payload["first_name"] = user.first_name
        if user.last_name:
            payload["last_name"] = user.last_name

        async with self._client() as client:
            response = await client.post(
                f"{PAYSTACK_BASE_URL}/customer",
                json=payload,
            )

        if response.status_code not in (200, 201):
            log.error(
                "paystack.create_customer.error",
                status=response.status_code,
                body=response.text,
            )
            raise PaystackError("Failed to create Paystack customer.")

        data = response.json()
        return data["data"]

    async def validate_identity(
        self, customer_code: str, payload: dict[str, Any]
    ) -> None:
        async with self._client() as client:
            response = await client.post(
                f"{PAYSTACK_BASE_URL}/customer/{customer_code}/identification",
                json=payload,
            )

        if response.status_code not in (200, 202):
            log.error(
                "paystack.validate_identity.error",
                customer_code=customer_code,
                status=response.status_code,
                body=response.text,
            )
            message = _parse_error_message(response, "Identity validation failed.")
            raise PaystackError(message)

    async def resolve_bank_account(
        self, account_number: str, bank_code: str
    ) -> dict[str, Any]:
        async with self._client() as client:
            response = await client.get(
                f"{PAYSTACK_BASE_URL}/bank/resolve",
                params={"account_number": account_number, "bank_code": bank_code},
            )

        if response.status_code != 200:
            log.error(
                "paystack.resolve_bank_account.error",
                account_number=account_number,
                bank_code=bank_code,
                status=response.status_code,
                body=response.text,
            )
            message = _parse_error_message(response, "Failed to resolve bank account.")
            raise PaystackError(message)

        return response.json()["data"]

    async def validate_bank_account(
        self,
        account_number: str,
        bank_code: str,
        account_name: str,
        account_type: str,
        country_code: str,
        document_type: str,
        document_number: str,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "account_number": account_number,
            "bank_code": bank_code,
            "account_name": account_name,
            "account_type": account_type,
            "country_code": country_code,
            "document_type": document_type,
        }
        if document_number:
            payload["document_number"] = document_number

        async with self._client() as client:
            response = await client.post(
                f"{PAYSTACK_BASE_URL}/bank/validate",
                json=payload,
            )

        if response.status_code != 200:
            log.error(
                "paystack.validate_bank_account.error",
                account_number=account_number,
                country_code=country_code,
                status=response.status_code,
                body=response.text,
            )
            message = _parse_error_message(response, "Failed to validate bank account.")
            raise PaystackError(message)

        data = response.json()
        if not data.get("data", {}).get("verified", False):
            message = (
                data.get("data", {}).get("verificationMessage")
                or "Bank account verification failed."
            )
            raise PaystackError(message)

        return data["data"]

    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        expected = hmac.new(
            settings.PAYSTACK_WEBHOOK_SECRET.encode(), body, hashlib.sha512
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


paystack = PaystackService()
