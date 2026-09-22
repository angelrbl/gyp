from datetime import date, timedelta

from nicegui import ui

from models import Club, EventStatus
from services.availability_service import unavailability_counts_by_slot
from services.event_service import (
    confirm_slot,
    delete_event,
    get_event_by_id,
    get_event_slots,
    list_events_for_club,
)
from services.token_service import get_event_token
from services.user_service import list_users_for_club
from views.layout import APP_BASE_URL
from views.theme import mix_color

DIAS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

STATUS_BADGE = {
    EventStatus.OPEN: ("Abierto", "bg-amber-100 text-amber-700"),
    EventStatus.CONFIRMED: ("Confirmado", "bg-green-100 text-green-700"),
    EventStatus.PAST: ("Pasado", "bg-gray-200 text-gray-600"),
}


def handle_confirm_slot(event_id: int, slot_id: int, dialog) -> None:
    confirm_slot(event_id, slot_id)
    dialog.close()
    ui.notify("Horario confirmado", type="positive")
    ui.navigate.reload()


def confirm_delete_event(event_id: int, parent_dialog=None) -> None:
    """Pide confirmación antes de borrar un evento. Si se llama desde el
    diálogo de detalle, `parent_dialog` se cierra también al confirmar."""

    def do_delete() -> None:
        delete_event(event_id)
        confirm_dialog.close()
        if parent_dialog:
            parent_dialog.close()
        ui.notify("Evento eliminado", type="positive")
        ui.navigate.reload()

    with ui.dialog() as confirm_dialog, ui.card().classes('w-full max-w-sm p-5 gap-3 rounded-2xl'):
        ui.label('¿Eliminar este evento?').classes('text-base font-bold text-gray-900')
        ui.label(
            'Esta acción no se puede deshacer y se perderán las respuestas de disponibilidad asociadas.'
        ).classes('text-sm text-gray-500')
        with ui.row().classes('w-full justify-end gap-2 mt-2'):
            ui.button('Cancelar', on_click=confirm_dialog.close).props('flat no-caps').classes('text-gray-600')
            ui.button('Eliminar', on_click=do_delete).props('unelevated no-caps').classes(
                'bg-red-600 text-white rounded-lg'
            )
    confirm_dialog.open()


