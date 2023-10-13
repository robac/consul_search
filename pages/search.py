from nicegui import ui
import asyncio
from contextlib import contextmanager
from consul_find import find

result = [((1,0), "test", "testvaalue")]
detail = None

async def handle_click(button: ui.button, text):
    global result
    with disable(button):
        found = await find.find([text])
        result = found
        draw_result.refresh()

def handle_cell_click(value):
    global detail
    detail = value
    draw_detail.refresh()

@contextmanager
def disable(button: ui.button) -> None:
    button.disable()
    try:
        yield
    finally:
        button.enable()

@ui.refreshable
def draw_result():
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
    }).on('cellClicked', lambda event: handle_cell_click(event.args["value"]))

@ui.refreshable
def draw_detail():
    if detail is None:
        ui.label("Nothing to show")
    else:
        ui.textarea(value=detail).classes('w-full')


def content() -> None:
    input = ui.input(placeholder='what to search', value="salt")
    ui.button('Search', on_click= lambda e: handle_click(e.sender, input.value))
    with ui.row().classes('w-full'):
        draw_result()
        draw_detail()


