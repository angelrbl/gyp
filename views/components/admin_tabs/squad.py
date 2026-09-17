from nicegui import app, ui

from models import Club, RoleType

from services.user_service import list_users_for_club
from services.role_service import get_user_roles

def squad_tab_page(club: Club):
    with ui.column().classes('w-full max-w-lg mx-auto min-h-screen p-4 gap-4'):

        squad = list_users_for_club(club_id=club.id)
        
        with ui.row().classes('w-full justify-between items-center mb-2'):
            ui.label('Jugadores').classes('text-2xl font-bold text-gray-900')
            
            ui.button('Nuevo jugador', icon='add') \
                .props('unelevated no-caps') \
                .classes('bg-primary text-white hover:bg-secondary text-sm font-medium rounded-lg px-3 py-1.5')

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
                    print(user_roles)
                    roles_text = ", ".join(role.value.title() for role in user_roles)
                    ui.label(roles_text).classes('text-sm font-medium text-gray-600')
                    
                    with ui.row().classes('gap-1 items-center'):
                        ui.button(icon='link').props('flat round density=compact') \
                            .classes('text-gray-400 hover:text-gray-700 hover:bg-gray-200')
                        
                        ui.button(icon='edit').props('flat round density=compact') \
                            .classes('text-gray-400 hover:text-gray-700 hover:bg-gray-200')
                        
                        ui.button(icon='delete').props('flat round density=compact') \
                            .classes('text-gray-400 hover:text-primary hover:bg-accent')