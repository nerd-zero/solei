import pytest

from solei.invoice.service import invoice as invoice_service
from solei.kit.address import Address, CountryAlpha2
from solei.models import Customer, Product
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_order


@pytest.mark.asyncio
async def test_create_order_invoice(
    save_fixture: SaveFixture, product: Product, customer: Customer
) -> None:
    order = await create_order(
        save_fixture,
        product=product,
        customer=customer,
        billing_name="John Doe",
        billing_address=Address(
            line1="456 Customer Ave",
            city="Los Angeles",
            state="CA",
            postal_code="90001",
            country=CountryAlpha2("US"),
        ),
        invoice_number="SOLEI-0001",
    )

    invoice_path = await invoice_service.create_order_invoice(order)
