#!/usr/bin/env python3
from nicegui import app, ui
from starlette.responses import RedirectResponse

import nicegui_test.frontend.customize as customize
import nicegui_test.frontend.data_views.details as details
import nicegui_test.frontend.data_views.list as list_view
import nicegui_test.frontend.random_stuff as random_stuff
import nicegui_test.frontend.proc_control.list as list_procs
import nicegui_test.frontend.proc_control.details as detail_proc

app.include_router(details.router)
app.include_router(list_view.router)
app.include_router(customize.router)
app.include_router(random_stuff.router)
app.include_router(list_procs.router)
app.include_router(detail_proc.router)


@ui.page("/")
def index():
    return RedirectResponse(url="/data")


ui.run(
    storage_secret="a not very secret secret (the word secret looks weird) :D",
    title="The data test",
)
