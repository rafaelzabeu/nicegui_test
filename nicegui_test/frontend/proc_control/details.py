from pathlib import Path
import uuid
from nicegui import ui, APIRouter
from nicegui_test.frontend.borders import make_borders
from nicegui_test.frontend.proc_control.nursery import (
    create_process,
    cribs,
    ProcessStates,
)

router = APIRouter(prefix="/procs")


@router.page("/{cid}")
def detail_view(cid: uuid.UUID):
    make_borders("Proc Details")
    if crib := cribs.get(cid, None):
        with ui.column() as row:
            with ui.card():
                ui.label().bind_text_from(
                    crib, "id", backward=lambda v: f"ID: {str(v)}"
                )
                ui.label().bind_text_from(crib, "name", backward=lambda v: f"Name: {v}")
                ui.label().bind_text_from(
                    crib, "state", backward=lambda v: f"State: {v}"
                )
                ui.separator()
                with ui.row():
                    ui.button(icon="stop_circle").bind_enabled_from(
                        crib,
                        "state",
                        backward=lambda v: v != ProcessStates.stopping
                        and v != ProcessStates.stopped,
                    )
                    ui.button(icon="stop_circle").bind_enabled_from(
                        crib,
                        "state",
                        backward=lambda v: v != ProcessStates.starting
                        and v != ProcessStates.running,
                    )

    else:
        ui.label("Not found").tailwind.text_color("red-400").font_size("xl")
