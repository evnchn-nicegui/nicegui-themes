"""Brutalist theme — Tier 1 coverage.

**SHAPE ONLY.** Per DESIGN.md §1.2: palette is explicitly out of scope for
`nicegui-themes`. Brutalist paints thick black borders, zero radius, and hard
offset shadows ON TOP OF whatever palette NiceGUI's `ui.colors()` defaults
provide — Quasar Material blue (#1976D2) primary by default, the user's
choice if they've called `ui.colors(...)` themselves. The shape is the
theme; the palette stays NiceGUI's.

Border/structure colors are taken from a NiceGUI-aware accent vocabulary:
- Border lines + body chrome: `#000` (brutalist signature; the only hardcoded
  colour). In dark-mode contexts a user can override `--ng-brutalist-border`
  to white.
- Truthy fills (checkbox bg, radio bg, toggle knob-on, slider thumb):
  `var(--q-primary)` — respects the live NiceGUI palette.
- Active focus ring: `var(--q-accent)` — same.
- Truthy checkmark / radio dot ink: `white` (legible on every Quasar default
  primary).

Tier 1 surface: button, card, input/number/textarea, select, toggle/switch/
checkbox/radio, slider, chip, label.

Tier 2 surface (table, dialog, tabs, expansion, progress, list, menu) lands in the next wave.
"""
from nicegui import ui

from nicegui_themes._common import enable_svg_control_replacement, ensure_icon_font_fix


# The only hardcoded colour in this theme — overridable via CSS custom property
# `--ng-brutalist-border` if the user needs it (e.g. dark mode).
_BORDER = 'var(--ng-brutalist-border, #000)'


def apply() -> None:
    """Apply the brutalist Tier 1 shape pass. Palette stays NiceGUI's native."""
    # NOTE: no `ui.colors(...)` call. Palette is out of scope per DESIGN.md §1.2.

    ui.add_head_html(
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">'
    )

    ui.add_css(f'''
        /* Typography — note: no body background override; let NiceGUI native paint it */
        body {{
            font-family: "Space Grotesk", sans-serif;
        }}

        /* Card — Dragon #2: kill hover-elevate by pinning the shadow.
           NOTE: no card background override; Quasar default white in light mode,
           dark grey in dark mode — brutalist border + shadow keeps it distinct. */
        .q-card {{
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
        }}

        /* Focus ring — Dragon #3.  Uses Quasar's live accent variable. */
        .q-btn:focus-visible,
        .q-field--focused .q-field__control,
        .q-checkbox:focus-within .q-checkbox__inner,
        .q-radio:focus-within .q-radio__bg {{
            outline: 3px solid var(--q-accent);
            outline-offset: 2px;
        }}

        /* Select dropdown items */
        .q-item {{
            border-radius: 0;
        }}

        /* Dragon #7 aesthetic layer.  Display/positioning baseline handled by
           enable_svg_control_replacement() (in @layer overrides).  Below is
           pure brutalist paint — palette-respecting, only borders are black. */

        /* Checkbox — square box, q-primary fill on truthy, white check mark */
        .q-checkbox__inner > .q-checkbox__native {{
            width: 20px; height: 20px;
            border: 2.5px solid {_BORDER};
            border-radius: 0;
        }}
        .q-checkbox__inner--truthy > .q-checkbox__native {{
            background: var(--q-primary);
            border-color: var(--q-primary);
        }}
        .q-checkbox__inner > .q-checkbox__native::after {{
            content: '';
            display: block;
            position: absolute;
            top: 50%; left: 50%;
            width: 5px; height: 10px;
            border: solid white;
            border-width: 0 3px 3px 0;
            transform: translate(-50%, -60%) rotate(45deg);
            opacity: 0;
        }}
        .q-checkbox__inner--truthy > .q-checkbox__native::after {{
            opacity: 1;
        }}

        /* Radio — square (no circles), q-primary fill on truthy, white dot */
        .q-radio__inner > .q-radio__native {{
            width: 20px; height: 20px;
            border: 2.5px solid {_BORDER};
            border-radius: 0;
        }}
        .q-radio__inner--truthy > .q-radio__native {{
            background: var(--q-primary);
            border-color: var(--q-primary);
        }}
        .q-radio__inner > .q-radio__native::after {{
            content: '';
            display: block;
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 8px; height: 8px;
            background: white;
            opacity: 0;
        }}
        .q-radio__inner--truthy > .q-radio__native::after {{
            opacity: 1;
        }}

        /* Toggle — rectangular bar with sliding rectangular knob */
        .q-toggle__inner > .q-toggle__native {{
            width: 44px; height: 22px;
            border: 2.5px solid {_BORDER};
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
            background: var(--q-primary);
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
            background: var(--q-primary) !important;
            border: 2.5px solid {_BORDER};
        }}
    ''')

    enable_svg_control_replacement()
    ensure_icon_font_fix()
