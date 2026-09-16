from nicegui import ui, app

from views.layout import frame

from services.club_service import get_club_by_id

@ui.page('/admin')
def admin_page() -> None:
    if not app.storage.user.get('user_id', None) or not app.storage.user.get('club_id', None):
        ui.navigate.to('/login')

    club_id = app.storage.user.get('club_id')
    club = get_club_by_id(club_id=club_id)

    with frame(navigation_title=(club.name if len(club.name) < 10 else "Admin")):
        if not app.storage.user.get('is_admin', None):
            ui.label("¡Prohíbido el paso!").classes("text-3xl font-black text-negative")
            ui.label("Solo el administrador de tu club puede estar aquí.").classes('text-xl font-bold text-slate-700')

        with ui.tabs().classes('w-full text-primary') as tabs:
            club = ui.tab('Club', icon='sports_soccer')
            squad = ui.tab('Plantilla', icon='groups')
            events = ui.tab('Eventos', icon='event')

        with ui.tab_panels(tabs, value=events).classes('w-full'):
            with ui.tab_panel(club):
                ui.label('Club tab')

            with ui.tab_panel(squad):
                ui.label('Squad tab')

            with ui.tab_panel(events):
                ui.label('Events tab')