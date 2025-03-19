"""Move to non-native enums for datasetFormat

Revision ID: 76bbe19c945c
Revises: da3992fd274e
Create Date: 2025-03-13 09:52:33.090037

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "76bbe19c945c"  # pragma: allowlist secret
down_revision: str | None = "da3992fd274e"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Leave removing the job status for next migration
    with op.batch_alter_table("datasets") as batch_op:
        native_enum = sa.Enum("JOB", name="datasetformat")
        non_native_enum = sa.Enum("JOB", "EXPERIMENT", native_enum=False)
        batch_op.alter_column(
            "format",
            type_=non_native_enum,
            existing_nullable=False,
            existing_type=native_enum,
        )


def downgrade() -> None:
    with op.batch_alter_table("jobs") as batch_op:
        native_enum = sa.Enum("JOB", name="datasetformat")
        non_native_enum = sa.Enum("JOB", "EXPERIMENT")
        batch_op.alter_column(
            "format",
            type_=native_enum,
            existing_nullable=False,
            existing_type=non_native_enum,
        )
