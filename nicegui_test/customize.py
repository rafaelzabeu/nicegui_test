from nicegui import ui, APIRouter

from nicegui_test.borders import make_borders

router = APIRouter(prefix="/customize")


@router.page("/")
def customize_view():
    make_borders("Customize")
