"""add_identity_verification_provider_to_users

Revision ID: 8dd4c61098da
Revises: 1a2e0acc75e3
Create Date: 2026-04-30 10:33:36.079256

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8dd4c61098da"
down_revision = "1a2e0acc75e3"
branch_labels: tuple[str] | None = None
depends_on: tuple[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "identity_verification_provider",
            sa.String(length=20),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "identity_verification_provider")
