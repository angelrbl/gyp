from nicegui import ui, app

from views.layout import frame

def handle_login():
    ...

@ui.page('/login')
def login_page():
    if app.storage.user.get("user_id", None):
        ui.navigate.to('/admin')

    with frame(navigation_title="Crear club"):
        with ui.column().classes("items-center gap-5 sm:gap-10 w-full text-center sm:mt-10"):
            ui.image('static/badge.png').classes('size-25')

            with ui.column().classes("items-center gap-3 w-full text-center"):
                ui.label("¡Bienvenido!").classes("text-3xl font-black text-primary")
                ui.label("Inicia sesión y comienza a gestionar tu club!").classes('text-xl font-bold text-slate-700')

            with ui.card().classes('w-full bg-primary/40 p-7 rounded-xl'):

                with ui.column().classes("gap-1 w-full text-center mb-2 mt-2"):
                    ui.label("Iniciar sesión").classes('text-md text-slate-500')
                    name = ui.input(label="Usuario").classes('w-full').props('standout="bg-primary text-white"')
                    password = ui.input(label="Contraseña", password=True, password_toggle_button=True).classes('w-full').props('standout="bg-primary text-white"')
                    password_repeat = ui.input(label="Repetir contraseña", password=True, password_toggle_button=True).classes('w-full').props('standout="bg-primary text-white"')

                error_label = ui.label(text="").classes('text-md text-negative hidden')

                (
                    ui.button(
                        text="Iniciar sesión",
                        on_click=lambda: handle_login(
                        )
                    )
                    .classes('w-full pt-3 pb-3 rounded-md font-bold')
                )