# nicegui-themes

Curated shape-pass themes for [NiceGUI](https://nicegui.io) — performance hygiene, embedded-display friendly, WCAG-AAA contrast where it counts.

> **Status**: v0.0.1 · pre-PyPI · brutalist Tier 1 shipped, more tiers in flight.

```python
import nicegui_themes
nicegui_themes.brutalist()
```

See `DESIGN.md` for the strategic frame (wedge, distribution stages, falsifiable conditions, benchmark methodology) and `demo/app.py` for the kitchen-sink demo. `bench/perf_metrics.py` documents the perf claims.

## Themes (v0.1 catalogue)

| Mood | Coverage | Pitch |
|---|---|---|
| **modern-flat** | Tier 1 + 2 | Dragon-baseline. The look NiceGUI default *should* have been. 4.0 future-default candidate. |
| **brutalist** | Tier 1 + 2 | Bold borders, hard offset shadows. WCAG-AAA verified (7.26:1 on primary). Measurably leaner layout work (~5% lower reflow cost in our bench) and stays legible on low-resolution embedded displays — Raspberry Pi over I2C/SPI, industrial HMIs, kiosk panels — where Material's soft shadows turn to mush. |
| **glass** | Tier 1 | Backdrop-blur cards + gradient body. Marketing screenshot. |
| **paper** | Tier 1 | Calm/long-form, serif body, terracotta primary. |

## Aspirational gallery

Aspirational — file a PR to promote one to a shipped theme: phosphor (CRT terminal), synthwave (neon), clay (soft pastel), editorial (magazine).
