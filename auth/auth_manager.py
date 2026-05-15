import bcrypt
from database.database import get_session
from database.models import User


class AuthManager:
    _current_user: User | None = None

    @classmethod
    def login(cls, username: str, password: str) -> tuple[bool, str]:
        db = get_session()
        try:
            user = db.query(User).filter_by(username=username, is_active=True).first()
            if not user:
                return False, "User not found."
            if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                return False, "Incorrect password."
            cls._current_user = user
            db.expunge(user)
            return True, "Login successful."
        finally:
            db.close()

    @classmethod
    def logout(cls):
        cls._current_user = None

    @classmethod
    def current_user(cls) -> User | None:
        return cls._current_user

    @classmethod
    def is_admin(cls) -> bool:
        return cls._current_user is not None and cls._current_user.role == "admin"

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
