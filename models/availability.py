from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from core import Base

if TYPE_CHECKING:
    from models.user import User
    from models.event import Slot

class Unavailability(Base):
    __tablename__ = "unavailability"

    __table_args__ = (
        UniqueConstraint("user_id", "slot_id", name="uq_user_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete='CASCADE'))
    slot_id: Mapped[int] = mapped_column(ForeignKey("slot.id", ondelete='CASCADE'))

    user: Mapped["User"] = relationship(back_populates="unavailabilities")
    slot: Mapped["Slot"] = relationship(back_populates="unavailabilities")