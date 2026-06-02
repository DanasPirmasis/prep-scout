"""add rimi products

Revision ID: c3f04ea8d9b1
Revises: 4d77420cb242
Create Date: 2026-06-02 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c3f04ea8d9b1"
down_revision: Union[str, Sequence[str], None] = "4d77420cb242"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "rimi_products",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("category", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("brand", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("currency", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("image_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("price_text", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("unit_price_text", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("comparative_unit", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("data_gtm_eec_product", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("rimi_products")
