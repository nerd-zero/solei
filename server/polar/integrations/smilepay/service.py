import httpx
import structlog

from polar.config import settings
from polar.exceptions import PolarError
from polar.logging import Logger

log: Logger = structlog.get_logger()

SANDBOX_URL = "https://zbnet.zb.co.zw/wallet_sandbox_api/payments-gateway"
PRODUCTION_URL = "https://zbnet.zb.co.zw/wallet_gateway/payments-gateway"

CURRENCY_CODES: dict[str, str] = {
    "usd": "840",
    "zwg": "924",
}


class SmilePayError(PolarError):
    def __init__(self, message: str, response_code: str | None = None) -> None:
        self.response_code = response_code
        super().__init__(message)


class SmilePayService:
    @property
    def _base_url(self) -> str:
        if settings.SMILEPAY_SANDBOX:
            return SANDBOX_URL
        return PRODUCTION_URL

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": settings.SMILEPAY_API_KEY,
            "x-api-secret": settings.SMILEPAY_API_SECRET,
            "Content-Type": "application/json",
        }

    async def initiate_transaction(
        self,
        *,
        order_reference: str,
        amount_cents: int,
        currency: str,
        return_url: str,
        result_url: str,
        item_name: str,
        item_description: str,
        first_name: str | None,
        email: str | None,
    ) -> dict[str, str]:
        currency_code = CURRENCY_CODES.get(currency.lower())
        if currency_code is None:
            raise SmilePayError(
                f"Unsupported currency for SmilePay: {currency}. "
                f"Supported currencies: {', '.join(CURRENCY_CODES.keys())}"
            )

        amount = f"{amount_cents / 100:.2f}"

        payload = {
            "orderReference": order_reference,
            "amount": amount,
            "currencyCode": currency_code,
            "returnUrl": return_url,
            "resultUrl": result_url,
            "itemName": item_name,
            "itemDescription": item_description,
        }
        if first_name:
            payload["firstName"] = first_name
        if email:
            payload["email"] = email

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/payments/initiate-transaction",
                headers=self._headers,
                json=payload,
                timeout=30.0,
            )

        data = response.json()
        response_code = data.get("responseCode")

        if response.status_code != 200 or response_code != "00":
            log.error(
                "SmilePay initiate_transaction failed",
                status_code=response.status_code,
                response_code=response_code,
                response_body=data,
            )
            raise SmilePayError(
                f"SmilePay transaction initiation failed (code={response_code})",
                response_code=response_code,
            )

        return {
            "paymentUrl": data["paymentUrl"],
            "transactionReference": data["transactionReference"],
        }

    async def verify_payment_status(self, order_reference: str) -> str:
        """
        Verify a payment status with SmilePay's status check API.
        Returns the status string (e.g. "PAID", "FAILED", "CANCELED").
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self._base_url}/payments/transaction/{order_reference}/status/check",
                headers=self._headers,
                timeout=30.0,
            )

        data = response.json()

        if response.status_code != 200:
            log.error(
                "SmilePay verify_payment_status failed",
                order_reference=order_reference,
                status_code=response.status_code,
                response_body=data,
            )
            raise SmilePayError(
                f"SmilePay status check failed for order {order_reference}"
            )

        return data.get("status", "UNKNOWN")


smilepay_service = SmilePayService()
