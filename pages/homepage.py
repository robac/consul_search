from nicegui import ui
import os

def content() -> None:
    consul_path = os.environ.get('CONSUL_PATH')
    ui.label(f'Consul path is: {consul_path}')
    ui.button('Continue', on_click=lambda: ui.open('/search'))
