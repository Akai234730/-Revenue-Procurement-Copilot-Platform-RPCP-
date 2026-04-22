from app.services.mock_data import purchase_request_list, quote_list, rfq_list


class ProcurementDomainService:
    def list_purchase_requests(self) -> list[dict]:
        return purchase_request_list()

    def list_rfqs(self) -> list[dict]:
        return rfq_list()

    def list_quotes(self) -> list[dict]:
        return quote_list()
