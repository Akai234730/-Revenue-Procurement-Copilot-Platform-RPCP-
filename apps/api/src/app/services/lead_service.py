from app.services.mock_data import lead_list


class LeadDomainService:
    def list_leads(self) -> list[dict]:
        return lead_list()

    def get_lead_detail(self, lead_id: str) -> dict:
        lead = self.list_leads()[0].copy()
        lead.update(
            {
                'id': lead_id,
                'profileSummary': '客户数字化采购需求明确，具备较强商机转化信号。',
                'signals': ['制造业标杆客户', '存在明确采购流程痛点', '中高层关注效率改进'],
                'risks': ['竞品已接触', '项目预算审批节奏未知'],
            }
        )
        return lead
