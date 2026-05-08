"""initial schema with expenses and api_keys

Revision ID: 72f0f3d80ec1
Revises: 
Create Date: 2026-05-07 22:09:38.704662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72f0f3d80ec1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear api_keys solo si no existe
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'api_keys' not in tables:
        op.create_table('api_keys',
            sa.Column('key', sa.String(), nullable=False),
            sa.Column('owner', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('key')
        )

    # Añadir owner a expenses solo si no existe
    columns = [col['name'] for col in inspector.get_columns('expenses')]
    if 'owner' not in columns:
        op.add_column('expenses', sa.Column('owner', sa.String(), nullable=True, server_default='default'))
        op.execute("UPDATE expenses SET owner = 'default' WHERE owner IS NULL")
        op.alter_column('expenses', 'owner', nullable=False)


def downgrade() -> None:
    op.drop_column('expenses', 'owner')
    op.drop_table('api_keys')
