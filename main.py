from nicegui import ui, app

from core import STORAGE_SECRET, init_db
import views
from views.theme import apply_theme

init_db()
apply_theme()

@ui.page('/')
def index() -> None:
    if not app.storage.user.get('club_id'):
        ui.navigate.to('/create_club')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
            storage_secret=STORAGE_SECRET,
            title="La Pizarra Peluda",
            favicon='static/favicon.svg',
            port=8080
    )
