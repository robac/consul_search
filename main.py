from pages import *
from nicegui import app, ui

@ui.page('/')
def route_search() -> None:
    search.content()

ui.run()