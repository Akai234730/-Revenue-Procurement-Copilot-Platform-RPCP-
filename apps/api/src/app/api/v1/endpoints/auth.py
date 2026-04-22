from fastapi import APIRouter, Depends
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import create_access_token, get_current_user, require_roles
from app.db.session import get_db
from app.models.identity import User
from app.schemas.common import APIResponse
from app.schemas.identity import UserCreate, UserLogin
from app.services.user_service import UserService

router = APIRouter()


def _raise_db_unavailable(exc: Exception) -> None:
    raise AppError(code="DB_CONNECTION_FAILED", message="数据库连接失败，请检查 PostgreSQL 是否启动且配置正确", status_code=503) from exc


@router.post("/login", response_model=APIResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> APIResponse:
    service = UserService(db)
    try:
        user = service.authenticate(payload.username, payload.password)
    except OperationalError as exc:
        _raise_db_unavailable(exc)
    except SQLAlchemyError as exc:
        raise AppError(code="DB_QUERY_FAILED", message="数据库查询失败，请稍后重试", status_code=503) from exc
    if not user:
        raise AppError(code="AUTH_INVALID_CREDENTIALS", message="用户名或密码错误", status_code=401)
    access_token = create_access_token(user.id, {"roles": [role.code for role in user.roles]})
    return APIResponse(
        data={
            "accessToken": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.display_name,
                "roles": [role.code for role in user.roles],
            },
        }
    )


@router.get("/me", response_model=APIResponse)
def me(current_user: User = Depends(get_current_user)) -> APIResponse:
    return APIResponse(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "display_name": current_user.display_name,
            "email": current_user.email,
            "roles": [role.code for role in current_user.roles],
        }
    )


@router.post("/users", response_model=APIResponse)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["admin"])),
) -> APIResponse:
    service = UserService(db)
    try:
        user = service.create_user(payload)
    except OperationalError as exc:
        _raise_db_unavailable(exc)
    except SQLAlchemyError as exc:
        raise AppError(code="DB_QUERY_FAILED", message="数据库写入失败，请稍后重试", status_code=503) from exc
    return APIResponse(
        data={
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "email": user.email,
        }
    )


@router.get("/users", response_model=APIResponse)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["admin"])),
) -> APIResponse:
    service = UserService(db)
    try:
        users = service.list_users()
    except OperationalError as exc:
        _raise_db_unavailable(exc)
    except SQLAlchemyError as exc:
        raise AppError(code="DB_QUERY_FAILED", message="数据库查询失败，请稍后重试", status_code=503) from exc
    return APIResponse(
        data=[
            {
                "id": item.id,
                "username": item.username,
                "display_name": item.display_name,
                "email": item.email,
                "status": item.status,
                "dept_id": item.dept_id,
                "title": item.title,
                "roles": [role.code for role in item.roles],
            }
            for item in users
        ]
    )
