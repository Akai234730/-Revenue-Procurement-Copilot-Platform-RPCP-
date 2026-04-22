export type LeadRecord = {
  id: string;
  company_name: string;
  contact_name: string;
  contact_title?: string;
  phone?: string;
  email?: string;
  industry_name: string;
  source_channel: string;
  company_size?: string;
  region_code?: string;
  demand_summary?: string;
  project_stage?: string;
  ai_lead_score: number;
  ai_maturity_level: string;
  ai_priority_level: string;
  ai_next_action: string;
  crm_sync_status: string;
  lead_status: string;
  invalid_reason?: string;
};

export type ProposalRecord = {
  id: string;
  project_name: string;
  industry_code: string;
  bid_type: string;
  proposal_status: string;
  risk_level: string;
  approval_status: string;
  owner_user_id: string;
};

export type SupplierRecord = {
  id: string;
  supplier_name: string;
  supplier_code?: string;
  supplier_category: string;
  qualification_level: string;
  supplier_status: string;
  region_code: string;
  major_products?: string;
  contact_person?: string;
  contact_phone?: string;
  settlement_terms?: string;
  strategic_supplier_flag?: string | boolean;
};

export type SupplierEvaluationRecord = {
  id: string;
  supplier_id: string;
  evaluation_period: string;
  total_score: number;
  risk_level: string;
  cooperation_suggestion: string;
};

export type QuoteRecord = {
  id: string;
  rfq_id: string;
  supplier_id: string;
  quote_total_amount_tax: number;
  quote_total_amount_no_tax: number;
  currency_code: string;
  quote_risk_level: string;
};

export type RFQRecord = {
  id: string;
  pr_id: string;
  rfq_code: string;
  category_code: string;
  invited_supplier_count: number;
  quote_deadline: string;
  rfq_status: string;
};

export type KnowledgeDocumentRecord = {
  id: string;
  doc_name: string;
  domain_type: string;
  source_system: string;
  permission_scope: string;
  vector_status: string;
};

export type RuntimeStatus = {
  service: string;
  environment: string;
  version: string;
  status: string;
  timestamp: string;
  provider: string;
  model_name: string;
  database: string;
  integrations: Record<string, number>;
};

export type MetricsOverview = {
  request_count: number;
  error_count: number;
  degraded_count: number;
  ai_task_count: number;
  integration_task_count: number;
  audit_log_count: number;
};

export type IntegrationStatus = {
  system_code: string;
  system_name: string;
  enabled: boolean;
  status: string;
  last_sync_at: string;
  owner: string;
  detail: Record<string, unknown>;
};

export type UnifiedTaskResult = {
  task_id: string;
  task_type: string;
  source_system: string;
  target_system: string;
  status: string;
  message: string;
  next_actions: string[];
  created_at: string;
};

export type AuditLogRecord = {
  id: string;
  module_name: string;
  action_name: string;
  operator_id: string;
  target_type: string;
  target_id: string;
  result: string;
  detail: string;
  created_at: string;
};

export type AIExecutionHistoryItem = {
  task_id: string;
  scene: string;
  agent_name: string;
  provider: string;
  operator_id: string;
  entity_id: string;
  status: string;
  summary: string;
  created_at: string;
  recommendations: string[];
  evidence: string[];
};

export type AIExecutionDetail = AIExecutionHistoryItem & {
  insights: Array<{ title: string; content: string; confidence: number }>;
  next_actions: string[];
  context: Record<string, unknown>;
  raw_output: Record<string, unknown>;
  error_message?: string;
  duration_ms?: number;
  completed_at?: string | null;
};

export type AIExecutionResult = {
  task_id: string;
  scene: string;
  agent_name: string;
  provider: string;
  status: string;
  summary: string;
  recommendations: string[];
  evidence: string[];
  next_actions: string[];
  insights: Array<{
    title: string;
    content: string;
    confidence: number;
  }>;
  raw_output: Record<string, unknown>;
  context: Record<string, unknown>;
  degraded: boolean;
  error_message: string;
  created_at: string | null;
  completed_at: string | null;
  duration_ms: number;
};

export type DashboardOverview = {
  metrics: {
    todoCount: number;
    urgentCount: number;
    approvalCount: number;
    riskCount: number;
    leadTrend: number[];
    proposalTrend: number[];
    supplierRiskDistribution: number[];
    procurementSavingsTrend: number[];
  };
  topLeads: LeadRecord[];
  pendingProposals: ProposalRecord[];
  supplierEvaluations: SupplierEvaluationRecord[];
  activeQuotes: QuoteRecord[];
};
