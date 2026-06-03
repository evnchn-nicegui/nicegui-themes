"""Brutalist theme — Tier 1 coverage.

Verified WCAG-AAA: white text on #2b2bff = 7.26:1 contrast (see DESIGN.md §7.1).
Render-cost theory solid (1-layer hard-offset shadow vs Quasar Material's
3-layer alpha-blended elevation); benchmark pending.

Tier 1 surface: button, card, input/number/textarea, select, toggle/switch/
checkbox/radio, slider, chip, label.

Tier 2 surface (table, dialog, tabs, expansion, progress, list, menu) lands in the next wave.
"""
from nicegui import ui

from nicegui_themes._common import enable_svg_control_replacement, ensure_icon_font_fix


# Verified AAA palette. Do not change without re-running contrast math.
_PRIMARY = '#2b2bff'
_SECONDARY = '#111111'
_ACCENT = '#ffe600'
_BODY_BG = '#faf7e8'
_CARD_BG = '#ffffff'
_BORDER = '#000000'


def apply() -> None:
    """Apply the brutalist Tier 1 shape pass to the current NiceGUI app."""
    ui.colors(primary=_PRIMARY, secondary=_SECONDARY, accent=_ACCENT)

    ui.add_head_html(
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">'
    )

    ui.add_css(f'''
        /* Typography + body */
        body {{
            background: {_BODY_BG};
            font-family: "Space Grotesk", sans-serif;
        }}

        /* Card — Dragon #2: kill hover-elevate by pinning the shadow */
        .q-card {{
            background: {_CARD_BG} !important;
            border: 3px solid {_BORDER};
            border-radius: 0;
            box-shadow: 7px 7px 0 {_BORDER} !important;
        }}
        .q-card.q-hoverable:hover {{
            box-shadow: 7px 7px 0 {_BORDER} !important;
        }}

        /* Button */
        .q-btn {{
            border-radius: 0;
            border: 2.5px solid {_BORDER};
            box-shadow: 4px 4px 0 {_BORDER};
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .q-btn:hover {{
            box-shadow: 2px 2px 0 {_BORDER};
            transform: translate(2px, 2px);
        }}

        /* Input/number/textarea — Dragon #1: replace Material underline with box */
        .q-field--standard .q-field__control::before,
        .q-field--standard .q-field__control::after {{
            display: none;
        }}
        .q-field--standard .q-field__control {{
            border: 2.5px solid {_BORDER};
            border-radius: 0;
            padding: 0 10px;
            background: {_CARD_BG};
        }}

        /* Focus ring — Dragon #3 */
        .q-btn:focus-visible,
        .q-field--focused .q-field__control,
        .q-checkbox:focus-within .q-checkbox__inner,
        .q-radio:focus-within .q-radio__bg {{
            outline: 3px solid {_ACCENT};
            outline-offset: 2px;
        }}

        /* Select dropdown items */
        .q-item {{
            border-radius: 0;
        }}

        /* Dragon #7 aesthetic layer.
           Display/positioning baseline (incl. !important fights with Quasar's .hidden)
           handled unlayered by enable_svg_control_replacement(). Below is pure brutalist
           paint — normal cascade, `nicegui` layer wins over `quasar` for non-!important. */

        /* Checkbox — square, yellow check on blue when truthy */
        .q-checkbox__inner > .q-checkbox__native {{
            width: 20px; height: 20px;
            border: 2.5px solid {_BORDER};
            background: {_CARD_BG};
            border-radius: 0;
        }}
        .q-checkbox__inner--truthy > .q-checkbox__native {{
            background: {_PRIMARY};
        }}
        .q-checkbox__inner > .q-checkbox__native::after {{
            content: '';
            display: block;
            position: absolute;
            top: 50%; left: 50%;
            width: 5px; height: 10px;
            border: solid {_ACCENT};
            border-width: 0 3px 3px 0;
            transform: translate(-50%, -60%) rotate(45deg);
            opacity: 0;
        }}
        .q-checkbox__inner--truthy > .q-checkbox__native::after {{
            opacity: 1;
        }}

        /* Radio — square (no circles in brutalism), accent dot on truthy */
        .q-radio__inner > .q-radio__native {{
            width: 20px; height: 20px;
            border: 2.5px solid {_BORDER};
            background: {_CARD_BG};
            border-radius: 0;
        }}
        .q-radio__inner--truthy > .q-radio__native {{
            background: {_PRIMARY};
        }}
        .q-radio__inner > .q-radio__native::after {{
            content: '';
            display: block;
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 8px; height: 8px;
            background: {_ACCENT};
            opacity: 0;
        }}
        .q-radio__inner--truthy > .q-radio__native::after {{
            opacity: 1;
        }}

        /* Toggle — rectangular bar with sliding rectangular knob */
        .q-toggle__inner > .q-toggle__native {{
            width: 44px; height: 22px;
            border: 2.5px solid {_BORDER};
            background: {_CARD_BG};
            border-radius: 0;
        }}
        .q-toggle__inner > .q-toggle__native::before {{
            content: '';
            display: block;
            position: absolute;
            top: 0; left: 0;
            width: 16px; height: 100%;
            background: {_BORDER};
            transition: left 0.12s ease-out;
        }}
        .q-toggle__inner--truthy > .q-toggle__native::before {{
            left: calc(100% - 16px);
            background: {_PRIMARY};
        }}

        /* Chip */
        .q-chip {{
            border-radius: 0;
            border: 2px solid {_BORDER};
            box-shadow: 3px 3px 0 {_BORDER};
            font-weight: 700;
        }}

        /* Slider */
        .q-slider__track {{
            background: {_BORDER};
            border-radius: 0;
        }}
        .q-slider__thumb {{
            border-radius: 0;
            background: {_PRIMARY} !important;
            border: 2.5px solid {_BORDER};
        }}
    ''')

    enable_svg_control_replacement()
    ensure_icon_font_fix()
