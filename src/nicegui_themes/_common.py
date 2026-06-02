"""Shared dragon-fixes applied by every theme.

**NiceGUI cascade-layer rule** (per evnchn's GH discussion guidance,
codified here as the canonical override pattern): layered CSS wins over
unlayered CSS in NiceGUI, and among layers declared LATER wins (which is
why Quasar names its last layer `quasar_importants` and puts its `!important`
rules there). To win an override fight, wrap your CSS in `@layer overrides`
(declared 7th in NiceGUI's layer order, beats `utilities` where Tailwind's
runtime classes live).

NiceGUI's full layer order:
    @layer theme, base, quasar, nicegui, components, utilities, overrides, quasar_importants;

Dragon #5 (Material Icons font clobber): theme fonts on container inherit
onto `<i class="material-icons">`. Fix: assert `.q-icon{font-family:'Material Icons'}`
in `@layer overrides` so it beats theme rules in `nicegui`/`utilities`.

Dragon #7 (Quasar SVG-rendered controls): radio dots, switch knob, checkbox
checkmark are SVG paths inside `.q-X__bg`/`.q-toggle__track`/`.q-toggle__thumb`,
while the actual `<input>` (`.q-X__native`) is given Tailwind's `.hidden` class
and rendered display:none. Fix: hide the SVG parts and promote the native
input — all via `@layer overrides` so we win the cascade fight with Tailwind's
`utilities`-layered `.hidden{display:none}`. Pure CSS, no JS observer.
Formalized from evnchn's basecoat hack #5608.
"""
from nicegui import ui


_ICON_FONT_FIX_INJECTED = False
_SVG_CONTROL_HIDE_INJECTED = False


def ensure_icon_font_fix() -> None:
    """Re-assert Material Icons font on `.q-icon`. Wrapped in `@layer overrides`
    so it wins NiceGUI's layered cascade. Idempotent. `shared=True` broadcasts
    to every connected client.
    """
    global _ICON_FONT_FIX_INJECTED
    if _ICON_FONT_FIX_INJECTED:
        return
    ui.add_head_html(
        "<style>"
        "@layer overrides{.q-icon{font-family:'Material Icons'!important}}"
        "</style>",
        shared=True,
    )
    _ICON_FONT_FIX_INJECTED = True


def enable_svg_control_replacement() -> None:
    """Slay Dragon #7: Quasar's SVG-rendered radio/checkbox/toggle controls.

    Pure CSS, wrapped in `@layer overrides` so it beats Tailwind's
    `utilities`-layered `.hidden{display:none}` per NiceGUI's cascade rule
    (layered > unlayered; later layer wins).

    1. Hide the SVG bg parts (`.q-checkbox__bg`, `.q-radio__bg`,
       `.q-toggle__track`, `.q-toggle__thumb`).
    2. Promote the hidden `__native` <input> to display:block and baseline-
       position it (appearance:none, absolute center).

    After this runs, theme styles the visible `__native` inputs via plain
    `ui.add_css` for shape (background, border, ::after pseudo for check/dot).
    Use `.q-X__inner--truthy > .q-X__native` for active state — Quasar already
    toggles that class.

    Formalized from evnchn's basecoat hack #5608. V1 of that hack used a
    MutationObserver; V3/V4 used Tailwind's `<style type="text/tailwindcss">`
    runtime. We use neither — just the `@layer overrides` cascade trick, which
    is the most idiomatic NiceGUI pattern. No JS, no observer.

    Idempotent. `shared=True` broadcasts to every client.
    """
    global _SVG_CONTROL_HIDE_INJECTED
    if _SVG_CONTROL_HIDE_INJECTED:
        return
    ui.add_head_html(
        '<style>'
        '@layer overrides {'
        '.q-radio__bg,.q-checkbox__bg,.q-toggle__track,.q-toggle__thumb'
        '{display:none!important}'
        '.q-checkbox__inner>.q-checkbox__native,'
        '.q-radio__inner>.q-radio__native,'
        '.q-toggle__inner>.q-toggle__native'
        '{display:block!important;position:absolute;top:50%;left:50%;'
        'transform:translate(-50%,-50%);appearance:none;-webkit-appearance:none;'
        'margin:0;cursor:pointer}'
        '}'
        '</style>',
        shared=True,
    )
    _SVG_CONTROL_HIDE_INJECTED = True
