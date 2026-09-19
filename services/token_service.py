from datetime import datetime, timedelta

from sqlalchemy import select

from core import get_session
from models import Token, TokenType, User, Event


def create_activation_token(user_id: int, days_valid: int = 14) -> Token:
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise ValueError("error_user_does_not_exist")

        stmt = select(Token).where(Token.user_id == user_id, Token.type == TokenType.ACTIVATION)
        old_tokens = session.scalars(stmt).all()
        for old in old_tokens:
            session.delete(old)

        token = Token(
            type=TokenType.ACTIVATION,
            user_id=user_id,
            expires_at=datetime.now() + timedelta(days=days_valid),
        )

        session.add(token)
        session.commit()
        session.refresh(token)
        session.expunge(token)
        return token

def create_event_token(event_id: int) -> Token:
    with get_session() as session:
        event = session.get(Event, event_id)
        if not event:
            raise ValueError("error_event_does_not_exist")
        
        token = Token(
            type=TokenType.EVENT,
            event_id=event_id,
            expires_at=event.response_deadline
        )

        session.add(token)
        session.commit()
        session.refresh(token)
        session.expunge(token)
        return token

def get_valid_token(value: str, token_type: TokenType) -> Token | None:
    with get_session() as session:
        stmt = select(Token).where(Token.value == value, Token.type == token_type)
        token = session.scalars(stmt).first()
        if not token:
            return None
        if token.expires_at and token.expires_at < datetime.now():
            return None
        session.expunge(token)
        return token

def get_event_token(event_id: int) -> Token | None:
    with get_session() as session:
        stmt = select(Token).where(Token.event_id == event_id, Token.type == TokenType.EVENT)
        token = session.scalars(stmt).first()
        if token:
            session.expunge(token)
        return token

def has_pending_activation_token(user_id: int) -> bool:
    with get_session() as session:
        stmt = select(Token).where(Token.user_id == user_id, Token.type == TokenType.ACTIVATION)
        token = session.scalars(stmt).first()
        if not token:
            return False
        if token.expires_at and token.expires_at < datetime.utcnow():
            return False
        return True

def activate_account(token_value: str, new_password: str) -> User:
    with get_session() as session:
        stmt = select(Token).where(Token.value == token_value, Token.type == TokenType.ACTIVATION)
        token = session.scalars(stmt).first()

        if not token:
            raise ValueError("error_token_not_found")
        if token.expires_at and token.expires_at < datetime.now():
            raise ValueError("error_token_expired")

        user = session.get(User, token.user_id)
        if not user:
            raise ValueError("error_user_does_not_exist")

        user.password = new_password
        user.is_active = True

        token.used_at = datetime.now()

        session.commit()
        session.refresh(user)
        session.expunge(user)
        return user