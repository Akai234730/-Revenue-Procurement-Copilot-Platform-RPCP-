from sqlalchemy.orm import Session

from app.core.crypto import hash_password, verify_password
from app.models.identity import User
from app.repositories.base import BaseRepository
from app.schemas.identity import UserCreate


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BaseRepository(User, db)

    def list_users(self) -> list[User]:
        return self.repo.list_all()

    def get_user(self, user_id: str) -> User | None:
        return self.repo.get_by_id(user_id)

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, payload: UserCreate) -> User:
        return self.repo.create(
            username=payload.username,
            display_name=payload.display_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            dept_id=payload.dept_id,
            title=payload.title,
        )

    def authenticate(self, username: str, password: str) -> User | None:
        user = self.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
