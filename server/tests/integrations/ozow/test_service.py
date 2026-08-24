import httpx
import pytest
import respx

from solei.config import settings
from solei.integrations.ozow.service import OzowError, OzowService

pytestmark = pytest.mark.asyncio

TOKEN_URL = f"{settings.OZOW_STAGING_API_URL}/token"
PAYMENTS_URL = f"{settings.OZOW_STAGING_API_URL}/payments"


async def _create_payment_request(service: OzowService) -> dict[str, str]:
    return await service.create_payment_request(
        amount_cents=10000,
        merchant_reference="checkout-123",
        return_url="https://example.com/return",
        notify_url="https://example.com/notify",
        expire_at="2026-08-22T00:00:00Z",
    )


class TestGetAccessToken:
    async def test_success_requests_payments_scope(self) -> None:
        service = OzowService()

        with respx.mock:
            route = respx.post(TOKEN_URL).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "access_token": "tok123",
                        "token_type": "bearer",
                        "expires_in": 3600,
                    },
                )
            )

            token = await service._get_access_token()

        assert token == "tok123"
        sent_body = httpx.QueryParams(route.calls.last.request.content.decode())
        assert sent_body["scope"] == "payments"

    async def test_caching_returns_same_token_without_second_call(self) -> None:
        service = OzowService()

        with respx.mock:
            route = respx.post(TOKEN_URL).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "access_token": "tok123",
                        "token_type": "bearer",
                        "expires_in": 3600,
                    },
                )
            )

            first = await service._get_access_token()
            second = await service._get_access_token()

        assert first == second == "tok123"
        assert route.call_count == 1

    async def test_non_200_raises_ozow_error(self) -> None:
        service = OzowService()

        with respx.mock:
            respx.post(TOKEN_URL).mock(
                return_value=httpx.Response(401, text="invalid_client")
            )

            with pytest.raises(OzowError):
                await service._get_access_token()


class TestCreatePaymentRequest:
    async def test_success_returns_id_and_redirect_url(self) -> None:
        service = OzowService()

        with respx.mock:
            respx.post(TOKEN_URL).mock(
                return_value=httpx.Response(
                    200, json={"access_token": "tok123", "expires_in": 3600}
                )
            )
            respx.post(PAYMENTS_URL).mock(
                return_value=httpx.Response(
                    201,
                    json={
                        "id": "abc-123",
                        # Ozow's OneAPI actually returns this capitalized
                        # ("Created"), despite the docs showing lowercase.
                        "status": "Created",
                        "redirectUrl": "https://pay.ozow.com/abc-123",
                        "links": {
                            "self": "https://one.ozow.com/v1/payments/abc-123",
                            "cancel": "https://one.ozow.com/v1/payments/abc-123/cancel",
                            "transactions": "https://one.ozow.com/v1/payments/abc-123/transactions",
                        },
                    },
                )
            )

            result = await _create_payment_request(service)

        assert result == {
            "id": "abc-123",
            "redirectUrl": "https://pay.ozow.com/abc-123",
        }

    async def test_non_created_status_raises_with_reason(self) -> None:
        service = OzowService()

        with respx.mock:
            respx.post(TOKEN_URL).mock(
                return_value=httpx.Response(
                    200, json={"access_token": "tok123", "expires_in": 3600}
                )
            )
            respx.post(PAYMENTS_URL).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "id": "abc-123",
                        "status": "expired",
                        "reason": "insufficient_funds",
                    },
                )
            )

            with pytest.raises(OzowError) as exc_info:
                await _create_payment_request(service)

        assert "expired" in str(exc_info.value)
        assert "insufficient_funds" in str(exc_info.value)

    async def test_http_error_status_raises_ozow_error(self) -> None:
        service = OzowService()

        with respx.mock:
            respx.post(TOKEN_URL).mock(
                return_value=httpx.Response(
                    200, json={"access_token": "tok123", "expires_in": 3600}
                )
            )
            respx.post(PAYMENTS_URL).mock(
                return_value=httpx.Response(403, json={"reason": "invalid scope"})
            )

            with pytest.raises(OzowError):
                await _create_payment_request(service)

    async def test_token_request_failure_propagates_before_payment_call(
        self,
    ) -> None:
        service = OzowService()

        with respx.mock:
            respx.post(TOKEN_URL).mock(
                return_value=httpx.Response(401, text="invalid_client")
            )

            with pytest.raises(OzowError):
                await _create_payment_request(service)
