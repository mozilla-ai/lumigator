"""Add stopped state

Revision ID: 400ea1feca4a
Revises: 54e483b63d8a
Create Date: 2025-02-26 15:25:26.295425

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "400ea1feca4a"  # pragma: allowlist secret
down_revision: str | None = "54e483b63d8a"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.alter_column(
            "status",
            type_=sa.Enum("CREATED", "PENDING", "RUNNING", "FAILED", "SUCCEEDED", "STOPPED", name="jobstatus"),
            existing_nullable=False,
            existing_type=sa.Enum("CREATED", "PENDING", "RUNNING", "FAILED", "SUCCEEDED", name="jobstatus"),
        )


def downgrade() -> None:
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.alter_column(
            "status",
            type_=sa.Enum("CREATED", "PENDING", "RUNNING", "FAILED", "SUCCEEDED", name="jobstatus"),
            existing_nullable=False,
            existing_type=sa.Enum("CREATED", "PENDING", "RUNNING", "FAILED", "SUCCEEDED", "STOPPED", name="jobstatus"),
        )
