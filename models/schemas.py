from datetime import datetime
from typing import Optional
from enum import Enum
from werkzeug.security import check_password_hash, generate_password_hash

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from core import Base

class Role(Enum):
    PLAYER = "player"
    STAFF = "staff"
    CAPTAIN = "captain"

class EventType(Enum):
    GAME = "game"
    MEETING = "meeting"
    FRIENDLY_MATCH = "friendly_match"
    TRAINING = "training"
    OTHER = "other"

class Club(Base):
    ...

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str] = mapped_column()

    roles: Mapped[list[Role]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    absences: Mapped[list["Absence"]] = relationship("Abscence", back_populates="user", cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError("Password is not an accessible property.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User(id={self.id}, name={self.name})"

class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), ondelete="CASCADE")
    role: Mapped[Role] = mapped_column(Role)

    user: Mapped["User"] = relationship("User", back_populates="roles")

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

class Absence(Base):
    ...