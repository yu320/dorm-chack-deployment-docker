"""add_announcements_table

Revision ID: 503107688e81
Revises: b6d44abd942f
Create Date: 2025-11-27 00:58:45.609015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '503107688e81'
down_revision: Union[str, Sequence[str], None] = '8220a7569c30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create TagType enum
    # op.execute("CREATE TYPE tagtype AS ENUM ('primary', 'success', 'warning', 'danger', 'info')")
    
    # Create announcements table
    op.create_table(
        'announcements',
        sa.Column('id', sa.CHAR(length=36), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tag', sa.String(length=50), nullable=False),
        sa.Column('tag_type', sa.Enum('primary', 'success', 'warning', 'danger', 'info', name='tagtype'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.CHAR(length=36), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop announcements table
    op.drop_table('announcements')
    
    # Drop TagType enum
    op.execute("DROP TYPE tagtype")
