from nicegui import ui, app

COLORS = {
    'primary': "#e4002b",
    'secondary': '#c8102e',
    'accent': '#a6192e',
    'negative': '#E63946',
    'positive': '#38A169',
    'dark': '#051c2c',
}

def apply_theme():
    app.add_static_files('/static', '././static')

    ui.colors(
        primary=COLORS['primary'],
        secondary=COLORS['secondary'],
        accent=COLORS['accent'],
        negative=COLORS['negative'],
        positive=COLORS['positive'],
        dark=COLORS['dark'],
    )