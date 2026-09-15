from contextlib import contextmanager
from nicegui import ui, app

def require_login() -> bool:
    if not app.storage.user.get("user_id"):
        ui.navigate.to("/login")
        return False
    return True


def logout() -> None:
    app.storage.user.clear()
    ui.navigate.to("/login")

@contextmanager
def frame(navigation_title: str = "La Pizarra Peluda") -> None:
    def go_home():
        ui.navigate.to('/')

    with ui.header().classes(
        'justify-between items-center '
        'bg-primary/40 backdrop-blur-xl backdrop-saturate-150 '
        'border-b border-white/20 '
        'text-white p-4 shadow-lg shadow-black/5'
    ):
            ui.label(navigation_title).on('click', go_home).classes('text-lg font-bold tracking-wide hover:opacity-90')
            ui.icon('img:/static/badge_outline.svg', size='lg')

    with ui.element('main').classes('w-full max-w-lg mx-auto p-4 min-h-screen pb-20'):
        yield