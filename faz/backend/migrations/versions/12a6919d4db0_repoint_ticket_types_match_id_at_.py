"""Repoint ticket_types, tickets and seat_holds to competition_matches

Revision ID: 12a6919d4db0
Revises: ac20bd9fc5c7
Create Date: 2026-09-10 15:33:38.929291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12a6919d4db0'
down_revision = 'ac20bd9fc5c7'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # ------------------------------------------------------------------
    # 1. Delete orphaned rows BEFORE swapping the FKs.
    #
    #    ticket_types / tickets / seat_holds still reference matches.id.
    #    Any row whose match_id isn't already present in competition_matches
    #    will block creation of the new FK. There's no reliable mapping from
    #    the old string-based matches to the new UUID-based competition_matches,
    #    so we drop the orphans.
    #
    #    Order matters because of FK dependencies:
    #        tickets       → order_items, ticket_types
    #        order_items   → ticket_types
    #        seat_holds    → ticket_types
    #        ticket_types  → matches
    # ------------------------------------------------------------------
    bind.execute(sa.text("""
        DELETE FROM tickets
        WHERE match_id NOT IN (SELECT id FROM competition_matches)
    """))

    bind.execute(sa.text("""
        DELETE FROM order_items
        WHERE ticket_type_id IN (
            SELECT id FROM ticket_types
            WHERE match_id NOT IN (SELECT id FROM competition_matches)
        )
    """))

    bind.execute(sa.text("""
        DELETE FROM seat_holds
        WHERE match_id NOT IN (SELECT id FROM competition_matches)
    """))

    bind.execute(sa.text("""
        DELETE FROM ticket_types
        WHERE match_id NOT IN (SELECT id FROM competition_matches)
    """))

    # ------------------------------------------------------------------
    # 2. ticket_types — swap the FK to competition_matches
    # ------------------------------------------------------------------
    with op.batch_alter_table('ticket_types', schema=None) as batch_op:
        batch_op.drop_constraint('ticket_types_match_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'ticket_types_match_id_fkey',
            'competition_matches',
            ['match_id'],
            ['id'],
            ondelete='CASCADE',
        )

    # ------------------------------------------------------------------
    # 3. tickets — swap the FK to competition_matches
    # ------------------------------------------------------------------
    with op.batch_alter_table('tickets', schema=None) as batch_op:
        batch_op.drop_constraint('tickets_match_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'tickets_match_id_fkey',
            'competition_matches',
            ['match_id'],
            ['id'],
        )

    # ------------------------------------------------------------------
    # 4. seat_holds — swap the FK to competition_matches
    # ------------------------------------------------------------------
    with op.batch_alter_table('seat_holds', schema=None) as batch_op:
        batch_op.drop_constraint('seat_holds_match_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'seat_holds_match_id_fkey',
            'competition_matches',
            ['match_id'],
            ['id'],
            ondelete='CASCADE',
        )


def downgrade():
    # Reverse, in reverse order. Explicit constraint names so the drops work.
    with op.batch_alter_table('seat_holds', schema=None) as batch_op:
        batch_op.drop_constraint('seat_holds_match_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'seat_holds_match_id_fkey',
            'matches',
            ['match_id'],
            ['id'],
        )

    with op.batch_alter_table('tickets', schema=None) as batch_op:
        batch_op.drop_constraint('tickets_match_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'tickets_match_id_fkey',
            'matches',
            ['match_id'],
            ['id'],
        )

    with op.batch_alter_table('ticket_types', schema=None) as batch_op:
        batch_op.drop_constraint('ticket_types_match_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'ticket_types_match_id_fkey',
            'matches',
            ['match_id'],
            ['id'],
        )