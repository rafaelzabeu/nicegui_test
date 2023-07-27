import asyncio
from pathlib import Path
from typing import Any
import uuid
from nicegui import ui, APIRouter
from nicegui_test.frontend.borders import make_borders
from nicegui_test.frontend.proc_control.nursery import (
    create_process,
    cribs,
    ProcessStates,
    Crib,
    stop_process,
    remove_process,
)

router = APIRouter(prefix="/procs")


async def _update_log(log, crib: Crib):
    while True:
        value = await crib.stdout.readline()
        if not value:
            return
        value = value.decode()
        log.push(value)


def _delete_crib_modal(crib: Crib):
    with ui.dialog() as dialog, ui.card():
        ui.label("This can't be undone.")

        async def _do_delete_crib():
            await remove_process(crib)
            ui.open("/procs")

        with ui.row():
            ui.button("DO IT!", on_click=_do_delete_crib)
            ui.button("No", on_click=dialog.close)

    dialog.open()


@router.page("/{cid}")
async def detail_view(cid: uuid.UUID):
    make_borders("Proc Details")
    if crib := cribs.get(cid, None):
        ui.label().bind_text_from(crib, "id", backward=lambda v: f"ID: {str(v)}")
        ui.label().bind_text_from(crib, "name", backward=lambda v: f"Name: {v}")
        ui.label().bind_text_from(crib, "state", backward=lambda v: f"State: {v}")
        ui.separator()
        with ui.row():
            ui.button(
                icon="stop_circle", on_click=lambda: stop_process(crib)
            ).bind_enabled_from(
                crib,
                "state",
                backward=lambda v: v != ProcessStates.stopping
                and v != ProcessStates.stopped,
            ).bind_visibility_from(
                crib,
                "state",
                backward=lambda v: v != ProcessStates.stopping
                and v != ProcessStates.stopped,
            )
            ui.button(
                icon="delete_forever", on_click=lambda: _delete_crib_modal(crib)
            ).bind_enabled_from(
                crib, "state", backward=lambda v: v == ProcessStates.stopped
            ).bind_visibility_from(
                crib, "state", backward=lambda v: v == ProcessStates.stopped
            )
        if crib.state == ProcessStates.running:
            ui.label("Output")
            output = ui.log().classes("resize")
            asyncio.ensure_future(_update_log(output, crib))

            async def _send(event):
                crib.stdin.write(f"{event.sender.value}\n".encode())
                await crib.stdin.drain()
                event.sender.value = ""

            ui.input().on("keydown.enter", _send).bind_enabled_from(
                crib, "state", backward=lambda v: v == ProcessStates.running
            )
    else:
        ui.label("Not found").tailwind.text_color("red-400").font_size("xl")
