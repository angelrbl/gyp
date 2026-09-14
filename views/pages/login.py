from nicegui import ui, app

from views.layout import frame

@ui.page('/login')
def login_page():
    with frame(navigation_title="Iniciar Sesión"):
        ui.label("Login")