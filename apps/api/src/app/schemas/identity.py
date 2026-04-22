from pydantic import BaseModel, EmailStr


class UserSummary(BaseModel):
    id: str
    username: str
    display_name: str
    email: str
    status: str
    dept_id: str
    title: str
    roles: list[str] = []


class UserCreate(BaseModel):
    username: str
    display_name: str
    email: EmailStr
    password: str
    dept_id: str = ""
    title: str = ""


class UserLogin(BaseModel):
    username: str
    password: str


class RoleSummary(BaseModel):
    id: str
    name: str
    code: str
    description: str
