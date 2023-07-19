from nicegui import ui


def make_borders(title: str):
    with ui.header(elevated=True):
        ui.button(on_click=lambda: right_drawer.toggle(), icon="menu").props(
            "flat color=white"
        )
        ui.label(title)

    with ui.left_drawer(fixed=False, bordered=True) as right_drawer:
        ui.link("Data List", "/data")
