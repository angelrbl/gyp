from sqlalchemy import select

from core import get_session
from models import RoleType, UserRole

def set_user_roles(user_id: int, roles: list[RoleType]) -> None:
    with get_session() as session:
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        existing = session.scalars(stmt).all()

        for role in existing:
            session.delete(role)

        for role in roles:
            session.add(UserRole(user_id=user_id, role=role))

        session.commit()


def get_user_roles(user_id: int) -> list[RoleType]:
    with get_session() as session:
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        roles = session.scalars(stmt).all()

        return [role.role for role in roles]