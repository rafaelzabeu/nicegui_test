import uuid
from nicegui import app, ui, APIRouter
from nicegui_test.frontend.borders import make_borders
from nicegui_test.frontend.data_stuff import datas, Data, DataState

router = APIRouter(prefix="/data")


def _make_not_found():
    ui.label("404 not found!").classes(replace="text-negative")


@ui.refreshable
def _make_details(data: Data):
    ui.label().bind_text_from(data, "id", backward=lambda v: f"ID: {v}")
    ui.label().bind_text_from(data, "name", backward=lambda v: f"Name: {v}")
    ui.label().bind_text_from(data, "status", backward=lambda v: f"Status {v}")
    ui.separator()
    match data.state:
        case DataState.starting:
            ui.spinner(color="gree")
        case DataState.ready:
            ui.button(
                icon="delete_forever",
                color="red",
                on_click=lambda: data.stop(
                    on_started=_make_details.refresh,
                    on_finished=lambda: ui.open("/data"),
                ),
            )
        case DataState.deleting:
            ui.spinner(color="red")


@router.page("/{id}")
def data_detail(id: uuid.UUID):
    make_borders(f"{str(id)}", app.storage.user)
    if data := datas.get(id, None):
        _make_details(data=data)
    else:
        _make_not_found()
