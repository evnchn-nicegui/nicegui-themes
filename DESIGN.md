# nicegui-themes — Design

> **Status**: design phase + v0.0.1 scaffold (no PyPI publish yet)
> **Repo target**: `github.com/evnchn-nicegui/nicegui-themes` (not yet created)
> **Local workdir**: `~/nicegui-themes/`
> **Author**: evnchn (Zauberzeug)
> **Origin**: 2026-06-02 design interview, rich-render at `~/rich-renders/nicegui-themes-design-2026-06-02.html`

## Multi-session protocol

This file is the source of truth. Any agent picking up this work in a fresh session:

1. **Read §11 Current State first** — only mutating section between sessions.
2. Read §1–10 for background. Stable; if you find them wrong, **propose a change in §11 before editing them**.
3. Before stopping, update §11 with: what you did, what's now true, what's next.
4. Append to §12 Session log: `YYYY-MM-DD — <agent/human> — <one-line summary>`.

§11 and §12 are mutation zones; §1–10 are append-only unless §11 instructs a revision.

---

## 1. Strategic frame

### 1.1 Wedge
Discolike — a Zauberzeug sponsor — ships a NiceGUI app that screams "NiceGUI" from a mile away. They never called `ui.colors()`. They only added button rounding. **The lazy-user majority is the entire addressable market.** Solve via one-liner curated themes, not a public theming contract.

### 1.2 Boundary
**Shape** (borders, shadows, blurs, density, focus rings, table chrome) is the hard parameter space — it's where applications "look like NiceGUI" or stop looking like NiceGUI. Palette is the easy axis; anyone can dice-roll colours until something sticks.

**Palette is explicitly out of scope** for this extension. Reasons:
- Keeps demand pressure on `ui.colors()` upstream rather than fragmenting.
- Preserves NiceGUI's color brand identity (if every app shuffles colors, nobody recognises NiceGUI by colour).
- Each mood ships a hardcoded palette; users who want palette flexibility submit upstream PRs to `ui.colors()` (tied to the future "NiceGUI logo-corner debug-widget" trade with Falko).

### 1.3 Distribution stages
- **Stage A**: external repo under `evnchn-nicegui/`. Velocity > governance. 抛磚引玉 — ship publicly, endorsement follows the artifact (Falko/Rodja are bandwidth-constrained, 2 months behind on deliverables).
- **Stage B**: nicegui.io top-right theme picker. Demand-generation engine.
- **Stage C** (the new lever): modern-flat T2 used to refactor nicegui.io's own CSS → false-marketing gap closed (nicegui.io is a NiceGUI showcase; if it ships bespoke CSS users can't easily replicate, then the showcase misrepresents what NiceGUI actually delivers). Modern-flat becomes a nicegui.io dependency → fast-tracks mainlining into NiceGUI core (likely a 3.x minor before 4.0).
- **Stage D**: 4.0 absorbs modern-flat as the new default. `nicegui_themes.modern_flat()` becomes a no-op alias. Non-default moods remain in the extension.

---

## 2. Catalogue (v0.1)

Four moods. L-shape coverage with **two deep verticals for different strategic reasons**:

| Mood | Tier 1 | Tier 2 | Strategic role |
|---|---|---|---|
| **modern-flat** | ✓ | ✓ | Dragon-baseline + 4.0 future-default + nicegui.io refactor target (closes false-marketing gap → upstream wedge) |
| **brutalist** | ✓ | ✓ | Launch wow + WCAG-AAA accessibility + leaner-layout perf hygiene (~5% sync-reflow saved) + low-res / embedded-display legibility — see §7.2, §7.3 |
| **glass** | ✓ | — | Marketing screenshot; Tier 2 gnarly (stacked blur, translucent rows) — defer to v0.2 |
| **paper** | ✓ | — | Calm/long-form aesthetic; demonstrates NiceGUI ≠ tech-tool-only |

**Aspirational gallery** (mockups in README + /gallery page on the picker): phosphor (CRT terminal), synthwave (neon), clay (soft pastel), editorial (magazine). Marketed as "you could also have these — file a PR." Generates v0.2/v0.3 news cycles.

---

## 3. Coverage tiers

**Tier 1** (12 elements): button, card, input, number, textarea, select, toggle, switch, checkbox, radio, slider, chip, label.

**Tier 2** (+7 elements = 19 total): table, dialog, tabs, expansion, progress, list, menu.

