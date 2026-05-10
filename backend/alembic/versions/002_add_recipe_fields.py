"""add missing recipe fields: cooking_time, difficulty, description

Revision ID: 002
Revises: 001
Create Date: 2026-05-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("recipes") as batch_op:
        batch_op.add_column(sa.Column("cooking_time", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("difficulty", sa.String(20), nullable=True))
        batch_op.add_column(sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("recipes") as batch_op:
        batch_op.drop_column("description")
        batch_op.drop_column("difficulty")
        batch_op.drop_column("cooking_time")
