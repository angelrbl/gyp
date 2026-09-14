from sqlalchemy import select

from core import get_session
from models import Club

def create_club(name: str) -> Club:
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

def delete_club(club_id: int) -> bool:
    with get_session() as session:
        club = session.get(Club, club_id)

        if not club:
            raise ValueError("error_club_does_not_exist")

        session.delete(club)
        session.commit()

        return True

def update_club_name(club_id: int, new_name: str) -> None:
    with get_session() as session:
        stmt = select(Club).where(Club.name == new_name)
        existing_club = session.scalars(stmt).first()

        if existing_club and existing_club.id != club_id:
            raise ValueError("error_club_already_exists")

        club = session.get(Club, club_id)
        if not club:
            raise ValueError("error_club_no_longer_exists")
        
        club.name = new_name
        session.commit()

def get_club_by_id(club_id: int) -> Club | None:
    if not club_id:
        return None

    with get_session() as session:
        club = session.get(Club, club_id)
        if club:
            session.expunge(club)
        return club

def get_club_by_name(name: str) -> Club | None:
    with get_session() as session:
        stmt = select(Club).where(Club.name == name)
        club = session.scalars(stmt).first()
        if club:
            session.expunge(club)
        return club

def get_only_club() -> Club | None:
    with get_session() as session:
        club = session.scalars(select(Club)).first()
        if club:
            session.expunge(club)
        return club

def any_club_exists() -> bool:
    with get_session() as session:
        return session.scalars(select(Club)).first() is not None