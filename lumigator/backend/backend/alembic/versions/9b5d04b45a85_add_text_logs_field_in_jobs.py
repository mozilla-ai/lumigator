"""Add text logs field in jobs

Revision ID: 9b5d04b45a85
Revises: 4c0345b3d525
Create Date: 2025-02-06 15:34:20.212502

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9b5d04b45a85"  # pragma: allowlist secret
down_revision: str | None = "4c0345b3d525"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("logs", sa.Text()))


def downgrade() -> None:
    op.drop_column("jobs", "logs")
