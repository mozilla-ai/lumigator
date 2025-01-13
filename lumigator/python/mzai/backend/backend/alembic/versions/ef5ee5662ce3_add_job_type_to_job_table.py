"""Add job type to job table

Revision ID: ef5ee5662ce3
Revises: e9679cbc3c36
Create Date: 2025-01-07 13:24:40.657958

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ef5ee5662ce3"  # pragma: allowlist secret
down_revision: str | None = "e9679cbc3c36"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("job_type", sa.String(), nullable=True))


def downgrade() -> None:
    op.remove_column("jobs", sa.Column("job_type", sa.String(), nullable=True))
