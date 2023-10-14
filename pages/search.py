from nicegui import ui, run
from contextlib import contextmanager
import asyncio

from consul_tools.ConsulSearch import ConsulSearch
from consul_tools import utils

result = [((1,0), "test", "testvaalue")]
detail = None
data = None

def searchx(text, searcher):
    return searcher.search([text])

async def handle_click(button: ui.button, text):
    global result
    ui.notify("Search started")
    with disable(button):
        found = await run.cpu_bound(searchx, text, searcher)
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
    } for i in result] if result else None

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
        ui.link(detail["key"], utils.get_consul_kv_path(get_config(), detail["key"]))
        ui.textarea(value=detail["value"]).classes('w-full').props('fit=scale-down')


def content() -> None:
    #ui.label("Nothing").bind_text(searcher, 'last_update', forward=lambda x: x if x else "No data")
    with ui.card().classes('w-full'):
        input = ui.input(placeholder='what to search', value="salt")
        ui.button('Search', on_click= lambda e: handle_click(e.sender, input.value))
    with ui.row().classes('w-full'):
        with ui.card().classes('w-full'):
            draw_result()
            draw_detail()

searcher = ConsulSearch()
ui.timer(120, lambda: searcher.load_data(get_config()))

