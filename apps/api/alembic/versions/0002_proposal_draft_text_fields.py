"""expand proposal draft fields to text

Revision ID: 0004_proposal_draft_text_fields
Revises: 0003_domain_platform_tables
Create Date: 2026-04-22 12:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0004_proposal_draft_text_fields'
down_revision = '0003_domain_platform_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('proposal_projects') as batch_op:
        batch_op.alter_column('generated_outline_uri', existing_type=sa.String(length=500), type_=sa.Text(), existing_nullable=False)
        batch_op.alter_column('technical_draft_uri', existing_type=sa.String(length=500), type_=sa.Text(), existing_nullable=False)
        batch_op.alter_column('commercial_draft_uri', existing_type=sa.String(length=500), type_=sa.Text(), existing_nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('proposal_projects') as batch_op:
        batch_op.alter_column('generated_outline_uri', existing_type=sa.Text(), type_=sa.String(length=500), existing_nullable=False)
        batch_op.alter_column('technical_draft_uri', existing_type=sa.Text(), type_=sa.String(length=500), existing_nullable=False)
        batch_op.alter_column('commercial_draft_uri', existing_type=sa.Text(), type_=sa.String(length=500), existing_nullable=False)
