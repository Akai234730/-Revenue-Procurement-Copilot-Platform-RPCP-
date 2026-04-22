from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def list_all(self) -> list[ModelType]:
        return list(self.db.query(self.model).all())

    def get_by_id(self, item_id: str) -> ModelType | None:
        return self.db.query(self.model).filter(self.model.id == item_id).first()

    def create(self, **kwargs) -> ModelType:
        item = self.model(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
