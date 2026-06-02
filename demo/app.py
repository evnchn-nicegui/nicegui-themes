"""Kitchen-sink demo. Renders the v0.1 Tier 1 coverage surface under brutalist.

Run:
    cd ~/nicegui-themes
    uv run --with nicegui --with-editable . python demo/app.py

Open http://localhost:8099/
"""
import os

from nicegui import ui

import nicegui_themes

THEME = os.environ.get('THEME', 'brutalist')
PORT = int(os.environ.get('PORT', '8099'))
COUNT = int(os.environ.get('COUNT', '1'))

if THEME == 'brutalist':
    nicegui_themes.brutalist()
# else: Quasar Material default (no theme applied) — used for bench baseline

with ui.column().classes('p-8 gap-4 max-w-3xl mx-auto'):
    ui.label(f'{THEME.title()} Tier 1 kitchen sink (×{COUNT})').classes('text-3xl')
    ui.label(
        'Tier 1: button · card · input · number · textarea · select · '
        'toggle · switch · checkbox · radio · slider · chip · label'
    ).classes('text-sm')

    for _ in range(COUNT):
        with ui.card():
            ui.label('Form elements').classes('text-xl')
            ui.input('Name', placeholder='your name')
            ui.number('Age', value=25)
            ui.textarea('Bio', placeholder='multi-line text')
            ui.select(['option a', 'option b', 'option c'],
                      label='Pick one', value='option a')
            with ui.row():
                ui.checkbox('I agree')
                ui.switch('Notify me')
                ui.toggle(['off', 'mid', 'on'], value='mid')
            with ui.row():
                ui.radio(['low', 'mid', 'high'], value='mid').props('inline')
            ui.slider(min=0, max=100, value=42).classes('w-full')

        with ui.card():
            ui.label('Actions').classes('text-xl')
            with ui.row():
                ui.button('Primary')
                ui.button('Secondary').props('color=secondary')
                ui.button('Accent').props('color=accent')
            with ui.row():
                ui.chip('tag-a')
                ui.chip('tag-b')
                ui.chip('removable', removable=True)


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(port=PORT, reload=False, show=False)
