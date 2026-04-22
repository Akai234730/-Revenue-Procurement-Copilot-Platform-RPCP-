from app.services.mock_data import supplier_evaluation_list, supplier_list


class SupplierDomainService:
    def list_suppliers(self) -> list[dict]:
        return supplier_list()

    def list_evaluations(self) -> list[dict]:
        return supplier_evaluation_list()
