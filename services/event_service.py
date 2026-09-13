from datetime import date, time, datetime

from sqlalchemy import select

from core import get_session
from models import Event, EventStatus, EventType, Slot

from services.club_service import get_club_by_name

def create_event(
    club_id: int,
    title: str,
    event_type: EventType,
    slots: list[tuple[date, time, time]],
    response_deadline: datetime | None = None,
    description: str | None = None,
    opponent_name: str | None = None,
) -> Event:
    if not slots:
        raise ValueError("error_event_needs_at_least_one_slot")

    with get_session() as session:
        opponent_club = get_club_by_name(name=opponent_name)

        event = Event(
            club_id=club_id,
            title=title,
            event_type=event_type,
            response_deadline=response_deadline,
            description=description,
            opponent_name=opponent_name,
            opponent=opponent_club
        )

        session.add(event)
        session.flush()

        for day, start, end in slots:
            session.add(Slot(event_id=event.id, day=day, start_time=start, end_time=end))

        session.commit()
        session.refresh(event)
        session.expunge(event)
        return event

def list_events_for_club(club_id: int) -> list[Event]:
    with get_session() as session:
        stmt = select(Event).where(Event.club_id == club_id).order_by(Event.id.desc())
        events = session.scalars(stmt).all()

        for e in events:
            session.expunge(e)
        return list(events)

def get_event_by_id(event_id: int) -> Event | None:
    with get_session() as session:
        event = session.get(Event, event_id)
        if event:
            session.expunge(event)
        return event

def get_event_slots(event_id: int) -> list[Slot]:
    with get_session() as session:
        stmt = select(Slot).where(Slot.event_id == event_id).order_by(Slot.day, Slot.start_time)
        slots = session.scalars(stmt).all()

        for s in slots:
            session.expunge(s)
        return list(slots)

def get_slot_by_id(slot_id: int) -> Slot | None:
    with get_session() as session:
        slot = session.get(Slot, slot_id)
        if slot:
            session.expunge(slot)
        return slot

def confirm_slot(event_id: int, slot_id: int) -> None:
    with get_session() as session:
        event = session.get(Event, event_id)
        if not event:
            raise ValueError("error_event_does_not_exist")

        slot = session.get(Slot, slot_id)
        if not slot or slot.event_id != event_id:
            raise ValueError("error_slot_does_not_belong_to_event")

        event.confirmed_slot_id = slot_id
        event.status = EventStatus.CONFIRMED
        session.commit()