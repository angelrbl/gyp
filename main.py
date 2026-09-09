from core import STORAGE_SECRET, init_db
from nicegui import ui, app
import os

import models
init_db()

@ui.page('/')
def index() -> None:
    if not app.storage.user.get('user_id'):
        ui.navigate.to('/login')

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        storage_secret=STORAGE_SECRET,
        title="GYP",
        favicon='static/favicon.svg',
    )