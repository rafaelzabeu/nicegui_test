import asyncio
from nicegui import app, ui, APIRouter
import uuid

from nicegui_test.frontend.borders import make_borders


from nicegui_test.frontend.data_stuff import Data, datas, DataState

router = APIRouter(prefix="/data")


@ui.refreshable
def build_data():
    if not datas:
        ui.label("Empty")
        return
    with ui.row():
        for id, data in datas.items():
            with ui.card():
                ui.label(f"ID: {str(id)}")
                ui.label().bind_text_from(data, "name", backward=lambda x: f"Name: {x}")
                ui.separator()
                with ui.row():
                    ui.label().bind_text_from(
                        data, "state", backward=lambda x: f"State: {x}"
                    )
                    ui.link("detail", f"/data/{str(id)}")


datas.on_change_list.append(build_data.refresh)


@router.page("/")
def list_view():
    def add_new(name: str):
        data = Data(id=uuid.uuid4(), name=name)
        asyncio.ensure_future(data.startup(build_data.refresh))
        datas[data.id] = data
        name_input.set_value("")
        name_input._error = None
        name_input.props(remove="error")
        build_data.refresh()

    make_borders(title="Data List")
    build_data()
    ui.separator()

    with ui.card():
        name_input = ui.input(
            "name",
            placeholder="enter name",
            validation={"Cannot be empty": lambda value: value},
        ).props("clearable")
        ui.button("Add new", on_click=lambda: add_new(name_input.value))
