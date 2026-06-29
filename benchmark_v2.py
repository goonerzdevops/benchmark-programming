#!/usr/bin/env python3
"""Benchmark v2 – run one stack at a time, clean isolation, log resources."""
import json, os, random, string, subprocess, sys, time, math, signal, hashlib
from pathlib import Path

BASE = Path("/mnt/d/Benchmark Programming")
PIDS = {}  # name -> {process, ports}
RESULT = {}
PAYLOADS = {"small": 100, "medium": 1000, "large": 5000}
PORT = {"dotnet": 8891, "fastapi": 8892, "go": 8893}

def start(name, cmd, port, ready_text):
    print(f"  🚀 Starting {name} on :{port} ...")
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        preexec_fn=lambda: os.setsid() if os.name != "nt" else None
    )
    # wait for ready signal or 10s
    deadline = time.time() + 10
    ready = False
    while time.time() < deadline:
        line = proc.stdout.readline().decode(errors="replace")
        if ready_text in line:
            ready = True
            break
        time.sleep(0.2)
    print(f"  {'✅' if ready else '⚠️'} ready={ready}")
    PIDS[name] = proc
    return ready

def stop(name):
    proc = PIDS.get(name)
    if proc:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=5)

def gen_payload(n):
    items = []
    for _ in range(n):
        v = round(random.uniform(10, 9999), 2)
        w = "".join(random.choices(string.ascii_lowercase + " ", k=random.randint(5, 30))).strip()
        items.append({"numeric_value": v, "string_data": w})
    return {"items": items}

def benchmark(name, port):
    print(f"\n{'='*50}")
    print(f"   BENCHMARKING {name}")
    print(f"{'='*50}")
    sizes = []
    for size_label, count in PAYLOADS.items():
        payload = gen_payload(count)
        body = json.dumps(payload).encode()
        times = []
        for run in range(3):
            try:
                import urllib.request
                req = urllib.request.Request(
                    f"http://localhost:{port}/complex-transform",
                    data=body, headers={"Content-Type": "application/json"}, method="POST"
                )
                t0 = time.time()
                with urllib.request.urlopen(req, timeout=30) as resp:
                    resp_data = json.loads(resp.read())
                t1 = time.time()
                server_ms = resp_data.get("server_processing_time", resp_data.get("server_processing_time_ms", 0))
                times.append({"run": run+1, "response_ms": round((t1-t0)*1000, 2), "server_ms": server_ms, "items_out": len(resp_data.get("transformed_and_sorted_items",[]))})
                print(f"  {name} [{size_label}:{count}] run {run+1}: {times[-1]['response_ms']}ms")
            except Exception as e:
                print(f"  {name} [{size_label}:{count}] run {run+1}: FAILED {e}")
        avg = sum(t["response_ms"] for t in times)/len(times) if times else 0
        sizes.append({"size": size_label, "count": count, "avg": round(avg, 2), "runs": times})
        if times:
            print(f"  → avg: {avg:.1f}ms")
    return sizes

def write_md(name, results):
    lines = [
        f"# {name} – Benchmark v2",
        f"**Date:** 2026-06-28",
        f"**Port:** {PORT[name.lower().split()[0]]}",
        f"",
        f"## Response Time",
        f"| Payload | Items | Avg | Min | Max |",
        f"|---|---:|---:|---:|---:|",
    ]
    for s in results:
        vals = [r["response_ms"] for r in s["runs"]]
        met = min(vals), max(vals)
        lines.append(f"| {s['size']} | {s['count']} | {s['avg']} ms | {met[0]} ms | {met[1]} ms |")
    lines.append("")
    suffix = {"dotnet": "dotnet", "fastapi": "python", "go": "golang"}
    for sk in suffix:
        if name.lower().startswith(sk):
            lines.append("### Raw Data")
            lines.append(f"- `results/benchmark_v2.json`")
    Path(BASE / "results" / f"{suffix.get(name.lower().split()[0], 'unknown')}_benchmark_v2.md").write_text("\n".join(lines) + "\n")
    print(f"  📝 Written {suffix.get(name.lower().split()[0])}_benchmark_v2.md")

def write_readme(all_results):
    import json as _j
    lines = [
        "# 3-Stack API Benchmark Comparison v2",
        "**Date:** 2026-06-28  **Use Case:** ComplexDataTransformation (SHA256 + aggregation + sort)",
        "",
        "| Stack | 100 items | 1000 items | 5000 items |",
        "|:---|---:|---:|---:|",
    ]
    for name, sizes in all_results.items():
        a = {s["size"]: s["avg"] for s in sizes}
        lines.append(f"| **{name}** | {a.get('small','?')} ms | {a.get('medium','?')} ms | {a.get('large','?')} ms |")
    lines.append("")
    Path(BASE / "results" / "README_v2.md").write_text("\n".join(lines) + "\n")
    print(f"  📝 Written README_v2.md")

def main():
    os.chdir(BASE)
    os.makedirs(BASE/"results", exist_ok=True)

    stacks = [
        (".NET 10", f"export PATH=$HOME/.dotnet:$PATH && dotnet run --urls http://localhost:8891 --no-build -c Release", 8891, "Now listening on", "dotnet"),
        ("FastAPI", f"export PATH=$HOME/.local/bin:$PATH && cd {BASE}/python-fastapi && .venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8892", 8892, "Uvicorn running on", "fastapi"),
        ("Go net/http", f"export PATH=$HOME/go/bin:$PATH && cd {BASE}/golang-minimal-api && ./benchmark-api", 8893, "server starting", "go"),
    ]
    all_results = {}
    for name, cmd, port, ready, _ in stacks:
        stop_key = name.split()[0].lower()
        stop(stop_key)
        time.sleep(1)
        ready = start(name, cmd, port, ready)
        if not ready:
            print(f"  ❌ {name} not ready, skipping")
            continue
        res = benchmark(name, port)
        all_results[name] = res
        # Write per-stack md
        stack_key = {"dotnet": "dotnet", "fastapi": "python", "go": "golang"}
        k = [v for k,v in stack_key.items() if name.lower().startswith(k)][0]
        write_md(name, res)
        k = {s[0].split()[0].lower(): s[-1] for s in stacks}.get(name.split()[0].lower(), "unknown")
        Map = {"dotnet":"dotnet","fastapi":"python","go":"golang"}
        suffixes = {v: v for v in Map.values()}
        fn = Map.get({s[0].split()[0].lower(): s[-1] for s in stacks}.get(name.split()[0].lower()), "unknown")
        if fn != "unknown":
            write_md(name, res)
        stop_key = name.split()[0].lower()
        stop(stop_key)
        print(f"  🛑 Stopped {name}\n")

    write_readme(all_results)
    # Save JSON
    (BASE/"results"/"benchmark_v2.json").write_text(json.dumps(all_results, indent=2))
    print(f"\n✅ BENCHMARK v2 COMPLETE")
    print(f"   Results: {BASE}/results/benchmark_v2.json")

if __name__ == "__main__":
    main()
