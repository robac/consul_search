from nicegui import ui
from contextlib import contextmanager
import asyncio

import consul_tools
from consul_tools import *
from consul_tools.ConsulSearch import ConsulSearch

searcher = ConsulSearch()
ui.timer(10, lambda: searcher.make_callable())

result = [((1,0), "test", "testvaalue")]
detail = None
data = None

async def handle_click(button: ui.button, text):
    global result
    ui.notify("Search started")
    with disable(button):
        found = await find.find([text], get_config())
        result = found
        draw_result.refresh()
    ui.notify("Search finished")

@contextmanager
def disable(button: ui.button) -> None:
    button.disable()
    try:
        yield
    finally:
        button.enable()

@ui.refreshable
def draw_result():
    async def handle_cell_click():
        global detail
        row = await grid.get_selected_row()
        detail = row
        draw_detail.refresh()

    data = [{
        "key" : i[1],
        "value" : i[2]
    } for i in result]

    grid = ui.aggrid({
        'defaultColDef': {'flex': 1},
        'columnDefs': [
            {'headerName': 'Key', 'field': 'key'},
            {'headerName': 'Value', 'field': 'value'}
        ],
        'rowData': data,
        'rowSelection': 'multiple',
    }).on('cellClicked', lambda event: handle_cell_click())

def get_config():
    return {
        "CONSUL_PATH" : r"consul.consul-1.cecolo.gofg.net",
        "CONSUL_PORT" : 8500,
        "CONSUL_ENCODING" : "UTF-8",
        "SEARCH_RECURSE" : True,
        "SEARCH_INDEX" : ""
    }

@ui.refreshable
def draw_detail():
    if detail is None:
        ui.label("Nothing to show")
    else:
        ui.link(detail["key"], consul_tools.utils.get_consul_kv_path(get_config(), detail["key"]))
        ui.textarea(value=detail["value"]).classes('w-full').props('fit=scale-down')


def content() -> None:
    #ui.label("Nothing").bind_text(searcher, 'last_update', forward=lambda x: x if x else "No data")
    ui.label().bind_text(searcher, "timer_run")
    with ui.card().classes('w-full'):
        input = ui.input(placeholder='what to search', value="salt")
        ui.button('Search', on_click= lambda e: handle_click(e.sender, input.value))\
          .bind_enabled(searcher, 'can_process')
    with ui.row().classes('w-full'):
        with ui.card().classes('w-full'):
            draw_result()
            draw_detail()


