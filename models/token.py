from enum import Enum
from uuid import uuid4
from typing import Optional
from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped

from core import Base

class TokenType(str, Enum):
    ACTIVATION = "activation"
    EVENT = "event"

class Token(Base):
    __tablename__ = "token"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(String(50), default=lambda: uuid4().hex, unique=True)
    type: Mapped["TokenType"] = mapped_column()

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), default=None)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id", ondelete="CASCADE"))

    event: Mapped["Event"] = relationship("Event", back_populates="tokens")

    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)