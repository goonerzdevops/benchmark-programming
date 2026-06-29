# 3-Stack API Benchmark Comparison v2

**Date:** 2026-06-28
**Mode:** Sequential one-by-one, one server at a time
**Use Case:** ComplexDataTransformation (numeric aggregate, SHA256, transform, sort)

## Result Table

| Stack | Small (100) | Medium (1000) | Large (5000) |
|---|---:|---:|---:|
| .NET 10 Minimal API | 9.16 ms | 11.40 ms | 40.13 ms |
| Python FastAPI | 11.05 ms | 47.31 ms | 155.10 ms |
| Go net/http | 4.83 ms | 15.54 ms | 145.44 ms |
| **Hono.js on Bun** | **5.47 ms** | **6.64 ms** | **15.04 ms** |

## Resource Snapshot Per Stack

### .NET 10 Minimal API
| Proses | PID | Threads | RSS (KB) | CPU% |
|---|---:|---:|---:|---:|
| App process | actual app | **20** | **58,880** | 10.3% |
| dotnet run (host) | parent | **23** | 149,508 | 81.5% |
| **Total lifecycle** | — | **43** | ~**208,388** | — |

- Notes: `dotnet run` includes host/build pipeline. AOT/published binary would drop the parent.

### Python FastAPI
| Proses | PID | Threads | RSS (KB) | CPU% |
|---|---:|---:|---:|---:|
| uvicorn worker | python process | **1** | **44,600** | 23.6% |
| **Total** | — | **1** | **~44,600** | — |

- Notes: Single-threaded async worker. No parent overhead.

### Go net/http
| Proses | PID | Threads | RSS (KB) | CPU% |
|---|---:|---:|---:|---:|
| BenchmarkApi binary | compiled | **6** | **6,400** | ~0% |
| **Total** | — | **6** | **~6,400** | — |

- Notes: Compiled binary — no runtime host. Go runtime manages goroutines transparently; 6 OS threads seen at snapshot.

### Hono.js on Bun
| Proses | PID | Threads | RSS (KB) | CPU% |
|---|---:|---:|---:|---:|
| bun run server | runtime | **12** | **54,456** | 0.9% |
| **Total** | — | **12** | **~54 MB** | — |

- Notes: Fastest large-payload latency with significantly lower resource cost than .NET. Bun runtime includes JS engine + transpiler.

## Thread Comparison Summary

| Metric | .NET 10 | FastAPI | Go | Hono/Bun |
|---|---:|---:|---:|---:|
| **Thread count** | 20 app + 23 host | 1 | 6 | **12** |
| **RSS total** | ~208 MB | ~45 MB | ~6.4 MB | **~54 MB** |
| **Smallest binary** | ~60 KB DLL | ~44 MB process | **~6.4 MB** | ~54 MB process |
| **Startup cost** | 7-15 sec (JIT) | ~1 sec | **~0.1 sec** | ~0.1 sec |

## Verdict
- **Best overall scaling:** .NET 10 Minimal API
- **Best small payload latency:** Go net/http
- **Best RAM efficiency:** Go net/http
- **Lowest thread count:** FastAPI (1)
- **Worst large-payload latency:** Python FastAPI

## Raw Files
- `results/dotnet_benchmark_v2.md`
- `results/python_benchmark_v2.md`
- `results/golang_benchmark_v2.md`
- `results/dotnet_benchmark_v2.json`
- `results/fastapi_benchmark_v2.json`
- `results/golang_benchmark_v2.json`
