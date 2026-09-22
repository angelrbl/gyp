from nicegui import ui, app

COLORS = {
    'primary': "#D6273E",
    'secondary': '#8C1526',
    'accent': "#8C1526",
    'negative': "#A32D2D",
    'positive': "#2F9E5B",
    'dark': "#161616",
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

POSITIVE_RGB = (47, 158, 91)
NEGATIVE_RGB = (214, 39, 62)

def mix_color(ratio: float) -> str:
    r = round(POSITIVE_RGB[0] + (NEGATIVE_RGB[0] - POSITIVE_RGB[0]) * ratio)
    g = round(POSITIVE_RGB[1] + (NEGATIVE_RGB[1] - POSITIVE_RGB[1]) * ratio)
    b = round(POSITIVE_RGB[2] + (NEGATIVE_RGB[2] - POSITIVE_RGB[2]) * ratio)
    return f"rgb({r},{g},{b})"
