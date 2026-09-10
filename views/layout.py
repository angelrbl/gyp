from contextlib import contextmanager
from nicegui import ui, app

from views.theme import apply_theme

@contextmanager
def frame(navigation_title: str = "La Pizarra Peluda"):
    apply_theme()

    def go_home():
        ui.navigate.to('/')

    def log_out():
        app.storage.user.pop('user_id', None)
        go_home()
    
    with ui.header().classes('justify-between items-center backdrop-blur-md bg-primary text-white p-4 shadow-md'):
            ui.icon('img:/static/badge.svg', size='lg')
            ui.label(navigation_title).on('click', go_home).classes('text-lg font-bold tracking-wide hover:opacity-90')

            if app.storage.user.get('user_id', None):
                ui.label(_("nav_log_out")).on('click', log_out).classes('cursor-pointer text-md sm:text-xl text-slate-700 hover:text-slate-500')
             

    with ui.element('main').classes('w-full max-w-lg mx-auto p-4 min-h-screen pb-20'):
        yield