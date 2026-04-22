from datetime import datetime

from pydantic import BaseModel, ConfigDict


class APIResponse(BaseModel):
    code: str = "0"
    message: str = "success"
    request_id: str = "local-dev"
    data: object | None = None


class TimestampSchema(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
