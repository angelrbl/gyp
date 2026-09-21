from datetime import date

from nicegui import ui

from models import EventStatus, TokenType
from services.availability_service import get_user_unavailable_slot_ids, set_unavailability
from services.event_service import get_event_by_id, get_event_slots, get_slot_by_id
from services.token_service import get_valid_token
from services.user_service import list_users_for_club

from views.layout import frame

DAYS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


@ui.page("/e/{token_value}")
def event_page(token_value: str):
    with frame(navigation_title="Evento"):
        token = get_valid_token(token_value, TokenType.EVENT)
        if not token:
            ui.label("¡Qué lastima!").classes("text-3xl font-black text-negative")
            ui.label("Este enlace no es válido o ha caducado.").classes('text-xl font-bold text-slate-700')
            return

        event = get_event_by_id(token.event_id)

        if event.status == EventStatus.OPEN:
            render_open_event(event)
        else:
            render_confirmed_event(event)


def render_confirmed_event(event) -> None:
    slot = get_slot_by_id(event.confirmed_slot_id) if event.confirmed_slot_id else None

    with ui.column().classes("w-full max-w-lg mx-auto gap-1"):
        ui.label(event.title).classes("text-lg font-bold text-dark")
        if event.opponent_name:
            ui.label(f"vs. {event.opponent_name}").classes("text-dark text-sm")

        if event.status == EventStatus.PAST:
            ui.label("Este evento ya ha pasado.").classes("mt-4 text-sm text-gray-500")
        elif slot:
            with ui.column().classes("gap-1 mt-4 p-4 bg-primary/10 rounded-lg"):
                ui.label("Horario confirmado").classes("text-primary text-xs font-semibold")
                ui.label(f"{DAYS[slot.day.weekday()]} {slot.day:%d/%m} · {slot.start_time:%H:%M}").classes(
                    "text-dark text-base font-bold"
                )
            # Antes: on_click navegaba a "None" (el import de google_calendar_url
            # se había perdido al adaptar el archivo) — el botón no hacía nada.
            ui.button(
                "Añadir a mi calendario",
                on_click=lambda: ui.navigate.to(None, new_tab=True),
            ).props('unelevated').classes("mt-4 w-full bg-primary text-white rounded-lg")
        else:
            ui.label("Este evento está confirmado, pero falta el horario.").classes("mt-4 text-sm text-gray-500")


