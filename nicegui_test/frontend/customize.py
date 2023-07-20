import json

from nicegui import APIRouter, app, ui
from nicegui_test.frontend.borders import apply_ui_colors, color_settings

from nicegui_test.frontend.borders import make_borders

router = APIRouter(prefix="/customize")

"""
primary='#5898d4',
                 secondary='#26a69a',
                 accent='#9c27b0',
                 dark='#1d1d1d',
                 positive='#21ba45',
                 negative='#c10015',
                 info='#31ccec',
                 warning='#f2c037'
"""


def _on_color_change(setting_name: str):
    def _do_change(new_value):
        app.storage.user[setting_name] = new_value.value
        apply_ui_colors()

    return _do_change


def _on_reset_value_to_default(setting_name: str, reset_to: str):
    def _do_reset():
        app.storage.user[setting_name] = reset_to
        apply_ui_colors()

    return _do_reset


def _reset_all_colours():
    for setting, default in color_settings:
        app.storage.user[setting] = default
    apply_ui_colors()


def _make_color_pickers():
    with ui.card():
        ui.label("Customize app colors").tailwind.font_size("lg")
        with ui.column():
            for color_setting, default_value in color_settings:
                with ui.row():
                    with ui.color_input(
                        f"{color_setting} color",
                        on_change=_on_color_change(color_setting),
                    ).bind_value_from(app.storage.user, color_setting):
                        ui.button(
                            icon="delete",
                            color="red",
                            on_click=_on_reset_value_to_default(
                                color_setting, default_value
                            ),
                        ).props("flat dense").tooltip("Reset to default")
            ui.button("Reset all", on_click=_reset_all_colours).tooltip(
                "Rest all colours to default values"
            )


@ui.refreshable
def _make_settings_dump():
    with ui.card():
        with ui.expansion("Settings dump", icon="build"):
            ui.label().bind_text_from(
                app.storage, "user", backward=lambda x: json.dumps(x, indent=4)
            )
            ui.button(icon="autorenew", on_click=_make_settings_dump.refresh)


@router.page("/")
def customize_view():
    make_borders("Customize")
    with ui.row():
        _make_color_pickers()
        _make_settings_dump()
