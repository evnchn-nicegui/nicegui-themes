"""Deeper render-cost probe: bypass rAF/vsync clamping.

vsync-bound rAF loops can't see paint-cost differences below the frame budget.
This bench uses metrics that are NOT vsync-clamped:

1. DOM node count, document count           (CDP Memory.getDOMCounters)
2. JS heap usage                            (CDP Performance.getMetrics → JSHeapUsedSize)
3. Cumulative layout duration               (CDP Performance.getMetrics → LayoutDuration)
4. Cumulative style recalc duration         (CDP Performance.getMetrics → RecalcStyleDuration)
5. Sync forced-reflow loop                  (tight for-loop, no rAF, paint-budget exceeded)
6. Paint loop (bg color toggle)             (forces full-page repaint, no rAF clamp)
7. Stylesheet count + total CSS bytes       (document.styleSheets iteration)

Output: side-by-side material vs brutalist, with per-card normalisation where
the page is 30 stacked sinks. The signal "tiny but real" lives in items 1-5.

Run:
    cd ~/nicegui-themes
    .venv/bin/python bench/perf_metrics.py
"""
import os
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / '.venv/bin/python'
APP = ROOT / 'demo/app.py'


def start_server(theme: str, port: int, count: int) -> subprocess.Popen:
    env = {**os.environ, 'THEME': theme, 'PORT': str(port), 'COUNT': str(count)}
    return subprocess.Popen(
        [str(PY), str(APP)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(ROOT),
    )


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


def measure(pw, url: str, cpu_throttle: int) -> dict:
    browser = pw.chromium.launch(args=['--disable-gpu', '--no-sandbox'])
    ctx = browser.new_context(viewport={'width': 1024, 'height': 900})
    page = ctx.new_page()
    client = ctx.new_cdp_session(page)
    client.send('Performance.enable')
    client.send('Emulation.setCPUThrottlingRate', {'rate': cpu_throttle})

    page.goto(url, wait_until='networkidle')
    page.evaluate("async () => { try { await document.fonts.ready; } catch(e){} }")
    page.wait_for_timeout(500)

    # 1+2. DOM + heap via CDP
    dom_counters = client.send('Memory.getDOMCounters')
    metrics_baseline = {m['name']: m['value']
                        for m in client.send('Performance.getMetrics')['metrics']}

    # 3. Sync forced-reflow loop (no rAF — measures layout cost directly)
    layout_ms = page.evaluate('''(N) => {
        const t0 = performance.now();
        const root = document.documentElement;
        for (let i = 0; i < N; i++) {
            root.style.setProperty('--bench-dummy', i);
            void root.offsetHeight;  // force layout flush
        }
        return performance.now() - t0;
    }''', 500)

    # 4. Paint loop — toggle a property that invalidates paint but not layout
    # background-color change on body forces a full-page repaint, no rAF clamp
    paint_ms = page.evaluate('''(N) => {
        const orig = document.body.style.backgroundColor;
        const t0 = performance.now();
        for (let i = 0; i < N; i++) {
            document.body.style.backgroundColor = (i % 2) ? '#abcdef' : '#fedcba';
            void document.body.offsetHeight;
        }
        document.body.style.backgroundColor = orig;
        return performance.now() - t0;
    }''', 200)

    # 5. Stylesheet count + size estimate
    css = page.evaluate('''() => {
      let count = 0, bytes = 0;
      for (const s of document.querySelectorAll('style')) {
        count++;
        bytes += (s.textContent || '').length;
      }
      // external sheets — accessible cssText would require fetch; just count
      const links = document.querySelectorAll('link[rel=stylesheet]').length;
      return {inline_count: count, inline_bytes: bytes, external_count: links};
    }''')

    # Capture post-work metrics again (to see if our loops produced different CDP deltas)
    metrics_post = {m['name']: m['value']
                    for m in client.send('Performance.getMetrics')['metrics']}

    browser.close()

    return {
        'nodes': dom_counters['nodes'],
        'documents': dom_counters['documents'],
        'js_event_listeners': dom_counters['jsEventListeners'],
        'js_heap_used_MB': metrics_baseline.get('JSHeapUsedSize', 0) / (1024 * 1024),
        'js_heap_total_MB': metrics_baseline.get('JSHeapTotalSize', 0) / (1024 * 1024),
        'cdp_Layout_ms_baseline':
            metrics_baseline.get('LayoutDuration', 0) * 1000,
        'cdp_RecalcStyle_ms_baseline':
            metrics_baseline.get('RecalcStyleDuration', 0) * 1000,
        'cdp_Layout_ms_after':
            metrics_post.get('LayoutDuration', 0) * 1000,
        'cdp_RecalcStyle_ms_after':
            metrics_post.get('RecalcStyleDuration', 0) * 1000,
        'sync_layout_500x_ms': layout_ms,
        'paint_200x_ms': paint_ms,
        'css_inline_count': css['inline_count'],
        'css_inline_kb': css['inline_bytes'] / 1024,
        'css_external_count': css['external_count'],
    }


def median(vals):
    s = sorted(vals)
    return s[len(s) // 2]


def main() -> None:
    cpu_throttle = int(os.environ.get('CPU_THROTTLE', '4'))
    cards = int(os.environ.get('CARDS', '30'))
    runs = int(os.environ.get('RUNS', '3'))

    print(f'CPU throttle: {cpu_throttle}x  |  cards/page: {cards}  |  runs: {runs}')
    print('Chromium: --disable-gpu (software composition)')
    print('Metrics: NOT vsync-bound (CDP counters + sync reflow loops)')
    print()

    p_def = start_server('default', 8100, count=cards)
    p_brt = start_server('brutalist', 8101, count=cards)
    try:
        wait_ready(8100)
        wait_ready(8101)
        with sync_playwright() as pw:
            # Warm-up
            print('warming...')
            measure(pw, 'http://127.0.0.1:8100/', cpu_throttle)
            measure(pw, 'http://127.0.0.1:8101/', cpu_throttle)

            d_runs, b_runs = [], []
            for run in range(runs):
                print(f'\n=== Run {run + 1}/{runs} ===')
                d = measure(pw, 'http://127.0.0.1:8100/', cpu_throttle)
                b = measure(pw, 'http://127.0.0.1:8101/', cpu_throttle)
                d_runs.append(d)
                b_runs.append(b)
                print(f'  Material  nodes={d["nodes"]}  heap={d["js_heap_used_MB"]:.2f}MB  '
                      f'sync-layout-500={d["sync_layout_500x_ms"]:.1f}ms  '
                      f'paint-200={d["paint_200x_ms"]:.1f}ms')
                print(f'  Brutalist nodes={b["nodes"]}  heap={b["js_heap_used_MB"]:.2f}MB  '
                      f'sync-layout-500={b["sync_layout_500x_ms"]:.1f}ms  '
                      f'paint-200={b["paint_200x_ms"]:.1f}ms')

        # Summary table
        print('\n=== Median across runs ===')
        keys = [
            ('nodes', 'DOM nodes', '{:>10.0f}'),
            ('documents', 'documents', '{:>10.0f}'),
            ('js_event_listeners', 'js event listeners', '{:>10.0f}'),
            ('js_heap_used_MB', 'JS heap used (MB)', '{:>10.2f}'),
            ('js_heap_total_MB', 'JS heap total (MB)', '{:>10.2f}'),
            ('cdp_Layout_ms_baseline', 'cumulative layout (ms)', '{:>10.2f}'),
            ('cdp_RecalcStyle_ms_baseline', 'cumulative style recalc (ms)', '{:>10.2f}'),
            ('sync_layout_500x_ms', 'sync layout x500 (ms)', '{:>10.1f}'),
            ('paint_200x_ms', 'paint loop x200 (ms)', '{:>10.1f}'),
            ('css_inline_count', '<style> blocks', '{:>10.0f}'),
            ('css_inline_kb', 'inline CSS (KB)', '{:>10.1f}'),
            ('css_external_count', 'external CSS files', '{:>10.0f}'),
        ]
        print(f'{"metric":<32}  {"material":>10}  {"brutalist":>10}  {"delta":>10}  per-card')
        print('-' * 90)
        for key, label, fmt in keys:
            d = median([r[key] for r in d_runs])
            b = median([r[key] for r in b_runs])
            delta = b - d
            per_card = delta / cards if cards > 0 else 0
            sign = '+' if delta >= 0 else ''
            verdict = ('cheaper' if delta < 0 else 'costlier' if delta > 0 else '=')
            print(f'{label:<32}  {fmt.format(d)}  {fmt.format(b)}  '
                  f'{sign + fmt.format(delta).strip():>10}  '
                  f'{per_card:+.2f}/card  ({verdict})')

    finally:
        for p in (p_def, p_brt):
            p.terminate()
            try:
                p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                p.kill()


if __name__ == '__main__':
    main()
