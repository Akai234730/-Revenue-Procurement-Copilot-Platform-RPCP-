"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-01 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'leads',
        sa.Column('source_channel', sa.String(length=64), nullable=False),
        sa.Column('source_detail', sa.String(length=128), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('contact_name', sa.String(length=128), nullable=False),
        sa.Column('contact_title', sa.String(length=128), nullable=False),
        sa.Column('phone', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('industry_code', sa.String(length=64), nullable=False),
        sa.Column('industry_name', sa.String(length=128), nullable=False),
        sa.Column('company_size', sa.String(length=64), nullable=False),
        sa.Column('region_code', sa.String(length=64), nullable=False),
        sa.Column('website_url', sa.String(length=255), nullable=False),
        sa.Column('demand_summary', sa.Text(), nullable=False),
        sa.Column('budget_signal', sa.String(length=128), nullable=False),
        sa.Column('project_stage', sa.String(length=64), nullable=False),
        sa.Column('owner_user_id', sa.String(length=64), nullable=False),
        sa.Column('ai_profile_summary', sa.Text(), nullable=False),
        sa.Column('ai_lead_score', sa.Float(), nullable=False),
        sa.Column('ai_maturity_level', sa.String(length=32), nullable=False),
        sa.Column('ai_priority_level', sa.String(length=16), nullable=False),
        sa.Column('ai_next_action', sa.Text(), nullable=False),
        sa.Column('ai_confidence', sa.Float(), nullable=False),
        sa.Column('ai_risk_flag', sa.Text(), nullable=False),
        sa.Column('lead_status', sa.String(length=32), nullable=False),
        sa.Column('crm_sync_status', sa.String(length=32), nullable=False),
        sa.Column('invalid_reason', sa.String(length=255), nullable=False),
        sa.Column('archived', sa.Boolean(), nullable=False),
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('leads')
