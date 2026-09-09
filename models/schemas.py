from datetime import datetime
from typing import Optional
from enum import Enum
from werkzeug.security import check_password_hash, generate_password_hash

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from core import Base

class RoleType(Enum):
    PLAYER = "player"
    STAFF = "staff"
    CAPTAIN = "captain"
    IT_DIRECTOR = "it_director"

class EventType(Enum):
    GAME = "game"
    MEETING = "meeting"
    FRIENDLY_MATCH = "friendly_match"
    TRAINING = "training"
    OTHER = "other"

class Club(Base):
    __tablename__ = "club"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    squad: Mapped[list["User"]] = relationship(back_populates="club", cascade="all, delete-orphan")
    events: Mapped[list["Event"]] = relationship(back_populates="club", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column()

    club_id: Mapped[int] = mapped_column(ForeignKey("club.id"))

    club: Mapped["Club"] = relationship(back_populates="squad")
    roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    absences: Mapped[list["Absence"]] = relationship("Absence", back_populates="user", cascade="all, delete-orphan")

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
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    role: Mapped["RoleType"] = mapped_column()

    user: Mapped["User"] = relationship("User", back_populates="roles")

class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("club.id", ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(255))

    event_type: Mapped["EventType"] = mapped_column()

    rival_name: Mapped[Optional[str]] = mapped_column(String(100))
    rival_club_id: Mapped[Optional[int]] = mapped_column(ForeignKey("club.id"))

    start_range: Mapped[datetime] = mapped_column(DateTime)
    end_range: Mapped[datetime] = mapped_column(DateTime)
    time_span: Mapped[int] = mapped_column(default=60)

    final_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    club: Mapped["Club"] = relationship("Club", foreign_keys=[club_id], back_populates="events")
    rival_club: Mapped[Optional["Club"]] = relationship("Club", foreign_keys=[rival_club_id])
    absences: Mapped[list["Absence"]] = relationship(back_populates="event", cascade="all, delete-orphan")

class Absence(Base):
    __tablename__ = "absence"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete='CASCADE'))
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id", ondelete='CASCADE'))

    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="absences")
    event: Mapped["Event"] = relationship(back_populates="absences")