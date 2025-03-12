"""Change type from enum to varchar

Revision ID: da3992fd274e
Revises: 400ea1feca4a
Create Date: 2025-03-10 09:30:27.476031

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "da3992fd274e"  # pragma: allowlist secret
down_revision: str | None = "400ea1feca4a"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Leave removing the job status for next migration
    with op.batch_alter_table("jobs") as batch_op:
        native_enum = sa.Enum("CREATED", "PENDING", "RUNNING", "FAILED", "SUCCEEDED", name="jobstatus")
        non_native_enum = sa.Enum("CREATED", "PENDING", "RUNNING", "FAILED", "SUCCEEDED", "STOPPED", native_enum=False)
        batch_op.alter_column(
            "status",
            type_=non_native_enum,
            existing_nullable=False,
            existing_type=native_enum,
        )


def downgrade() -> None:
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.alter_column(
            "status",
            type_=sa.Enum("CREATED", "PENDING", "RUNNING", "FAILED", "SUCCEEDED", name="jobstatus"),
            existing_nullable=False,
            existing_type=sa.Enum("CREATED", "PENDING", "RUNNING", "FAILED", "SUCCEEDED", "STOPPED", native_enum=False),
        )