def open_event_detail(event_id: int) -> None:
    event = get_event_by_id(event_id)
    slots = get_event_slots(event_id)
    token = get_event_token(event_id)
    total_users = len(list_users_for_club(event.club_id))
    baja_counts = unavailability_counts_by_slot(event_id)
    link = f"{APP_BASE_URL}/e/{token.value}" if token else ""
    is_open = event.status == EventStatus.OPEN

    all_days = sorted({slot.day for slot in slots})
    all_times = sorted({slot.start_time for slot in slots})
    slot_lookup = {(slot.day, slot.start_time): slot for slot in slots}

    best_slot_id = min(baja_counts, key=baja_counts.get) if baja_counts else None

    def week_start(d: date) -> date:
        return d - timedelta(days=d.weekday())

    days_by_week: dict[date, list[date]] = {}
    for day in all_days:
        days_by_week.setdefault(week_start(day), []).append(day)
    week_starts = sorted(days_by_week.keys())

    default_week_index = 0
    best_slot = next((s for s in slots if s.id == best_slot_id), None)
    if best_slot and week_start(best_slot.day) in days_by_week:
        default_week_index = week_starts.index(week_start(best_slot.day))

    state = {"week_index": default_week_index}

    def change_week(delta: int) -> None:
        new_index = state["week_index"] + delta
        if 0 <= new_index < len(week_starts):
            state["week_index"] = new_index
            render_grid.refresh()

    with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl p-5 gap-3 rounded-2xl'):
        with ui.row().classes('w-full justify-between items-start no-wrap'):
            with ui.column().classes('gap-0'):
                ui.label(event.title).classes('text-xl font-bold text-gray-900')
                if event.opponent_name:
                    ui.label(f"vs. {event.opponent_name}").classes('text-sm text-gray-500')
            label_text, badge_style = STATUS_BADGE[event.status]
            ui.label(label_text).classes(f'px-2.5 py-0.5 text-xs font-medium rounded-full {badge_style}')

        with ui.row().classes('w-full gap-2 items-center p-2 border border-gray-200 rounded-lg bg-gray-50'):
            ui.icon('link').classes('text-gray-400 text-base')
            ui.input(value=link).props('readonly borderless dense').classes('flex-grow text-sm')
            ui.button(
                icon='content_copy',
                on_click=lambda: (
                    ui.run_javascript(f'navigator.clipboard.writeText("{link}")'),
                    ui.notify('Enlace copiado', type='positive'),
                ),
            ).props('flat round dense').classes('text-gray-500')

        if not slots:
            ui.label('Este evento todavía no tiene franjas candidatas.').classes('text-sm text-gray-500 py-2')
        else:
            @ui.refreshable
            def render_grid() -> None:
                current_week_start = week_starts[state["week_index"]]
                current_week_days = days_by_week[current_week_start]
                current_week_end = current_week_start + timedelta(days=6)
                is_first_week = state["week_index"] == 0
                is_last_week = state["week_index"] == len(week_starts) - 1

                with ui.row().classes('items-center justify-between w-full no-wrap'):
                    ui.button(icon='chevron_left', on_click=lambda: change_week(-1)).props(
                        'flat round dense' + (' disable' if is_first_week else '')
                    ).classes('text-primary')
                    ui.label(f"{current_week_start:%d/%m} – {current_week_end:%d/%m}").classes(
                        'text-base font-bold text-dark'
                    )
                    ui.button(icon='chevron_right', on_click=lambda: change_week(1)).props(
                        'flat round dense' + (' disable' if is_last_week else '')
                    ).classes('text-primary')

                grid_style = f"grid-template-columns: 56px repeat({len(current_week_days)}, minmax(64px, 1fr));"
                with ui.element('div').classes('w-full overflow-x-auto mt-2'):
                    with ui.element('div').classes('grid gap-2').style(grid_style):
                        ui.element('div')
                        for day in current_week_days:
                            with ui.column().classes('items-center gap-0'):
                                ui.label(DIAS_ES[day.weekday()][:3].capitalize()).classes(
                                    'text-sm font-semibold text-dark'
                                )
                                ui.label(f"{day:%d/%m}").classes('text-xs text-gray-500')

                        for t in all_times:
                            ui.label(f"{t:%H:%M}").classes('text-xs text-gray-500 flex items-center')
                            for day in current_week_days:
                                slot = slot_lookup.get((day, t))
                                if slot is None:
                                    ui.element('div')
                                    continue

                                count = baja_counts.get(slot.id, 0)
                                ratio = count / total_users if total_users else 0
                                bg = mix_color(ratio)
                                is_best = slot.id == best_slot_id
                                is_confirmed_slot = slot.id == event.confirmed_slot_id

                                cell_classes = (
                                    "h-16 w-full min-w-0 rounded-lg flex flex-col items-center justify-center "
                                    "gap-3 text-white transition-transform relative"
                                )
                                if is_confirmed_slot:
                                    cell_classes += " ring-2 ring-offset-2 ring-primary"
                                if is_open:
                                    cell_classes += " cursor-pointer hover:scale-[1.04]"

                                cell = ui.button(
                                    on_click=(lambda s=slot: handle_confirm_slot(event_id, s.id, dialog))
                                    if is_open
                                    else None,
                                ).props('unelevated dense' + ('' if is_open else ' disable'))
                                cell.classes(cell_classes).style(f'background:{bg} !important;')
                                with cell:
                                    ui.label(str(count)).classes('text-lg font-bold leading-none')
                                    ui.label('baja' + ('s' if count != 1 else '')).classes(
                                        'text-[10px] leading-none opacity-90'
                                    )
                                    if is_best:
                                        ui.icon('star').classes('absolute top-1 right-1 text-white text-xs')

                if is_open:
                    ui.label('Toca una franja para confirmarla como horario definitivo.').classes(
                        'text-xs text-gray-400 mt-1'
                    )

            render_grid()

        with ui.row().classes('w-full justify-between items-center mt-2'):
            ui.button('Eliminar evento', on_click=lambda: confirm_delete_event(event_id, dialog)).props(
                'flat no-caps'
            ).classes('text-red-600')
            ui.button('Cerrar', on_click=dialog.close).props('flat no-caps').classes('text-gray-600')

    dialog.open()


def events_tab_page(club: Club):
    with ui.column().classes('w-full max-w-lg mx-auto min-h-screen p-4 gap-4'):

        events = list_events_for_club(club_id=club.id)

        with ui.row().classes('w-full justify-between items-center mb-2'):
            ui.label('Eventos').classes('text-2xl font-bold text-gray-900')
            ui.button(
                'Nuevo evento', icon='add', on_click=lambda: ui.navigate.to('/admin/events/new')
            ).props('unelevated no-caps').classes(
                'bg-primary text-white hover:bg-secondary text-sm font-medium rounded-lg px-3 py-1.5'
            )

        if not events:
            ui.label('Todavía no hay eventos. Crea el primero.').classes('text-sm text-gray-500')

        for event in events:
            label_text, badge_style = STATUS_BADGE[event.status]

            with ui.card().classes(
                'w-full p-4 bg-gray-50 border border-gray-200 rounded-xl shadow-none '
                'hover:shadow-md hover:border-gray-300 transition-all gap-2'
            ):
                with ui.row().classes('w-full items-start no-wrap gap-2'):
                    with ui.column().classes('flex-grow gap-0 cursor-pointer').on(
                        'click', lambda ev=event: open_event_detail(ev.id)
                    ):
                        title = (
                            event.title
                            if not event.opponent_name
                            else f"{event.title} · vs. {event.opponent_name}"
                        )
                        ui.label(title).classes('font-semibold text-gray-900 text-base leading-tight')
                        ui.label(event.event_type.value.title()).classes('text-sm text-gray-500')

                    with ui.column().classes('items-end gap-1 flex-shrink-0'):
                        ui.label(label_text).classes(
                            f'px-2.5 py-0.5 text-xs font-medium rounded-full {badge_style}'
                        )
                        ui.button(
                            icon='delete_outline',
                            on_click=lambda ev=event: confirm_delete_event(ev.id),
                        ).props('flat round dense').classes('text-gray-400 hover:text-red-600')