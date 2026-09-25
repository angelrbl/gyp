from datetime import date, time, datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, ForeignKey, Date, Time, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from core import Base

from models.club import Club
from models.availability import Unavailability

class EventStatus(str, Enum):
    OPEN = "open"
    CONFIRMED = "confirmed" 
    PAST = "past" 

class EventType(str, Enum):
    GAME = "partido"
    MEETING = "reunión"
    FRIENDLY_MATCH = "partido_amistoso"
    TRAINING = "entrenamiento"
    OTHER = "otro"

class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("club.id", ondelete='CASCADE'))

    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(255))

    event_type: Mapped["EventType"] = mapped_column()
    status: Mapped["EventStatus"] = mapped_column(default=EventStatus.OPEN)
    response_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)

    opponent_name: Mapped[Optional[str]] = mapped_column(String(100))
    opponent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("club.id"))

    slots: Mapped[list["Slot"]] = relationship(
        "Slot",
        back_populates="event",
        foreign_keys="[Slot.event_id]",
        cascade="all, delete-orphan",
    )
    confirmed_slot_id: Mapped[Optional[int]] = mapped_column(ForeignKey("slot.id"), default=None)
    confirmed_slot: Mapped[Optional["Slot"]] = relationship("Slot", foreign_keys=[confirmed_slot_id])

    club: Mapped["Club"] = relationship("Club", foreign_keys=[club_id], back_populates="events")
    opponent: Mapped[Optional["Club"]] = relationship("Club", foreign_keys=[opponent_id])

class Slot(Base):
    __tablename__ = "slot"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id", ondelete='CASCADE'))

    day: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    event: Mapped["Event"] = relationship("Event", back_populates="slots", foreign_keys=[event_id])
    unavailabilities: Mapped[list["Unavailability"]] = relationship(back_populates="slot", cascade="all, delete-orphan")