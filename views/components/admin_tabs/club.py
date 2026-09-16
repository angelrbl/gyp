from nicegui import app, ui

from models import Club

from services.club_service import update_club_name


def handle_update_club_name(club_id: int, new_name: str, error_label: ui.label) -> None:
    if not new_name:
        error_label.text = "Por favor, introduce un nombre válido antes de guardar los cambios."
        error_label.classes(remove='hidden')
        return

    try:
        update_club_name(club_id=club_id, new_name=new_name)
    except ValueError as e:
        match str(e):
            case "error_club_already_exists":
                error_text = "El nombre introducido ya está en uso, pruebe otro."
            case "error_club_no_longer_exists":
                error_text = "El club cuyo nombre se intenta actualizar ya no existe, pruebe de nuevo."
            case _:
                error_text = "No se ha podido actualizar el nombre. Inténtalo de nuevo."
                print(e)

        error_label.text = error_text
        error_label.classes(remove='hidden')

    return


def club_tab_page(club: Club):
    with ui.row().classes('mt-3 w-full items-center justify-between gap-5'):
        with ui.card().classes('w-full bg-primary/40 p-7 rounded-xl'):
            ui.label("Datos del club").classes('text-xl text-primary font-black')
            name = ui.input(
                label="Nombre del club",
                value=club.name,
                placeholder="Por ejemplo, 'Grandiosa y Peluda'").classes('w-full').props('standout="bg-primary text-white"')

            error_label = ui.label(text="").classes('text-md text-negative hidden')

            ui.button(
                text="Guardar cambios",
                on_click=lambda: handle_update_club_name(
                    club_id=club.id,
                    new_name=name.value,
                    error_label=error_label
                )
            ).classes('w-full pt-3 pb-3 rounded-md font-bold')
        
        with ui.card().classes('w-full bg-primary/40 p-7 rounded-xl items-center'):
            with ui.column().classes('items-center gap-1 text-center justify-between'):
                ui.label(len(club.squad)).classes('text-4xl text-primary font-black')
                ui.label("Jugadores en plantilla").classes('text-lg font-bold text-slate-700')