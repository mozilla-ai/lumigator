"""Add job type to job table

Revision ID: 3be4994d87d5
Revises: 4c0345b3d525
Create Date: 2025-02-03 17:38:54.564918

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3be4994d87d5"  # pragma: allowlist secret
down_revision: str | None = "4c0345b3d525"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("job_type", sa.String(), nullable=True))


def downgrade() -> None:
    op.remove_column("jobs", sa.Column("job_type", sa.String(), nullable=True))
