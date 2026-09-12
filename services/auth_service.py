from sqlalchemy import select

from core import get_session
from models import User

def authenticate_user(club_id: int, name: str, password: str) -> User | None:
    with get_session() as session:
        stmt = select(User).where(User.name == name, User.club_id == club_id)
        user = session.scalars(stmt).first()

        if not user:
            raise ValueError("error_user_does_not_exist")

        if not user.is_active or not user.password_hash:
            raise ValueError("error_account_not_activated")

        if not user.check_password(password=password):
            raise ValueError("error_invalid_password")

        session.expunge(user)
        return user

def update_password(user_id: int, new_password: str) -> None:
    with get_session() as session:
        user = session.get(User, user_id)

        if not user:
            raise ValueError("error_user_does_not_exist")
        
        if user.password_hash and user.check_password(password=new_password):
            raise ValueError("error_password_already_used")

        user.password = new_password
        session.commit()