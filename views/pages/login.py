from nicegui import ui

from views.layout import frame

@ui.page('/login')
def login_page():
    with frame(navigation_title="Login"):
        ui.label("Login")