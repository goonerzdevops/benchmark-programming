# 3-Stack API Benchmark Comparison

**Date:** 2026-06-28  
**Use Case:** Complex data transformation — payload with raw JSON array, numeric aggregation, string concatenation + SHA256 hash, object transformation, sort.

## Environment
- **Host:** WSL2 (Ubuntu 24.04)
- **RAM (WSL):** ~3.8 GB total, ~1.9 GB available
- **Stacks tested:** .NET 10 Minimal API, Python FastAPI, Go net/http
- **Payload sizes:** 100 / 1000 / 5000 items per request

## Response Time Results

| Stack | 100 items | 1000 items | 5000 items |
|:---|---:|---:|---:|
| **.NET 10** | 5.10 ms | 9.45 ms | 40.15 ms |
| **FastAPI** | 5.85 ms | 26.74 ms | 106.47 ms |
| **Go net/http** | 2.59 ms | 11.63 ms | 135.98 ms |

## Resource Snapshot (Post-Benchmark)

| Stack | CPU | RAM (RSS) | Process tree size |
|:---|---|---:|---:|
| .NET 10 | ~0.2% | ~90 MB | ~150 MB (incl. dotnet run) |
| FastAPI | ~2.9% | ~55 MB | Minimal |
| Go net/http | ~1.4% | ~12.5 MB | Minimal |

## Key Takeaways

### .NET 10 Minimal API
- ✅ Best at scale: handles 5000 items faster than both competitors
- ✅ Server-side processing time extremely low (1–8 ms)
- ❌ RAM usage higher (90 MB + ~150 MB shared for the `dotnet run` hosting process)
- ❌ AOT not tested — this was a JIT-compiled run

### Python FastAPI
- ✅ Consistent middle-ground performance for small/medium payloads
- ✅ Low RAM for the process (55 MB)
- ❌ Scales poorly: 5000 items took 2.6x longer than .NET
- ❌ Python’s GIL + serialization overhead impacts large payloads

### Go net/http
- ✅ Fastest for small payloads (2.6 ms)
- ✅ Extremely efficient RAM (12.5 MB RSS — a standalone binary)
- ✅ No runtime dependency overhead
- ❌ Sharp performance degradation at 5000 items (slower than both FastAPI and .NET)
- ❌ JSON serialization for large arrays shows high CPU cost vs .NET’s `System.Text.Json`

## Overall Winner
**.NET 10 Minimal API** — most resource-efficient *in terms of time per workload at scale*. Go wins on RAM efficiency. Python wins on nothing except quick prototyping.

## Raw Data
- `results/dotnet_benchmark_2026-06-28.md`
- `results/python_benchmark_2026-06-28.md`
- `results/golang_benchmark_2026-06-28.md`
- `results/benchmark_raw.json`
