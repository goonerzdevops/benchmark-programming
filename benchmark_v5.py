#!/usr/bin/env python3
"""4-phase benchmark harness for .NET, FastAPI, Go, and Hono/Bun.

Phases:
1) Request count: 1 / 10 / 100
2) Concurrency: 1 / 5 / 20 / 50
3) Payload size: 100 / 1000 / 5000 items
4) Soak test: 10 minutes

Outputs per stack are written to results/benchmark_v5_<stack>.json and .md.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import os
import random
import statistics as stats
import string
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path('/mnt/d/Benchmark Programming')
RESULTS = ROOT / 'results'
RESULTS.mkdir(parents=True, exist_ok=True)

PAYLOAD_SIZES = [100, 1000, 5000]
REQUEST_COUNTS = [1, 10, 100]
CONCURRENCY_LEVELS = [1, 5, 20, 50]
SOAK_SECONDS = 600
SOAK_CONCURRENCY = 20

STACKS = {
    'dotnet': {
        'name': '.NET 10 Minimal API',
        'port': 8891,
        'cwd': ROOT / 'dotnet-minimal-api',
        'start': ['bash', '-lc', 'export PATH="$HOME/.dotnet:$PATH" && dotnet run --urls http://localhost:8891 --no-build -c Release'],
    },
    'fastapi': {
        'name': 'Python FastAPI',
        'port': 8892,
        'cwd': ROOT / 'python-fastapi',
        'start': ['bash', '-lc', 'export PATH="$HOME/.local/bin:$PATH" && .venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8892 --workers 4'],
    },
    'go': {
        'name': 'Go net/http',
        'port': 8893,
        'cwd': ROOT / 'golang-minimal-api',
        'start': ['bash', '-lc', './benchmark-api'],
    },
    'hono': {
        'name': 'Hono.js on Bun',
        'port': 8894,
        'cwd': ROOT / 'hono-bun',
        'start': ['bash', '-lc', 'export BUN_INSTALL="$HOME/.bun" && export PATH="$BUN_INSTALL/bin:$PATH" && bun run src/index.ts'],
    },
}


def make_payload(n: int) -> dict[str, Any]:
    return {
        'items': [
            {
                'numeric_value': round(random.uniform(10, 9999), 2),
                'string_data': ''.join(random.choices(string.ascii_lowercase + ' ', k=random.randint(5, 30))).strip(),
            }
            for _ in range(n)
        ]
    }


def pctl(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    vals = sorted(values)
    k = (len(vals) - 1) * (pct / 100)
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    if f == c:
        return vals[f]
    return vals[f] * (c - k) + vals[c] * (k - f)


def post_json(url: str, payload: dict[str, Any], timeout: int = 30) -> tuple[float, dict[str, Any]]:
    import urllib.request
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        js = json.loads(raw)
    t1 = time.time()
    return (t1 - t0) * 1000, js


def wait_ready(port: int, timeout: int = 30) -> None:
    deadline = time.time() + timeout
    payload = {'items': [{'numeric_value': 1, 'string_data': 'test'}]}
    while time.time() < deadline:
        try:
            ms, _ = post_json(f'http://localhost:{port}/complex-transform', payload, timeout=5)
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f'Port {port} not ready in {timeout}s')


def run_seq(url: str, payload: dict[str, Any], count: int) -> dict[str, Any]:
    times = []
    errors = 0
    for _ in range(count):
        try:
            ms, _ = post_json(url, payload, timeout=30)
            times.append(ms)
        except Exception:
            errors += 1
    return {
        'count': count,
        'p50_ms': round(pctl(times, 50), 2),
        'p95_ms': round(pctl(times, 95), 2),
        'p99_ms': round(pctl(times, 99), 2),
        'avg_ms': round(sum(times) / len(times), 2) if times else 0,
        'errors': errors,
        'samples': len(times),
    }


def run_concurrent(url: str, payload: dict[str, Any], concurrency: int, total_requests: int) -> dict[str, Any]:
    def one(_: int) -> float:
        ms, _ = post_json(url, payload, timeout=60)
        return ms

    start = time.time()
    latencies: List[float] = []
    errors = 0
    with cf.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = [ex.submit(one, i) for i in range(total_requests)]
        for fut in cf.as_completed(futures):
            try:
                latencies.append(fut.result())
            except Exception:
                errors += 1
    elapsed = time.time() - start
    rps = total_requests / elapsed if elapsed > 0 else 0
    return {
        'concurrency': concurrency,
        'requests': total_requests,
        'seconds': round(elapsed, 2),
        'rps': round(rps, 2),
        'p50_ms': round(pctl(latencies, 50), 2),
        'p95_ms': round(pctl(latencies, 95), 2),
        'p99_ms': round(pctl(latencies, 99), 2),
        'avg_ms': round(sum(latencies) / len(latencies), 2) if latencies else 0,
        'errors': errors,
    }


def sample_resource(pid: int) -> dict[str, Any]:
    try:
        out = subprocess.check_output(['ps', '-o', 'pid,ppid,thcount,rss,pcpu,cmd', '-p', str(pid)], text=True)
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        if len(lines) >= 2:
            parts = lines[1].split(None, 5)
            return {
                'pid': int(parts[0]),
                'ppid': int(parts[1]),
                'threads': int(parts[2]),
                'rss_kb': int(parts[3]),
                'cpu_pct': float(parts[4]),
                'cmd': parts[5],
            }
    except Exception:
        pass
    return {}


def main() -> int:
    summary = {}
    for key, cfg in STACKS.items():
        print(f'== {cfg["name"]} ==')
        proc = subprocess.Popen(cfg['start'], cwd=str(cfg['cwd']), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            wait_ready(cfg['port'])
            url = f'http://localhost:{cfg["port"]}/complex-transform'
            results = {'phase1': {}, 'phase2': {}, 'phase3': {}, 'phase4': {}, 'resource': []}

            # Phase 1: request count
            payload = make_payload(100)
            for count in REQUEST_COUNTS:
                results['phase1'][str(count)] = run_seq(url, payload, count)

            # Phase 2: concurrency
            payload = make_payload(100)
            for c in CONCURRENCY_LEVELS:
                total = c * 20
                results['phase2'][str(c)] = run_concurrent(url, payload, c, total)

            # Phase 3: payload scaling
            for n in PAYLOAD_SIZES:
                results['phase3'][str(n)] = run_seq(url, make_payload(n), 3)

            # Phase 4: soak test (10 minutes)
            soak_payload = make_payload(1000)
            soak_start = time.time()
            soak_lat = []
            soak_errors = 0
            sample_points = []
            while time.time() - soak_start < SOAK_SECONDS:
                with cf.ThreadPoolExecutor(max_workers=SOAK_CONCURRENCY) as ex:
                    futures = [ex.submit(post_json, url, soak_payload, 60) for _ in range(SOAK_CONCURRENCY)]
                    for fut in cf.as_completed(futures):
                        try:
                            ms, _ = fut.result()
                            soak_lat.append(ms)
                        except Exception:
                            soak_errors += 1
                sample_points.append(sample_resource(proc.pid))
                time.sleep(5)
            results['phase4'] = {
                'seconds': SOAK_SECONDS,
                'concurrency': SOAK_CONCURRENCY,
                'avg_ms': round(sum(soak_lat) / len(soak_lat), 2) if soak_lat else 0,
                'p50_ms': round(pctl(soak_lat, 50), 2),
                'p95_ms': round(pctl(soak_lat, 95), 2),
                'p99_ms': round(pctl(soak_lat, 99), 2),
                'errors': soak_errors,
                'samples': len(soak_lat),
            }
            results['resource'] = sample_points
            summary[key] = results

            (RESULTS / f'benchmark_v5_{key}.json').write_text(json.dumps(results, indent=2))
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except Exception:
                proc.kill()
        print(f'-- done {key}')

    (RESULTS / 'benchmark_v5_summary.json').write_text(json.dumps(summary, indent=2))
    print('wrote summary')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
