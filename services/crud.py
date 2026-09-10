from sqlalchemy import select

from core import get_session
from models import User, Club

def create_user(name: str, password: str, club_id: int, email:str | None = None) -> User | None:
    with get_session() as session:
        stmt = select(User).where(User.name == name, User.club_id == club_id)
        user = session.scalars(stmt).first()

        if user:
            raise ValueError("error_user_already_exists")

        user = User(name=name, password=password, email=email, club_id=club_id)

        session.add(user)
        session.commit()

        session.refresh(user)
        session.expunge(user)

        return user

def create_club(name: str) -> Club | None:
    with get_session() as session:
        stmt = select(Club).where(Club.name == name)
        club = session.scalars(stmt).first()

        if club:
            raise ValueError("error_club_already_exists")

        club = Club(name=name)

        session.add(club)
        session.commit()

        session.refresh(club)
        session.expunge(club)

        return club

def delete_user(user_id: int, password: str) -> bool:
    with get_session() as session:
        user = session.get(User, user_id)

        if not user:
            raise ValueError("error_user_does_not_exist")

        if not user.check_password(password=password):
            raise ValueError("error_invalid_password")

        session.delete(user)
        session.commit()

        return True

def delete_user(club_id: int) -> bool:
    with get_session() as session:
        club = session.get(Club, club_id)

        if not club:
            raise ValueError("error_club_does_not_exist")

        session.delete(club)
        session.commit()

        return True

def update_user_name(user_id: int, new_name: str) -> None:
    with get_session() as session:
        stmt = select(User).where(User.name == new_name)
        existing_user = session.scalar(stmt)

        if existing_user and existing_user.id != user_id:
            raise ValueError("error_name_already_exists")

        user = session.get(User, user_id)
        if not user:
            raise ValueError("error_user_no_longer_exists")
        
        user.name = new_name
        session.commit()

def update_club_name(club_id: int, new_name: str) -> None:
    with get_session() as session:
        stmt = select(Club).where(Club.name == new_name)
        existing_club = session.scalar(stmt)

        if existing_club and existing_club.id != club_id:
            raise ValueError("error_club_already_exists")

        club = session.get(Club, club_id)
        if not club:
            raise ValueError("error_club_no_longer_exists")
        
        club.name = new_name
        session.commit()

def get_user_by_id(user_id: int) -> User | None:
    if not user_id:
        return None

    with get_session() as session:
        return session.get(User, user_id)

def get_club_by_id(club_id: int) -> Club | None:
    if not club_id:
        return None

    with get_session() as session:
        return session.get(Club, club_id)

def get_user_by_club_name(name: str, club_id: int) -> User | None:
    with get_session() as session:
        stmt = select(User).where(User.name == name, User.club_id == club_id)
        return session.scalar(stmt)

def get_club_by_name(name: str)) -> Club | None:
    with get_session() as session:
        stmt = select(User).where(Club.name == name)
        return session.scalar(stmt)