from nicegui import ui, app


def make_borders(title: str, user_storage: dict = {}):
    apply_ui_colors()

    with ui.header(elevated=True):
        ui.button(on_click=lambda: right_drawer.toggle(), icon="menu").props(
            "flat color=white"
        )
        ui.label(title)

    with ui.left_drawer(fixed=False, bordered=True) as right_drawer:
        with ui.column():
            ui.link("Data List", "/data")
            ui.link("Random stuff", "/random")
            ui.button(icon="settings", on_click=lambda: ui.open("/customize")).props(
                "bottom-0"
            )


color_settings = [
    ("primary", "#5898d4"),
    ("secondary", "#26a69a"),
    ("accent", "#9c27b0"),
    ("dark", "#1d1d1d"),
    ("positive", "#21ba45"),
    ("negative", "#c10015"),
    ("info", "#31ccec"),
    ("warning", "#f2c037"),
]


def apply_ui_colors():
    ui.colors(
        **{setting: app.storage.user.get(setting, "") for setting, _ in color_settings}
    )
