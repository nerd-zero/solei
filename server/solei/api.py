from fastapi import APIRouter

from solei.account.endpoints import router as accounts_router
from solei.auth.endpoints import router as auth_router
from solei.benefit.endpoints import router as benefits_router
from solei.benefit.grant.endpoints import router as benefit_grants_router
from solei.checkout.endpoints import router as checkout_router
from solei.checkout_link.endpoints import router as checkout_link_router
from solei.cli.endpoints import router as cli_router
from solei.custom_field.endpoints import router as custom_field_router
from solei.customer.endpoints import router as customer_router
from solei.customer_meter.endpoints import router as customer_meter_router
from solei.customer_portal.endpoints import router as customer_portal_router
from solei.customer_seat.endpoints import router as customer_seat_router
from solei.customer_session.endpoints import router as customer_session_router
from solei.discount.endpoints import router as discount_router
from solei.dispute.endpoints import router as dispute_router
from solei.email_update.endpoints import router as email_update_router
from solei.event.endpoints import router as event_router
from solei.event_type.endpoints import router as event_type_router
from solei.eventstream.endpoints import router as stream_router
from solei.file.endpoints import router as files_router
from solei.integrations.apple.endpoints import router as apple_router
from solei.integrations.chargeback_stop.endpoints import (
    router as chargeback_stop_router,
)
from solei.integrations.discord.endpoints import router as discord_router
from solei.integrations.github.endpoints import router as github_router
from solei.integrations.github_repository_benefit.endpoints import (
    router as github_repository_benefit_router,
)
from solei.integrations.google.endpoints import router as google_router
from solei.integrations.paystack.endpoints import router as paystack_router
from solei.integrations.plain.endpoints import router as plain_router
from solei.integrations.smilepay.endpoints import router as smilepay_router
from solei.integrations.stripe.endpoints import router as stripe_router
from solei.license_key.endpoints import router as license_key_router
from solei.login_code.endpoints import router as login_code_router
from solei.member.endpoints import router as member_router
from solei.meter.endpoints import router as meter_router
from solei.metrics.endpoints import router as metrics_router
from solei.notifications.endpoints import router as notifications_router
from solei.oauth2.endpoints.oauth2 import router as oauth2_router
from solei.order.endpoints import router as order_router
from solei.organization.endpoints import router as organization_router
from solei.organization_access_token.endpoints import (
    router as organization_access_token_router,
)
from solei.payment.endpoints import router as payment_router
from solei.payout.endpoints import router as payout_router
from solei.personal_access_token.endpoints import router as pat_router
from solei.product.endpoints import router as product_router
from solei.refund.endpoints import router as refund_router
from solei.subscription.endpoints import router as subscription_router
from solei.transaction.endpoints import router as transaction_router
from solei.user.endpoints import router as user_router
from solei.wallet.endpoints import router as wallet_router
from solei.webhook.endpoints import router as webhook_router

router = APIRouter(prefix="/v1")

# /users
router.include_router(user_router)
# /integrations/github
router.include_router(github_router)
# /integrations/github_repository_benefit
router.include_router(github_repository_benefit_router)
# /integrations/stripe
router.include_router(stripe_router)
# /integrations/discord
router.include_router(discord_router)
# /integrations/apple
router.include_router(apple_router)
# /login-code
router.include_router(login_code_router)
# /notifications
router.include_router(notifications_router)
# /personal_access_tokens
router.include_router(pat_router)
# /accounts
router.include_router(accounts_router)
# /stream
router.include_router(stream_router)
# /organizations
router.include_router(organization_router)
# /subscriptions
router.include_router(subscription_router)
# /transactions
router.include_router(transaction_router)
# /auth
router.include_router(auth_router)
# /oauth2
router.include_router(oauth2_router)
# /benefits
router.include_router(benefits_router)
# /benefit-grants
router.include_router(benefit_grants_router)
# /webhooks
router.include_router(webhook_router)
# /products
router.include_router(product_router)
# /orders
router.include_router(order_router)
# /refunds
router.include_router(refund_router)
# /disputes
router.include_router(dispute_router)
# /checkouts
router.include_router(checkout_router)
# /cli
router.include_router(cli_router)
# /files
router.include_router(files_router)
# /metrics
router.include_router(metrics_router)
# /integrations/google
router.include_router(google_router)
# /license-keys
router.include_router(license_key_router)
# /checkout-links
router.include_router(checkout_link_router)
# /custom-fields
router.include_router(custom_field_router)
# /discounts
router.include_router(discount_router)
# /customers
router.include_router(customer_router)
# /members
router.include_router(member_router)
# /customer-portal
router.include_router(customer_portal_router)
# /seats
router.include_router(customer_seat_router)
# /update-email
router.include_router(email_update_router)
# /customer-sessions
router.include_router(customer_session_router)
# /integrations/plain
router.include_router(plain_router)
# /events
router.include_router(event_router)
# /event-types
router.include_router(event_type_router)
# /meters
router.include_router(meter_router)
# /organization-access-tokens
router.include_router(organization_access_token_router)
# /customer-meters
router.include_router(customer_meter_router)
# /payments
router.include_router(payment_router)
# /payouts
router.include_router(payout_router)
# /wallets
router.include_router(wallet_router)
# /integrations/chargeback-stop
router.include_router(chargeback_stop_router)
# /integrations/smilepay
router.include_router(smilepay_router)
# /integrations/paystack
router.include_router(paystack_router)
