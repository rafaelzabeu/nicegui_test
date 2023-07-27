import random
from nicegui import ui, APIRouter, app
from nicegui_test.frontend.borders import make_borders
import time

router = APIRouter(prefix="/random")


@router.page("/table")
def table_suff():
    make_borders("Tables")

    columns = [
        {"name": "name", "label": "Name", "field": "name", "required": True},
        {"name": "age", "label": "Age", "field": "age", "sortable": True},
    ]
    rows = [
        {"id": 0, "name": "Alice", "age": 18},
        {"id": 1, "name": "Bob", "age": 21},
        {"id": 2, "name": "Lionel", "age": 19},
        {"id": 3, "name": "Michael", "age": 32},
        {"id": 4, "name": "Julie", "age": 12},
        {"id": 5, "name": "Livia", "age": 25},
        {"id": 6, "name": "Carol"},
    ]

    with ui.table(
        title="My Team", columns=columns, rows=rows, selection="multiple", pagination=10
    ).classes("w-96") as table:
        with table.add_slot("top-right"):
            with ui.input(placeholder="Search").props("type=search").bind_value(
                table, "filter"
            ).add_slot("append"):
                ui.icon("search")
        with table.add_slot("bottom-row"):
            with table.row():
                with table.cell():
                    ui.button(
                        on_click=lambda: (
                            table.add_rows(
                                {
                                    "id": time.time(),
                                    "name": new_name.value,
                                    "age": new_age.value,
                                }
                            ),
                            new_name.set_value(None),
                            new_age.set_value(None),
                        ),
                        icon="add",
                    ).props("flat fab-mini")
                with table.cell():
                    new_name = ui.input("Name")
                with table.cell():
                    new_age = ui.number("Age")

    ui.label().bind_text_from(
        table, "selected", lambda val: f"Current selection: {val}"
    )
    ui.button(
        "Remove", on_click=lambda: table.remove_rows(*table.selected)
    ).bind_visibility_from(table, "selected", backward=lambda val: bool(val))


@router.page("/log")
def log_():
    make_borders("Random log")
    l = ui.log()
    l.classes("resize")
    ui.button("Add line", on_click=lambda: l.push(f"{random.random()}"))


@router.page("/")
def list_():
    make_borders("Random stuff")
    with ui.column():
        ui.link("Table", table_suff)
        ui.link("Log", log_)
