from pathlib import Path
from nicegui import ui, APIRouter
from nicegui_test.frontend.borders import make_borders
from nicegui_test.frontend.proc_control.nursery import create_process, cribs

router = APIRouter(prefix="/procs")


@ui.refreshable
def _make_list():
    if len(cribs) == 0:
        ui.label("Empty")
        return
    with ui.row():
        for crib in cribs.values():
            with ui.card():
                ui.label().bind_text_from(
                    crib, "id", backward=lambda v: f"ID: {str(v)}"
                )
                ui.label().bind_text_from(crib, "name", backward=lambda v: f"Name: {v}")
                ui.label().bind_text_from(
                    crib, "state", backward=lambda v: f"State: {v}"
                )
                ui.separator()
                ui.button(
                    "Details",
                    on_click=lambda: ui.open(f"/procs/{str(crib.id)}"),
                )


@router.page("/")
def list_process():
    def _add_new(name: str):
        crib = create_process(name, logs_dir=Path(".procs/"))
        ui.open(f"/procs/{str(crib.id)}")

    make_borders("Processes")
    with ui.column():
        _make_list()
        ui.separator()
        with ui.card():
            name_input = ui.input(
                "name",
                placeholder="enter name",
                validation={"Cannot be empty": lambda value: value},
            ).props("clearable")
            ui.button("Add new", on_click=lambda: _add_new(name_input.value))