def render_open_event(event) -> None:
    slots = get_event_slots(event.id)
    members = list_users_for_club(event.club_id)

    all_days = sorted({slot.day for slot in slots})
    all_times = sorted({slot.start_time for slot in slots})
    slot_lookup = {(slot.day, slot.start_time): slot for slot in slots}

    state = {"user_id": None}
    slot_buttons: dict[int, ui.button] = {}
    selected_slots: dict[int, bool] = {}
    count_label_ref: dict[str, ui.label] = {}

    BASE_CLASSES = "h-10 w-full min-w-0 rounded-md border text-xs font-medium transition-colors"
    UNSELECTED = "bg-white text-dark border-gray-300"
    SELECTED = "bg-primary text-white border-primary"

    def style_slot_button(slot_id: int) -> None:
        btn = slot_buttons[slot_id]
        if selected_slots[slot_id]:
            btn.classes(remove=UNSELECTED, add=SELECTED)
        else:
            btn.classes(remove=SELECTED, add=UNSELECTED)

    def toggle_slot(slot_id: int) -> None:
        selected_slots[slot_id] = not selected_slots[slot_id]
        style_slot_button(slot_id)
        update_count()

    def update_count() -> None:
        if "label" not in count_label_ref:
            return
        n = sum(1 for v in selected_slots.values() if v)
        if n:
            count_label_ref["label"].text = f"{n} franja{'s' if n != 1 else ''} marcada{'s' if n != 1 else ''}"
        else:
            count_label_ref["label"].text = "Ninguna franja marcada"

    def save() -> None:
        if not state["user_id"]:
            ui.notify("Elige tu nombre primero.", type="negative")
            return
        chosen = [sid for sid, is_selected in selected_slots.items() if is_selected]
        set_unavailability(user_id=state["user_id"], event_id=event.id, slot_ids=chosen)
        ui.notify("¡Guardado!", type="positive")

    @ui.refreshable
    def render_grid() -> None:
        slot_buttons.clear()
        selected_slots.clear()
        count_label_ref.pop("label", None)

        if not state["user_id"]:
            ui.label("Elige tu nombre arriba para ver y marcar las franjas.").classes("text-sm text-gray-500 mt-4")
            return

        my_unavailable = get_user_unavailable_slot_ids(state["user_id"], event.id)
        for slot in slots:
            selected_slots[slot.id] = slot.id in my_unavailable

        with ui.row().classes("items-start gap-2 mt-3 p-3 bg-primary/10 rounded-lg no-wrap"):
            ui.icon("warning").classes("text-primary text-base flex-shrink-0")
            ui.label("Marca solo las franjas en las que NO puedes asistir.").classes(
                "text-primary text-xs leading-relaxed"
            )

        if not slots:
            ui.label("Este evento no tiene franjas candidatas todavía.").classes("mt-4 text-sm text-gray-500")
            return

        # Rejilla tipo calendario: filas = horas, columnas = días. Como todas
        # las franjas de un evento comparten ventana y duración, las horas
        # coinciden entre días -> se puede alinear en una tabla de verdad.
        # overflow-x-auto: en móvil, con muchos días, se desliza en vez de
        # apretujarse ilegible.
        with ui.element("div").classes("w-full overflow-x-auto mt-4"):
            grid_style = f"grid-template-columns: 48px repeat({len(all_days)}, minmax(52px, 1fr));"
            with ui.element("div").classes("grid gap-1").style(grid_style):
                ui.element("div")  # esquina vacía
                for day in all_days:
                    with ui.column().classes("items-center gap-0"):
                        ui.label(DAYS[day.weekday()][:3].capitalize()).classes("text-xs font-semibold text-dark")
                        ui.label(f"{day:%d/%m}").classes("text-[10px] text-gray-500")

                for t in all_times:
                    ui.label(f"{t:%H:%M}").classes("text-xs text-gray-500 flex items-center")
                    for day in all_days:
                        slot = slot_lookup.get((day, t))
                        if slot is None:
                            ui.element("div")  # ese día no tiene franja a esta hora
                            continue
                        btn = (
                            ui.button(on_click=lambda sid=slot.id: toggle_slot(sid))
                            .props(f'unelevated dense aria-label="{DAYS[day.weekday()]} {day:%d/%m} {t:%H:%M}"')
                            .classes(f"{BASE_CLASSES} {UNSELECTED}")
                        )
                        slot_buttons[slot.id] = btn
                        style_slot_button(slot.id)

        with ui.row().classes("items-center justify-between w-full no-wrap mt-4"):
            count_label_ref["label"] = ui.label("").classes("text-gray-500 text-xs")
            ui.button("Guardar disponibilidad", on_click=save).props("unelevated").classes(
                "bg-primary text-white rounded-lg"
            )
        update_count()

    def on_pick(e) -> None:
        state["user_id"] = e.value
        render_grid.refresh()

    with ui.column().classes("w-full max-w-lg mx-auto gap-1"):
        ui.label(event.title).classes("text-lg font-bold text-dark")
        if event.opponent_name:
            ui.label(f"vs. {event.opponent_name}").classes("text-dark text-sm")

        if not members:
            ui.label("Todavía no hay jugadores dados de alta en el club.").classes("mt-4 text-sm text-gray-500")
            return

        ui.select(
            {m.id: m.name for m in members},
            label="¿Quién eres?",
            with_input=True,
            on_change=on_pick,
        ).classes("w-full mt-3")

        render_grid()