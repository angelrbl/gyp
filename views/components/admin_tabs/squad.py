from nicegui import app, ui

from models import User, Club, RoleType

from services.user_service import list_users_for_club, create_user
from services.role_service import get_user_roles, set_user_roles
from services.token_service import create_activation_token

def handle_create_activation_link(user: User):
    if user.is_active:
        ui.notify('¡Este usuario ya está activo!', type="positive")
        return
    
    with ui.dialog() as dialog:
        try:
            token = create_activation_token(user_id=user.id)
            with ui.card().classes('w-full p-4 bg-gray-50 border border-gray-200 rounded-xl shadow-none gap-2'):
                with ui.row().classes('w-full gap-2 p-2 border border-gray-300 rounded-lg shadow-none'):
                    ui.label(token.value).classes('text-gray-900 text-md')
                    async def clip():
                        await ui.run_javascript(f'navigator.clipboard.writeText("{token.value}")')

                    ui.button('Clip', on_click=clip)
        except:
            ui.notify("El usuario no existe, pruebe de nuevo.")
            dialog.close()

def handle_create_user(
    club_id: int,
    name: str,
    error_label: ui.label,
    number: int | None = None,
    roles: list[RoleType] | None = None
) -> None:
    if not (club_id and name):
        error_label.text = "Por favor, rellena todos los campos antes de eliminar el club."
        error_label.classes(remove='hidden')
        return

    try:
        user = create_user(club_id=club_id, name=name, number=number)
        set_user_roles(user_id=user.id, roles=roles)
        ui.notify("Jugador creado éxitosamente", type="positive")
        ui.navigate.reload()
    except ValueError as e:
        match str(e):
            case "error_user_already_exists":
                error_text = "El usuario ya existe en este club, pruebe otro."
            case _:
                error_text = "No se ha podido borrar el club. Inténtalo de nuevo."
                print(e)

        error_label.text = error_text
        error_label.classes(remove='hidden')

    return

def squad_tab_page(club: Club):
    with ui.column().classes('w-full max-w-lg mx-auto min-h-screen p-4 gap-4'):

        squad = list_users_for_club(club_id=club.id)
        
        with ui.row().classes('w-full justify-between items-center mb-2'):
            ui.label('Jugadores').classes('text-2xl font-bold text-gray-900')
            
            with ui.dropdown_button('Nuevo jugador', icon='add') \
                .props('unelevated no-caps') \
                .classes('bg-primary text-white hover:bg-secondary text-sm font-medium rounded-lg px-3 py-1.5'):
                with ui.column().classes("p-4 gap-1 w-full text-center mb-2"):
                    ui.label("User info").classes('text-md text-slate-500')
                    with ui.row().classes('w-full gap-1'):
                        name = ui.input(label="Nombre").props('standout="bg-primary text-white"')
                        number = ui.number(label="Dorsal", min=1, max=99, step=1).props('standout="bg-primary text-white"')

                    roles = ui.select({rt: rt.value.title() for rt in RoleType}, clearable=True, multiple=True, label="Roles").classes('w-full mb-2').props('use-chips')
    
                    error_label = ui.label(text="").classes('text-md text-negative hidden')
    
                    (
                        ui.button(
                            text="Crear",
                            on_click=lambda: handle_create_user(
                                club_id=club.id,
                                name=name.value,
                                number=number.value,
                                roles=roles.value or [],
                                error_label=error_label
                            )
                        )
                        .classes('w-full pt-3 pb-3 rounded-md font-bold')
                    )

        for user in squad:
            user_roles = get_user_roles(user_id=user.id)

            with ui.card().classes('w-full p-4 bg-gray-50 border border-gray-200 rounded-xl shadow-none gap-2'):
                
                with ui.row().classes('w-full justify-between items-start no-wrap'):
                    with ui.column().classes('gap-0'):
                        ui.label(user.name).classes('font-semibold text-gray-900 text-base leading-tight')
                        ui.label(user.email).classes('text-sm text-gray-500')

                    if RoleType.STAFF in user_roles:
                        badge_style = 'bg-green-100 text-green-700' if user.is_active else 'bg-amber-100 text-amber-700'
                        (
                            ui.label("Activo" if user.is_active else "Pendiente")
                            .classes(f'px-2.5 py-0.5 text-xs font-medium rounded-full {badge_style}')
                        )

                ui.separator().classes('my-1 bg-gray-200')

                with ui.row().classes('w-full justify-between items-center'):
                    roles_text = ", ".join(role.value.title() for role in user_roles)
                    ui.label(roles_text).classes('text-sm font-medium text-gray-600')
                    
                    with ui.row().classes('gap-1 items-center'):
                        ui.button(icon='link', on_click=lambda usr=user: handle_create_activation_link(user=usr)) \
                            .props('flat round density=compact') \
                            .classes('text-gray-400 hover:text-gray-700 hover:bg-gray-200')

                        
                        ui.button(icon='edit').props('flat round density=compact') \
                            .classes('text-gray-400 hover:text-gray-700 hover:bg-gray-200')
                        
                        ui.button(icon='delete').props('flat round density=compact') \
                            .classes('text-gray-400 hover:text-primary hover:bg-accent')