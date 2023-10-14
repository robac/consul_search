from pages import *
from nicegui import app, ui

@ui.page('/')
def route_homepage() -> None:
    homepage.content()

@ui.page('/search')
def route_search() -> None:
    search.content()


ui.run()