import hashlib

import httpx
import structlog

from solei.config import settings
from solei.exceptions import SoleiError
from solei.logging import Logger

log: Logger = structlog.get_logger()


class OzowError(SoleiError):
    def __init__(self, message: str, error_message: str | None = None) -> None:
        self.error_message = error_message
        super().__init__(message)


class OzowService:
    @property
    def _base_url(self) -> str:
        return (
            settings.OZOW_STAGING_API_URL
            if settings.OZOW_IS_TEST
            else settings.OZOW_PRODUCTION_API_URL
        )

    def _generate_hash(
        self,
        *,
        site_code: str,
        country_code: str,
        currency_code: str,
        amount: str,
        transaction_reference: str,
        bank_reference: str,
        cancel_url: str,
        error_url: str,
        success_url: str,
        notify_url: str,
        is_test: bool,
    ) -> str:
        input_string = (
            site_code
            + country_code
            + currency_code
            + amount
            + transaction_reference
            + bank_reference
            + cancel_url
            + error_url
            + success_url
            + notify_url
            + str(is_test).lower()
            + settings.OZOW_PRIVATE_KEY
        )
        return hashlib.sha512(input_string.lower().encode()).hexdigest()

    def verify_notification_hash(self, data: dict[str, str]) -> bool:
        # Ozow notification hash: fields 1-13 in order + private key, lowercase, SHA512.
        # Fields per Ozow spec: SiteCode, TransactionId, TransactionReference,
        # Amount, Status, Optional1-5, CurrencyCode, IsTest, StatusMessage.
        fields = [
            data.get("SiteCode", ""),
            data.get("TransactionId", ""),
            data.get("TransactionReference", ""),
            data.get("Amount", ""),
            data.get("Status", ""),
            data.get("Optional1", ""),
            data.get("Optional2", ""),
            data.get("Optional3", ""),
            data.get("Optional4", ""),
            data.get("Optional5", ""),
            data.get("CurrencyCode", ""),
            data.get("IsTest", ""),
            data.get("StatusMessage", ""),
        ]
        input_string = "".join(fields) + settings.OZOW_PRIVATE_KEY
        expected = hashlib.sha512(input_string.lower().encode()).hexdigest()
        received = data.get("Hash", "")
        # Strip leading zeros before comparison — some SHA512 implementations omit them
        return received.lstrip("0").lower() == expected.lstrip("0").lower()

    async def create_payment_request(
        self,
        *,
        amount_cents: int,
        transaction_reference: str,
        bank_reference: str,
        cancel_url: str,
        error_url: str,
        success_url: str,
        notify_url: str,
        customer_name: str | None = None,
    ) -> dict[str, str]:
        amount = f"{amount_cents / 100:.2f}"
        is_test = settings.OZOW_IS_TEST

        hash_check = self._generate_hash(
            site_code=settings.OZOW_SITE_CODE,
            country_code="ZA",
            currency_code="ZAR",
            amount=amount,
            transaction_reference=transaction_reference,
            bank_reference=bank_reference,
            cancel_url=cancel_url,
            error_url=error_url,
            success_url=success_url,
            notify_url=notify_url,
            is_test=is_test,
        )

        payload: dict[str, object] = {
            "siteCode": settings.OZOW_SITE_CODE,
            "countryCode": "ZA",
            "currencyCode": "ZAR",
            "amount": float(amount),
            "transactionReference": transaction_reference,
            "bankReference": bank_reference,
            "cancelUrl": cancel_url,
            "errorUrl": error_url,
            "successUrl": success_url,
            "notifyUrl": notify_url,
            "isTest": is_test,
            "hashCheck": hash_check,
        }
        if customer_name:
            payload["customer"] = customer_name[:100]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/PostPaymentRequest",
                headers={
                    "Accept": "application/json",
                    "ApiKey": settings.OZOW_API_KEY,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30.0,
            )

        data = response.json()

        if response.status_code != 200 or data.get("errorMessage"):
            log.error(
                "Ozow create_payment_request failed",
                status_code=response.status_code,
                error_message=data.get("errorMessage"),
                response_body=data,
            )
            raise OzowError(
                f"Ozow payment request failed: {data.get('errorMessage', 'unknown error')}",
                error_message=data.get("errorMessage"),
            )

        return {
            "url": data["url"],
            "paymentRequestId": data["paymentRequestId"],
        }


ozow_service = OzowService()
