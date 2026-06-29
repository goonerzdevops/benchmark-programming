#!/usr/bin/env python3
"""Benchmark test payload generator and API tester for 3-stack comparison."""

import json
import random
import string
import subprocess
import sys
import time
import os
import signal
from pathlib import Path

OUT_DIR = Path("/mnt/d/Benchmark Programming/results")
PAYLOAD_SIZES = {
    "small": 100,
    "medium": 1000,
    "large": 5000,
}

def generate_payload(count: int) -> dict:
    items = []
    for _ in range(count):
        value = round(random.uniform(10.0, 9999.0), 2)
        word_len = random.randint(5, 30)
        label = "".join(random.choices(string.ascii_lowercase + " ", k=word_len))
        items.append({"numeric_value": value, "string_data": label.strip()})
    return {"items": items}

def save_payload(payload: dict, size_name: str):
    path = OUT_DIR / f"payload_{size_name}.json"
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return path

def run_benchmark(name: str, port: int, payload_sizes: list[str]):
    """Run benchmarks for one stack across multiple payload sizes."""
    results = []
    for size_name in payload_sizes:
        count = PAYLOAD_SIZES[size_name]
        payload = generate_payload(count)
        payload_path = save_payload(payload, size_name)

        # Warmup run (1x)
        try:
            import urllib.request
            req = urllib.request.Request(
                f"http://localhost:{port}/complex-transform",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                _ = json.loads(resp.read())
        except Exception as e:
            print(f"  Warmup failed for {name} [{size_name}]: {e}")
            continue

        # Benchmark runs (3x)
        run_times = []
        for run in range(3):
            start = time.time()
            try:
                req = urllib.request.Request(
                    f"http://localhost:{port}/complex-transform",
                    data=json.dumps(payload).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read())
                elapsed = (time.time() - start) * 1000
                run_times.append({
                    "run": run + 1,
                    "response_time_ms": round(elapsed, 2),
                    "server_processing_ms": data.get("server_processing_time", data.get("server_processing_time_ms", 0)),
                    "items_out": len(data.get("transformed_and_sorted_items", [])),
                })
            except Exception as e:
                print(f"  Run {run+1} failed for {name} [{size_name}]: {e}")

        results.append({
            "size": size_name,
            "count": count,
            "runs": run_times,
        })
        print(f"  {name} [{size_name}:{count}] avg response: {sum(r['response_time_ms'] for r in run_times)/len(run_times):.1f}ms" if run_times else f"  {name} [{size_name}] FAILED")
    return results

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    payload_sizes = ["small", "medium", "large"]

    all_results = {}

    # Store results as JSON for processing
    for name, port in [(".NET 10", 8891), ("FastAPI", 8892), ("Go net/http", 8893)]:
        print(f"\n{'='*50}")
        print(f"Benchmarking {name} on port {port}")
        print(f"{'='*50}")
        results = run_benchmark(name, port, payload_sizes)
        all_results[name] = results

    # Save raw results
    with open(OUT_DIR / "benchmark_raw.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nRaw results saved to {OUT_DIR / 'benchmark_raw.json'}")

if __name__ == "__main__":
    main()
