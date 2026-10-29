"""add competition fields

Revision ID: 7b29765ebb3a
Revises: 
Create Date: 2026-08-30 07:32:57.303985

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '7b29765ebb3a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------
    # 1. Add new columns to competition_seasons
    # ------------------------------------------
    with op.batch_alter_table('competition_seasons', schema=None) as batch_op:
        # Add all new columns as nullable
        batch_op.add_column(sa.Column('season', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('champion_id', sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column('runner_up_id', sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column('started_at', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('ended_at', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('is_archived', sa.Boolean(), nullable=True))

        # Create foreign keys
        batch_op.create_foreign_key(None, 'teams', ['champion_id'], ['id'])
        batch_op.create_foreign_key(None, 'teams', ['runner_up_id'], ['id'])

        # Drop old columns (no longer needed)
        batch_op.drop_column('end_date')
        batch_op.drop_column('is_current')
        batch_op.drop_column('start_date')
        batch_op.drop_column('status')
        batch_op.drop_column('name')

    # ----------------------------------------------------
    # 2. Populate the new 'season' column for existing rows
    #    (prevents future NOT NULL issues if we ever make it required)
    # ----------------------------------------------------
    # Use raw SQL to update all rows with a default season value
    op.execute(text("UPDATE competition_seasons SET season = '2025-2026' WHERE season IS NULL"))

    # ------------------------------------------
    # 3. Add new columns to competitions
    # ------------------------------------------
    with op.batch_alter_table('competitions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('season', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('is_archived', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('level', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('icon', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('current_champion_id', sa.UUID(), nullable=True))
        batch_op.create_foreign_key(None, 'teams', ['current_champion_id'], ['id'])


def downgrade():
    # ------------------------------------------
    # Revert changes (if needed)
    # ------------------------------------------
    with op.batch_alter_table('competitions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('current_champion_id')
        batch_op.drop_column('icon')
        batch_op.drop_column('level')
        batch_op.drop_column('is_archived')
        batch_op.drop_column('season')

    with op.batch_alter_table('competition_seasons', schema=None) as batch_op:
        # Restore old columns
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=100), nullable=False))
        batch_op.add_column(sa.Column('status', sa.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('start_date', sa.DATE(), nullable=True))
        batch_op.add_column(sa.Column('is_current', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('end_date', sa.DATE(), nullable=True))

        # Remove foreign keys and new columns
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('is_archived')
        batch_op.drop_column('ended_at')
        batch_op.drop_column('started_at')
        batch_op.drop_column('runner_up_id')
        batch_op.drop_column('champion_id')
        batch_op.drop_column('season')