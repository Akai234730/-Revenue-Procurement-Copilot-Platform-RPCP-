from app.services.mock_data import proposal_list


class ProposalDomainService:
    def list_projects(self) -> list[dict]:
        return proposal_list()
