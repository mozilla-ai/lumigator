"""Added experiments table

Revision ID: fa1278e4a265
Revises: e9679cbc3c36
Create Date: 2025-01-08 00:41:37.785066

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fa1278e4a265"  # pragma: allowlist secret
down_revision: str | None = "e9679cbc3c36"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "experiments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("CREATED", "PENDING", "RUNNING", "FAILED", "SUCCEEDED", name="jobstatus"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_table("experiments")
    # ### end Alembic commands ###
