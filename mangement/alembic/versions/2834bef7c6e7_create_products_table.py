"""create products table

Revision ID: 2834bef7c6e7
Revises: 6e5178e0f7e2
Create Date: 2025-12-29 12:57:44.563898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = '2834bef7c6e7'
down_revision: Union[str, Sequence[str], None] = '6e5178e0f7e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("rating", sa.String(), nullable=True),
        sa.Column("platform", sa.String(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("final_attributes", sa.JSON(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), server_default=func.now()),
        sa.Column("created_at", sa.DateTime(), server_default=func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )

   


def downgrade():
   
    op.drop_table("products")

