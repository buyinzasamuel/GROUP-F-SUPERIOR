"""Added image field to Destination model

Revision ID: 8b1c6dee9ea6
Revises: 72c6657a408a
Create Date: 2025-07-22 17:42:35.408025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b1c6dee9ea6'
down_revision = '72c6657a408a'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add destination_id as nullable
    with op.batch_alter_table('tour', schema=None) as batch_op:
        batch_op.add_column(sa.Column('destination_id', sa.Integer(), nullable=True))

    # 2. Set all existing tours to use destination_id = 7
    op.execute("UPDATE tour SET destination_id = 7")

    # 3. Make the column non-nullable and create the foreign key
    with op.batch_alter_table('tour', schema=None) as batch_op:
        batch_op.alter_column('destination_id', nullable=False)
        batch_op.create_foreign_key(None, 'destination', ['destination_id'], ['id'])

    # 4. Add created_at column to user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    with op.batch_alter_table('tour', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('destination_id')
