from nicegui import ui, app

from views.layout import frame

@ui.page('/admin')
def admin_page() -> None:
    if not app.storage.user.get('user_id', None):
        ui.navigate.to('/login')

    with frame(navigation_title="Admin"):
        if not app.storage.user.get('is_admin', None):
            ui.label("¡Prohíbido el paso!").classes("text-3xl font-black text-primary")
            ui.label("Solo el administrador de tu club puede estar aquí.").classes('text-xl font-bold text-slate-700')