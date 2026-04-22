"""add domain and platform tables

Revision ID: 0003_domain_platform_tables
Revises: 0002_auth_tables
Create Date: 2026-04-20 00:30:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0003_domain_platform_tables'
down_revision = '0002_auth_tables'
branch_labels = None
depends_on = None


def _base_cols():
    return [
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    ]


def upgrade() -> None:
    op.create_table('followup_records', sa.Column('lead_id', sa.String(64), nullable=False), sa.Column('followup_type', sa.String(64), nullable=False, server_default='call'), sa.Column('followup_channel', sa.String(64), nullable=False, server_default='phone'), sa.Column('followup_content', sa.Text(), nullable=False, server_default=''), sa.Column('followup_result', sa.String(128), nullable=False, server_default=''), sa.Column('next_action', sa.Text(), nullable=False, server_default=''), sa.Column('recorder_user_id', sa.String(64), nullable=False, server_default='system'), sa.Column('ai_generated_flag', sa.Boolean(), nullable=False, server_default=sa.false()), *_base_cols())
    op.create_index(op.f('ix_followup_records_lead_id'), 'followup_records', ['lead_id'], unique=False)
    op.create_table('proposal_projects', sa.Column('customer_id', sa.String(64), nullable=False, server_default=''), sa.Column('project_name', sa.String(255), nullable=False), sa.Column('industry_code', sa.String(64), nullable=False, server_default=''), sa.Column('bid_type', sa.String(64), nullable=False, server_default='rfp'), sa.Column('rfp_doc_uri', sa.String(500), nullable=False, server_default=''), sa.Column('requirement_json', sa.Text(), nullable=False, server_default='{}'), sa.Column('scoring_rule_json', sa.Text(), nullable=False, server_default='{}'), sa.Column('generated_outline_uri', sa.String(500), nullable=False, server_default=''), sa.Column('technical_draft_uri', sa.String(500), nullable=False, server_default=''), sa.Column('commercial_draft_uri', sa.String(500), nullable=False, server_default=''), sa.Column('version_no', sa.Integer(), nullable=False, server_default='1'), sa.Column('proposal_status', sa.String(32), nullable=False, server_default='draft'), sa.Column('risk_level', sa.String(32), nullable=False, server_default='medium'), sa.Column('approval_status', sa.String(32), nullable=False, server_default='pending'), sa.Column('owner_user_id', sa.String(64), nullable=False, server_default=''), *_base_cols())
    op.create_table('suppliers', sa.Column('supplier_name', sa.String(255), nullable=False), sa.Column('supplier_code', sa.String(64), nullable=False, server_default=''), sa.Column('supplier_category', sa.String(64), nullable=False, server_default=''), sa.Column('qualification_level', sa.String(64), nullable=False, server_default=''), sa.Column('region_code', sa.String(64), nullable=False, server_default=''), sa.Column('major_products', sa.Text(), nullable=False, server_default=''), sa.Column('contact_person', sa.String(128), nullable=False, server_default=''), sa.Column('contact_phone', sa.String(64), nullable=False, server_default=''), sa.Column('tax_no', sa.String(64), nullable=False, server_default=''), sa.Column('settlement_terms', sa.Text(), nullable=False, server_default=''), sa.Column('supplier_status', sa.String(32), nullable=False, server_default='active'), sa.Column('strategic_supplier_flag', sa.String(16), nullable=False, server_default='false'), *_base_cols())
    op.create_table('supplier_evaluations', sa.Column('supplier_id', sa.String(64), nullable=False), sa.Column('evaluation_period', sa.String(32), nullable=False, server_default=''), sa.Column('price_score', sa.Float(), nullable=False, server_default='0'), sa.Column('delivery_score', sa.Float(), nullable=False, server_default='0'), sa.Column('quality_score', sa.Float(), nullable=False, server_default='0'), sa.Column('service_score', sa.Float(), nullable=False, server_default='0'), sa.Column('risk_score', sa.Float(), nullable=False, server_default='0'), sa.Column('qualification_score', sa.Float(), nullable=False, server_default='0'), sa.Column('strategic_score', sa.Float(), nullable=False, server_default='0'), sa.Column('total_score', sa.Float(), nullable=False, server_default='0'), sa.Column('risk_level', sa.String(32), nullable=False, server_default='medium'), sa.Column('cooperation_suggestion', sa.Text(), nullable=False, server_default=''), sa.Column('reviewer_user_id', sa.String(64), nullable=False, server_default='system'), *_base_cols())
    op.create_index(op.f('ix_supplier_evaluations_supplier_id'), 'supplier_evaluations', ['supplier_id'], unique=False)
    op.create_table('purchase_requests', sa.Column('applicant_user_id', sa.String(64), nullable=False, server_default=''), sa.Column('dept_id', sa.String(64), nullable=False, server_default=''), sa.Column('category_code', sa.String(64), nullable=False, server_default=''), sa.Column('demand_desc', sa.Text(), nullable=False, server_default=''), sa.Column('spec_doc_uri', sa.String(500), nullable=False, server_default=''), sa.Column('expected_quantity', sa.Integer(), nullable=False, server_default='0'), sa.Column('expected_delivery_date', sa.String(64), nullable=False, server_default=''), sa.Column('budget_amount', sa.Float(), nullable=False, server_default='0'), sa.Column('request_status', sa.String(32), nullable=False, server_default='draft'), *_base_cols())
    op.create_table('rfqs', sa.Column('pr_id', sa.String(64), nullable=False), sa.Column('rfq_code', sa.String(64), nullable=False, server_default=''), sa.Column('category_code', sa.String(64), nullable=False, server_default=''), sa.Column('structured_requirement_json', sa.Text(), nullable=False, server_default='{}'), sa.Column('invited_supplier_count', sa.Integer(), nullable=False, server_default='0'), sa.Column('rfq_doc_uri', sa.String(500), nullable=False, server_default=''), sa.Column('quote_deadline', sa.String(64), nullable=False, server_default=''), sa.Column('rfq_status', sa.String(32), nullable=False, server_default='draft'), sa.Column('owner_user_id', sa.String(64), nullable=False, server_default=''), *_base_cols())
    op.create_index(op.f('ix_rfqs_pr_id'), 'rfqs', ['pr_id'], unique=False)
    op.create_table('quotes', sa.Column('rfq_id', sa.String(64), nullable=False), sa.Column('supplier_id', sa.String(64), nullable=False), sa.Column('quote_doc_uri', sa.String(500), nullable=False, server_default=''), sa.Column('quote_total_amount_tax', sa.Float(), nullable=False, server_default='0'), sa.Column('quote_total_amount_no_tax', sa.Float(), nullable=False, server_default='0'), sa.Column('currency_code', sa.String(16), nullable=False, server_default='CNY'), sa.Column('payment_terms', sa.Text(), nullable=False, server_default=''), sa.Column('delivery_lead_time', sa.String(64), nullable=False, server_default=''), sa.Column('warranty_period', sa.String(64), nullable=False, server_default=''), sa.Column('service_terms', sa.Text(), nullable=False, server_default=''), sa.Column('technical_match_score', sa.Float(), nullable=False, server_default='0'), sa.Column('quote_risk_level', sa.String(32), nullable=False, server_default='medium'), sa.Column('parsed_json', sa.Text(), nullable=False, server_default='{}'), *_base_cols())
    op.create_index(op.f('ix_quotes_rfq_id'), 'quotes', ['rfq_id'], unique=False)
    op.create_index(op.f('ix_quotes_supplier_id'), 'quotes', ['supplier_id'], unique=False)
    op.create_table('knowledge_documents', sa.Column('doc_name', sa.String(255), nullable=False), sa.Column('doc_type', sa.String(64), nullable=False, server_default='document'), sa.Column('domain_type', sa.String(64), nullable=False, server_default='general'), sa.Column('source_system', sa.String(64), nullable=False, server_default='manual'), sa.Column('version_no', sa.String(32), nullable=False, server_default='v1'), sa.Column('owner_dept', sa.String(128), nullable=False, server_default=''), sa.Column('tags', sa.Text(), nullable=False, server_default='[]'), sa.Column('permission_scope', sa.String(128), nullable=False, server_default='internal'), sa.Column('vector_status', sa.String(32), nullable=False, server_default='pending'), sa.Column('effective_date', sa.String(32), nullable=False, server_default=''), sa.Column('expire_date', sa.String(32), nullable=False, server_default=''), sa.Column('quality_score', sa.String(16), nullable=False, server_default='0'), *_base_cols())
    op.create_table('audit_logs', sa.Column('module_name', sa.String(64), nullable=False, server_default='system'), sa.Column('action_name', sa.String(128), nullable=False, server_default=''), sa.Column('operator_id', sa.String(64), nullable=False, server_default='system'), sa.Column('target_type', sa.String(64), nullable=False, server_default=''), sa.Column('target_id', sa.String(64), nullable=False, server_default=''), sa.Column('result', sa.String(32), nullable=False, server_default='success'), sa.Column('detail', sa.Text(), nullable=False, server_default='{}'), *_base_cols())
    op.create_table('ai_task_executions', sa.Column('task_id', sa.String(128), nullable=False), sa.Column('scene', sa.String(64), nullable=False, server_default=''), sa.Column('agent_name', sa.String(128), nullable=False, server_default=''), sa.Column('provider', sa.String(64), nullable=False, server_default='mock'), sa.Column('operator_id', sa.String(64), nullable=False, server_default='system'), sa.Column('entity_id', sa.String(64), nullable=False, server_default=''), sa.Column('status', sa.String(32), nullable=False, server_default='completed'), sa.Column('summary', sa.Text(), nullable=False, server_default=''), sa.Column('recommendations', sa.Text(), nullable=False, server_default='[]'), sa.Column('evidence', sa.Text(), nullable=False, server_default='[]'), sa.Column('insights', sa.Text(), nullable=False, server_default='[]'), sa.Column('next_actions', sa.Text(), nullable=False, server_default='[]'), sa.Column('context', sa.Text(), nullable=False, server_default='{}'), sa.Column('raw_output', sa.Text(), nullable=False, server_default='{}'), *_base_cols(), sa.UniqueConstraint('task_id'))


def downgrade() -> None:
    op.drop_table('ai_task_executions')
    op.drop_table('audit_logs')
    op.drop_table('knowledge_documents')
    op.drop_index(op.f('ix_quotes_supplier_id'), table_name='quotes')
    op.drop_index(op.f('ix_quotes_rfq_id'), table_name='quotes')
    op.drop_table('quotes')
    op.drop_index(op.f('ix_rfqs_pr_id'), table_name='rfqs')
    op.drop_table('rfqs')
    op.drop_table('purchase_requests')
    op.drop_index(op.f('ix_supplier_evaluations_supplier_id'), table_name='supplier_evaluations')
    op.drop_table('supplier_evaluations')
    op.drop_table('suppliers')
    op.drop_table('proposal_projects')
    op.drop_index(op.f('ix_followup_records_lead_id'), table_name='followup_records')
    op.drop_table('followup_records')
