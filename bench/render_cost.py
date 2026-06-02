"""Render-cost benchmark for the brutalist "cheaper paint" pitch.

Methodology:
- Two demo servers: Quasar Material defaults (THEME=default) vs brutalist (THEME=brutalist).
- Chromium launched with `--disable-gpu` to force CPU compositing — exposes
  shadow rasterisation cost that GPU compositors hide on a beefy machine.
- CDP `Emulation.setCPUThrottlingRate` set to 4x to approximate Pi-class CPU.
- Repaint cost measured by forcing N transform-toggles inside a rAF loop and
  timing the total ms.
- Initial-load `domContentLoaded` + `load` event times captured too.

Output: ratio brutalist/material per metric. <1 means brutalist cheaper.

Caveats:
- Mac CPU at 4x throttle ≠ actual Pi 4. Directionally representative only.
- macOS + software composition has different memory-bandwidth profile than Pi VC6.
- Re-run on real Pi 4 / Q506 for a "1.8x" type production claim.

Run:
    cd ~/nicegui-themes
    .venv/bin/python bench/render_cost.py
"""
import os
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / '.venv/bin/python'
APP = ROOT / 'demo/app.py'


def start_server(theme: str, port: int, count: int = 1) -> subprocess.Popen:
    env = {**os.environ, 'THEME': theme, 'PORT': str(port), 'COUNT': str(count)}
    proc = subprocess.Popen(
        [str(PY), str(APP)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(ROOT),
    )
    return proc


def wait_ready(port: int, timeout: float = 10.0) -> None:
    import socket
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(('127.0.0.1', port))
                return
            except OSError:
                time.sleep(0.25)
    raise RuntimeError(f'server on :{port} did not come up within {timeout}s')


def measure(playwright, url: str, cpu_throttle: int, iterations: int) -> dict:
    browser = playwright.chromium.launch(args=['--disable-gpu', '--no-sandbox'])
    ctx = browser.new_context(viewport={'width': 1024, 'height': 900})
    page = ctx.new_page()
    client = ctx.new_cdp_session(page)
    client.send('Emulation.setCPUThrottlingRate', {'rate': cpu_throttle})

    t_nav_start = time.perf_counter()
    page.goto(url, wait_until='networkidle')
    t_nav = (time.perf_counter() - t_nav_start) * 1000

    # Wait for theme assets (fonts) to settle
    page.evaluate(
        "async () => { try { await document.fonts.ready; } catch(e){} }"
    )
    page.wait_for_timeout(500)

    nav = page.evaluate('''() => {
      const n = performance.getEntriesByType('navigation')[0];
      return {
        dcl: n.domContentLoadedEventEnd - n.startTime,
        load: n.loadEventEnd - n.startTime,
      };
    }''')

    # Repaint cost: toggle a transform invalidating compositing, force layout,
    # repeat N times in a rAF loop. Total ms = paint+layout cost x N.
    repaint_ms = page.evaluate(f'''(n) => new Promise(resolve => {{
        const t0 = performance.now();
        let i = 0;
        function tick() {{
            document.body.style.transform = (i % 2)
                ? 'translateZ(1px) scale(1.0001)'
                : 'translateZ(0) scale(1)';
            void document.body.offsetHeight;  // force layout flush
            i++;
            if (i < n) requestAnimationFrame(tick);
            else resolve(performance.now() - t0);
        }}
        requestAnimationFrame(tick);
    }})''', iterations)

    browser.close()
    return {
        'nav_total_ms': t_nav,
        'dcl_ms': nav['dcl'],
        'load_ms': nav['load'],
        'repaint_ms': repaint_ms,
        'repaint_per_frame_ms': repaint_ms / iterations,
    }


def main() -> None:
    cpu_throttle = int(os.environ.get('CPU_THROTTLE', '4'))
    iterations = int(os.environ.get('ITERATIONS', '120'))
    runs = int(os.environ.get('RUNS', '3'))
    card_count = int(os.environ.get('CARDS', '30'))

    print(f'CPU throttle: {cpu_throttle}x  |  iterations: {iterations}  |  '
          f'runs: {runs}  |  cards: {card_count}')
    print('Chromium: --disable-gpu (software composition)')
    print()

    p_def = start_server('default', 8100, count=card_count)
    p_brt = start_server('brutalist', 8101, count=card_count)
    try:
        wait_ready(8100)
        wait_ready(8101)
        print('Both servers up; warming caches with one untimed pass...')
        with sync_playwright() as pw:
            measure(pw, 'http://127.0.0.1:8100/', cpu_throttle, 10)
            measure(pw, 'http://127.0.0.1:8101/', cpu_throttle, 10)

            results = {'default': [], 'brutalist': []}
            for run in range(runs):
                print(f'\n=== Run {run + 1}/{runs} ===')
                d = measure(pw, 'http://127.0.0.1:8100/', cpu_throttle, iterations)
                b = measure(pw, 'http://127.0.0.1:8101/', cpu_throttle, iterations)
                results['default'].append(d)
                results['brutalist'].append(b)
                print(f'  Material default:  load {d["load_ms"]:7.1f}ms  '
                      f'repaint {d["repaint_ms"]:7.1f}ms ({d["repaint_per_frame_ms"]:.2f}ms/frame)')
                print(f'  Brutalist:         load {b["load_ms"]:7.1f}ms  '
                      f'repaint {b["repaint_ms"]:7.1f}ms ({b["repaint_per_frame_ms"]:.2f}ms/frame)')

        # Aggregate
        def med(vals):
            s = sorted(vals)
            return s[len(s) // 2]

        d_load = med([r['load_ms'] for r in results['default']])
        b_load = med([r['load_ms'] for r in results['brutalist']])
        d_paint = med([r['repaint_ms'] for r in results['default']])
        b_paint = med([r['repaint_ms'] for r in results['brutalist']])

        print('\n=== Median across runs ===')
        print(f'  load        material {d_load:7.1f}ms  brutalist {b_load:7.1f}ms  '
              f'ratio b/m = {b_load / d_load:.2f}  ({"brutalist cheaper" if b_load < d_load else "material cheaper"})')
        print(f'  repaint     material {d_paint:7.1f}ms  brutalist {b_paint:7.1f}ms  '
              f'ratio b/m = {b_paint / d_paint:.2f}  ({"brutalist cheaper" if b_paint < d_paint else "material cheaper"})')
        delta = (1 - b_paint / d_paint) * 100
        print(f'\n  brutalist paint cost = {delta:+.0f}% vs material baseline'
              f'  (negative = brutalist wins)')
    finally:
        p_def.terminate()
        p_brt.terminate()
        try:
            p_def.wait(timeout=2)
        except subprocess.TimeoutExpired:
            p_def.kill()
        try:
            p_brt.wait(timeout=2)
        except subprocess.TimeoutExpired:
            p_brt.kill()


if __name__ == '__main__':
    main()
