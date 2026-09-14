from nicegui import ui, app

COLORS = {
    'primary': "#D6273E",
    'secondary': '#8C1526',
    'accent': "#8C1526",
    'negative': "#A32D2D",
    'positive': "#2F9E5B",
    'dark': "#241417",
}

def hide_scrollbar() -> None:
    ui.add_head_html('''
        <style>
            ::-webkit-scrollbar {
                display: none;
            }
            * {
                -ms-overflow-style: none;
                scrollbar-width: none;
            }
        </style>
    ''', shared=True)

def apply_theme() -> None:
    hide_scrollbar()

    app.add_static_files('/static', '././static')

    app.colors(**COLORS)