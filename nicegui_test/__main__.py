#!/usr/bin/env python3
from nicegui import ui, app
import nicegui_test.data_views.details as details
import nicegui_test.data_views.list as list_view
from nicegui_test.borders import make_borders

app.include_router(details.router)
app.include_router(list_view.router)

make_borders("Index!")

ui.run()
