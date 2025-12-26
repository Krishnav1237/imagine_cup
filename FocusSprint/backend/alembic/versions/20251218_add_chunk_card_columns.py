"""add chunk card columns

Revision ID: add_chunk_card_columns
Revises: 
Create Date: 2025-12-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_chunk_card_columns'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('content_chunks', sa.Column('card_json', sa.Text(), nullable=True))
    op.add_column('content_chunks', sa.Column('source_file', sa.String(length=512), nullable=True))
    op.add_column('content_chunks', sa.Column('source_page', sa.Integer(), nullable=True))
    op.add_column('content_chunks', sa.Column('source_slide', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('content_chunks', 'card_json')
    op.drop_column('content_chunks', 'source_file')
    op.drop_column('content_chunks', 'source_page')
    op.drop_column('content_chunks', 'source_slide')