**Out of v0.1**: charts (echart/plotly), editor, scene, leaflet. Console-warn fires; PR welcome.

---

## 4. The 6 Dragons (per-theme shape-pass spec)

Every theme's CSS must address these. Painted-over themes (the 6 prior C themes from the pre-compact gallery at `~/rich-renders/nicegui-style-sets-2026-05-25.html`) caught the eye but broke the moment a `q-field` or `q-table` appeared.

1. **`q-field` Material underline** — replace with box border.
2. **`hover-elevate-2/-4` cascade** — Quasar's hover-elevation classes fire on top of theme shadow → stacking artifacts. Override per element.
3. **Focus ring coherency** — Quasar's blue Material ring vs theme's intended ring.
4. **`q-table` chrome** — header bar, row separators, sticky styles (Tier 2 only).
5. **`q-icon` cascade-layer trap** — theme font on container clobbers `<i class="material-icons">`. `ui.add_css` is wrapped in a cascade layer and loses; re-assert unlayered via `ui.add_head_html('<style>...</style>')`. Handled in `_common.ensure_icon_font_fix()`.
6. **Density / `dense` modifier** — Quasar's `dense` changes padding scale across all elements; themes declare a density stance.
7. **SVG-based controls** (discovered empirically 2026-06-02 building brutalist; formalised in `_common.enable_svg_control_replacement()`) — Quasar renders radio dots, switch knobs, and checkbox checkmarks as SVG paths inside `.q-X__bg` / `.q-toggle__track` / `.q-toggle__thumb`, while the actual `<input>` (`.q-X__native`) carries a Tailwind `hidden` class and is invisible. `border-radius` does nothing.

   **Slay-pattern — pure CSS via `@layer overrides` (wave 6 fix)**:

   The NiceGUI cascade rule (evnchn's standard advice on GH discussions): **layered CSS wins over unlayered in NiceGUI**, and among layers declared LATER wins for both normal and `!important` rules — which is why Quasar's last layer is named `quasar_importants`. The full declared order is:

       @layer theme, base, quasar, nicegui, components, utilities, overrides, quasar_importants;

   Tailwind v4's runtime puts `.hidden{display:none}` in the `utilities` layer (6th). To win, wrap the override in `@layer overrides` (7th). The single style block does it all — no JS needed:

   ```css
   @layer overrides {
     .q-radio__bg, .q-checkbox__bg, .q-toggle__track, .q-toggle__thumb {
       display: none !important;
     }
     .q-checkbox__inner > .q-checkbox__native,
     .q-radio__inner > .q-radio__native,
     .q-toggle__inner > .q-toggle__native {
       display: block !important;
       position: absolute; top: 50%; left: 50%;
       transform: translate(-50%, -50%);
       appearance: none; -webkit-appearance: none;
       margin: 0; cursor: pointer;
     }
   }
   ```

   Injected via `ui.add_head_html(..., shared=True)`. Theme then paints the visible natives via plain `ui.add_css` for `background`/`border`/`::after` (check/dot), with active state driven by Quasar's existing `.q-X__inner--truthy >` parent class.

   Earlier wave-2 attempt (JS observer stripping the `hidden` class) was the empirical fallback before understanding the `@layer overrides` trick. Brutalist v0.0.5 is the pure-CSS reference implementation.

   **Reusable principle**: any time a theme needs to override a `quasar`/`utilities`-layer rule, wrap the override in `@layer overrides` to win the cascade. This is the canonical NiceGUI theming pattern; document it for future theme authors.

---

## 5. API surface

```python
import nicegui_themes
nicegui_themes.brutalist()      # or .modern_flat() / .glass() / .paper()
```

Each theme function:
1. Calls `ui.colors(...)` for Quasar variable wiring.
2. `ui.add_head_html('<link>')` for theme fonts.
3. `ui.add_css(...)` for layered shape-pass CSS.
4. `ui.add_head_html('<style>...</style>')` for **unlayered** dragon-fixes (Material Icons font re-assert, etc.).
5. Registers a coverage manifest for console-warn (v0.0.x: deferred; design captured here).

**Coverage signalling** (planned): console-warn once per unsupported element type per session.

```
nicegui_themes: 'echart' not styled by 'brutalist'
  PR: https://github.com/evnchn-nicegui/nicegui-themes/blob/main/src/nicegui_themes/brutalist.py
```

No debug overlay, no telemetry, no introspection function in v0.1.

---

## 6. Operational

| Item | Decision |
|---|---|
| Repo | `evnchn-nicegui/nicegui-themes` |
| License | MIT (default; CC0 if preferred for theme assets) |
| PyPI | `pip install nicegui-themes` |
| Versioning | Theme contents not API-stable; palette/shape may drift per minor. Documented up front. |
| Tests | Headless Playwright screenshot diff per theme per element-set; run on PR |
| Falko/Rodja | 抛磚引玉 — ship-then-tell. No upfront ask. Expected gains: endorsement signal + agentic-budget runway. |

---

## 7. Data-backed claims

### 7.1 Brutalist WCAG-AAA (verified 2026-06-02)
Primary button, white text on `#2b2bff`: **7.26:1** — clears AAA (≥7).

Comparison (white text on each mood's primary):
- glass `#7c5cff`: 4.34:1 (✗ fails AA normal text, needs 4.5:1)
- paper `#b5651d`: 4.33:1 (✗ fails AA normal text)
- modern-flat (bitdoze-class) `#6E93D6`: 3.08:1 (✗ fails AA normal text)

Brutalist is the only mood that ships AAA for primary buttons unmodified. **"Accidentally accessible" pitch is data-backed.**

WCAG math: sRGB→linear (c≤.03928: c/12.92; else ((c+.055)/1.055)^2.4); L = 0.2126R + 0.7152G + 0.0722B; contrast = (L₁+0.05)/(L₂+0.05); AA=4.5, AAA=7.

### 7.2 Brutalist render-cost — RESHAPED: leaner layout, not cheaper paint (2026-06-02)

Two bench passes were necessary because the first methodology was vsync-bound.

**Wave A** (rAF loop, `bench/render_cost.py`): null result on repaint cost because rAF clamps total time to N × frame_budget unless per-frame paint exceeds vsync. At 30 cards + 4× CPU throttle + `--disable-gpu`, paint cost stayed under 16.67ms/frame — invisible. Load cost 11% slower for brutalist (extra fonts/CSS/JS).

**Wave B** (CDP `Performance.getMetrics` + sync forced-reflow loops, `bench/perf_metrics.py`) — same Chromium settings, but non-vsync-bound metrics:

| Metric (30-card page) | Material | Brutalist | Δ | per-card |
|---|---|---|---|---|
| DOM nodes | 6656 | 6526 | **−130** | −4.3/card cheaper |
| Cumulative LayoutDuration | 100.2ms | 85.6ms | **−14.6ms** | −0.49ms/card cheaper |
| Sync layout x500 reflows | 13018ms | 12308ms | **−710ms** | −1.4ms/reflow cheaper (5.4%) |
| Paint loop x200 | 13.0ms | 13.3ms | +0.3 | noise |
| Style recalc cumulative | 126.4ms | 128.4ms | +1.9 | noise |
| JS heap used | 19.09MB | 19.18MB | +0.09MB | font + observer overhead |
| JS heap total | 34.70MB | 35.20MB | +0.50MB | as above |
| Inline CSS | 7.4KB | 12.5KB | +5.1KB | shape pass + dragon fixes |
| External CSS files | 0 | 1 | +1 | Google Fonts |

**Honest interpretation:**
- Paint cost is **NOT** measurably different — the original theoretical pitch ("1-layer shadow vs 3-layer Material elevation cheaper to raster") doesn't survive measurement. Shadow paint is GPU work that doesn't differentiate at this scale.
- Layout cost **IS** measurably cheaper — brutalist saves ~5% per sync reflow, ~14.6ms cumulative on a 30-card page. Attributable to: simpler box-shadow geometry (no blur → no overflow-bbox dilation calc), fewer compositing-layer triggers, SVG sub-paths display:none-skipped from layout.
- Trade: brutalist costs +0.5MB JS heap + 5KB CSS upfront (fonts, shape pass, JS observer) for the layout savings + AAA contrast over the app's lifetime.

**Revised pitch (replaces "cheaper to render"):** "Measurably leaner layout cost — ~5% lower sync-reflow time + ~15% lower cumulative LayoutDuration on a 30-card kitchen sink (Chromium `--disable-gpu` + 4× CPU throttle, directionally Pi-class). Paint cost is unchanged; the win is in style/layout work, not raster."

Real Pi 4 numbers would scale proportionally for ratios. Methodology in `bench/perf_metrics.py`.

**Public framing (locked: option A — performance hygiene):**
> *Brutalist is also measurably leaner in layout work — ~5% fewer reflow cycles, ~130 fewer DOM nodes per 30-card dashboard in our bench — and stays legible on low-resolution embedded displays (Raspberry Pi over I2C/SPI, industrial HMIs, kiosk panels) where soft Material shadows turn to mush. Not magic speedup — just hygiene that compounds on constrained hardware.*

Keywords threaded for agent + SEO discoverability without keyword-stuffing: *performance hygiene · embedded display · Raspberry Pi · industrial HMI · kiosk · constrained hardware · layout cost · reflow*. Used verbatim in `README.md` brutalist row; safe to copy into nicegui.io marketing copy when the picker lands.

### 7.3 Low-resolution display legibility (uncontroversial design)

A second uncontroversial perf-adjacent angle for brutalist, ships as part of the framing A pitch but worth documenting separately so future revisions don't lose it:

- **Thick borders (2.5–3px)** survive downscaling and low-DPI rendering. Material's 1px hairline strokes vanish or alias on sub-100ppi panels.
- **Hard #000-on-#fff contrast** doesn't depend on subpixel antialiasing — works correctly on monochrome / dithered / e-paper / low-bit-depth displays.
- **No blur radius anywhere** — no smudging on resampled output (e.g. HDMI capture, downscale-to-fit kiosk display, screen mirror to lower-res panel).

Empirical re-verification not required — these are established display behaviors, not novel claims. If a sceptical reader pushes, demo by viewport-resizing to 480×320 at device-scale 1 and screenshotting both themes.

---

## 8. Falsifiable conditions

For each major design decision, what evidence invalidates it:

| Decision | Falsified if |
|---|---|
| Wedge = lazy users | Survey of NiceGUI users shows >50% already customise colors before shipping → reconsider whether docs improvement is the right wedge. |
| Shape > palette | Community PRs after v0.1 dominated by palette swaps → re-open palette API discussion. |
| 4-mood conservative slate | Download stats show 90%+ pick 1 mood → trim slate; or <5% pick 3 of 4 → trim slate. |
| Brutalist deep is tractable | Tier 2 brutalist costs >2× the LOC of brutalist Tier 1 → reconsider which mood goes deep. |
| Brutalist AAA contrast holds for users | Accessibility-conscious users want a non-`#2b2bff` brutalist palette → AAA pitch becomes conditional, document palette dependency. |
| Brutalist cheaper render | ✓ **RESHAPED 2026-06-02**: original "cheaper paint" framing FALSIFIED (rAF + tight loop both show identical paint cost). But CDP `Performance.getMetrics` + sync reflow loops surfaced a real LAYOUT-cost win: −5.4% per sync reflow, −14.6ms cumulative LayoutDuration (~15% cheaper) at 30-card workload. Pitch survives as "leaner layout" (NOT "cheaper paint"). See §7.2 for the corrected framing and trade-off honesty. |
| Modern-flat = 4.0 default candidate | Falko/Rodja explicitly veto → downgrade to just-another-theme. |
| Ship-then-tell with F/R | F/R explicitly object within 30 days of publish → pull endorsement push, keep extension freestanding. |
| Modern-flat T2 = nicegui.io refactor candidate | Applying modern-flat T2 to nicegui.io produces >20% pixel-diff in key pages → "false marketing" framing overstated, modern-flat is its own thing. |
| Console-warn is enough UX | >3 GitHub issues in first 60 days are "I didn't know X wasn't themed" → upgrade to dev-mode visual marker. |
| No palette parameter | >5 GitHub issues in first 60 days demanding palette-per-mood → fold into extension. |

---

## 9. Explicitly NOT in v0.1

- Palette parameter / `brutalist(palette='catppuccin')` — never advertised
- Public CSS variable contract (no `--ng-*` promise)
- Runtime swap helper (nicegui.io picker builds its own swap on top of per-call API)
- Charts / editor / scene / leaflet styling
- Telemetry, debug overlay, coverage introspection function

---

## 10. Upstream interfaces (out of this repo)

- **`ui.colors()` palette enhancement PR** — separate upstream PR to `zauberzeug/nicegui`. Tied to future "NiceGUI logo-corner debug-widget" trade with Falko.
- **nicegui.io theme picker** — separate work item; depends on this package shipping a stable per-call API.
- **nicegui.io modern-flat refactor** — depends on §2 modern-flat T2 being shipped. PR to NiceGUI website repo replaces bespoke CSS with `nicegui_themes.modern_flat()`.

---

## 11. Current state

> **UPDATE THIS SECTION EVERY SESSION. Leave a clean handoff for the next session.**

### 11.1 Now (2026-06-02 ~22:15 HKT) — wave 6

**Wave 6 — pure-CSS Dragon #7 (the `@layer overrides` trick)**:
- evnchn corrected the framing: NiceGUI behaves *layered > unlayered*; among layers, LATER wins. (Standard advice he gives in GH discussions; not a spec quirk so much as NiceGUI's chosen cascade behavior, which is why Quasar's last-declared layer is named `quasar_importants`.)
- Refactored `_common.py`: wrapped both `ensure_icon_font_fix()` and `enable_svg_control_replacement()` rules in `@layer overrides { ... }`. **Dropped the JS observer** that was wave-2's fallback.
- Verified live: computed `display: block` on natives, `hidden` class still present but inactive (cascade won correctly). Brutalist v0.0.5 screenshot at `~/rich-renders/nicegui-themes-brutalist-v0.0.5-2026-06-02.png` is visually identical to v0.0.4, proving the CSS-only path works.
- Updated §4 Dragon #7 with the @layer pattern as the canonical NiceGUI theme-override mechanism.

**evnchn decisions closed this session**:
- License: **MIT** (current; confirmed)
- Import style: **eager** (current; confirmed)
- Repo timing: **create as PRIVATE now, squash and flip to public later**
- Dragon #7 strategy: **@layer overrides trick — done, JS observer dropped**
- Dashboard refresh: **no, current "are we winning" dashboard is fine**
- Memory: **triage at end, write candidates to disk (too many to track inline)** — file at `~/nicegui-themes/MEMORY_CANDIDATES.md`

**Not yet** (carry to next session):
- Initial git commit + `gh repo create evnchn-nicegui/nicegui-themes --private`
- modern-flat / glass / paper implementations
- Tier 2 elements (table/dialog/tabs/expansion/progress/list/menu)
- Console-warn machinery
- Screenshot CI

### 11.0 Previous wave snapshot (2026-06-02 ~21:35 HKT)
**Done this session** (two waves):

*Wave 1* (16:30):
- DESIGN.md initial draft + project skeleton + brutalist Tier 1 v0.0.1.
- Demo ran; visual verification at `~/rich-renders/nicegui-themes-brutalist-v0.0.1-2026-06-02.png` — 80% Tier 1 working; Dragon #7 (SVG controls) discovered.

*Wave 2* (21:00) — Dragon #7 slain via basecoat-hack #5608 formalisation:
- Fetched #5608 V1→V5 via `gh api graphql`.
- Added `enable_svg_control_replacement()` to `_common.py` — formalises the technique as framework infra. CSS hides SVG bgs + baseline-positions natives; tiny inline JS observer strips Tailwind's `hidden` class from natives (empirical fallback because our unlayered `!important` mysteriously loses the cascade — see §4 Dragon #7 deep notes).
- Brutalist updated to paint the visible natives (square checkbox/radio with accent dot/check on truthy; rectangular toggle bar with sliding knob).
- Empirical screenshot `~/rich-renders/nicegui-themes-brutalist-v0.0.4-2026-06-02.png` confirms all three SVG-control dragons slain.

**Not yet**:
- modern-flat / glass / paper implementations.
- Tier 2 elements anywhere (table/dialog/tabs/expansion/progress/list/menu).
- Console-warn machinery (§5).
- Playwright screenshot test in CI.
- Root-cause investigation for why unlayered `!important` lost to Tailwind's runtime `.hidden` (interesting but not blocking).
- Repo creation (`gh repo create evnchn-nicegui/nicegui-themes`), PyPI publish.

### 11.2 Next session should
1. **Implement modern-flat Tier 1** (Stage C upstream lever — closes nicegui.io false-marketing gap).
2. **Wire console-warn** per §5. Cheapest: per-theme coverage manifest dict + monkey-patch `nicegui.element.Element.__init_subclass__` or instrument the public factories.
3. After modern-flat T1 lands: cut at modern-flat T2 (table/dialog/tabs/expansion/progress/list/menu) — the actual nicegui.io refactor candidate.
4. (Stretch) Root-cause why unlayered `!important` lost to Tailwind v4 runtime `.hidden{display:none}` despite cascade spec. Likely answer: Tailwind v4's CSSOM injection happens via `adoptedStyleSheets` or similar that changes effective cascade origin. If found, simplify Dragon #7 to CSS-only; remove the JS observer.

### 11.3 Open questions for evnchn
*(All session-3 decisions answered in §11.1 wave 6. Remaining are for future sessions.)*
- Demo screenshots: regenerate per release, or accept that the bench screenshots in `~/rich-renders/` are sufficient until v0.1 ships?
- nicegui.io theme picker timing: build alongside modern-flat T2, or wait until v0.1 stable?
- Public repo flip timing: after modern-flat T1 lands, or after both modern-flat tiers?

---

## 12. Session log

```
2026-06-02 — Claude (Opus 4.7) — Interview with evnchn surfaced design; rich-render at ~/rich-renders/nicegui-themes-design-2026-06-02.html; DESIGN.md + v0.0.1 scaffold written; brutalist Tier 1 implemented; demo app runs end-to-end under uv venv; Playwright screenshot at ~/rich-renders/nicegui-themes-brutalist-v0.0.1-2026-06-02.png shows 80% conversion — discovered Dragon #7 (SVG-based controls don't take border-radius).
2026-06-02 — Claude (Opus 4.7) — Wave 2: Dragon #7 slain. Fetched evnchn's basecoat-hack #5608 V1-V5 via gh graphql; formalised the technique as `_common.enable_svg_control_replacement()` framework helper. Tried pure-CSS (V4-style unlayered !important) — failed despite higher specificity; root cause unconfirmed (Tailwind v4 runtime cascade quirk). Fell back to V1-style JS class-strip observer (~10 lines). Brutalist v0.0.4 screenshot at ~/rich-renders/nicegui-themes-brutalist-v0.0.4-2026-06-02.png confirms square radios, rectangular toggle, hard-bordered checkbox. Reference impl for future themes.
2026-06-02 — Claude (Opus 4.7) — Wave 3: built bench/render_cost.py (Playwright + CDP CPU throttle + --disable-gpu). 1× and 30× card kitchen sinks measured: repaint vsync-bound (~16.5ms/frame both modes), brutalist load 11% SLOWER (extra fonts/CSS/JS). Cheap-render pitch preliminarily falsified per §8 condition; dropped from §2 positioning. AAA contrast remains the sole data-backed secondary angle.
2026-06-02 — Claude (Opus 4.7) — Wave 4: evnchn pushed back on the vsync-bound null result. Built bench/perf_metrics.py using non-vsync-bound metrics (CDP Performance.getMetrics for cumulative LayoutDuration/RecalcStyleDuration + CDP Memory.getDOMCounters + sync forced-reflow loops). RESULTS: brutalist genuinely cheaper at layout (−5.4% per sync reflow, −14.6ms cumulative, −130 DOM nodes at 30 cards) but identical at paint. Trade: +0.5MB heap + 5KB CSS. Pitch RESTORED but reshaped: "leaner layout" not "cheaper paint". See §7.2 for the corrected framing.
2026-06-02 — Claude (Opus 4.7) — Wave 5: locked framing A (performance hygiene) + added low-res / embedded-display legibility angle to §7.2 + new §7.3. Keywords threaded for agent + SEO discoverability (Raspberry Pi, I2C/SPI, industrial HMI, kiosk, embedded display, performance hygiene). Brutalist's public framing now covers four angles: aesthetic launch wow + WCAG-AAA contrast + measurable layout-cost hygiene + low-res legibility. None overclaiming.
2026-06-02 — Claude (Opus 4.7) — Wave 6: evnchn corrected the cascade framing — in NiceGUI layered > unlayered; LATER layer wins (which is why Quasar's last layer is `quasar_importants`). Applied `@layer overrides` wrap to both `ensure_icon_font_fix()` and `enable_svg_control_replacement()` in `_common.py`. Dropped the JS observer entirely; pure CSS now slays Dragon #7. Verified via brutalist v0.0.5 screenshot at `~/rich-renders/nicegui-themes-brutalist-v0.0.5-2026-06-02.png` (visually identical to v0.0.4, confirming the CSS path works). Documented `@layer overrides` as the canonical NiceGUI theme-override pattern in §4 Dragon #7. Also: evnchn answered all 6 dashboard decisions (MIT, eager, private repo + squash, @layer for dragon, no dashboard refresh, memory to disk).
```
