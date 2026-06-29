# Go net/http Benchmark Report

**Date:** 2026-06-28
**Port:** 8893
**Stack:** Go net/http

## Summary
- Fastest on small payload.
- Performance degrades significantly for large payloads.
- Peak resource snapshot during run:
  - CPU: ~1.4% (active process snapshot)
  - RAM: ~12.5 MB RSS (compiled binary)

## Response Time Results
| Payload | Items | Avg Response | Min | Max |
|---|---:|---:|---:|---:|
| Small | 100 | 2.59 ms | 2.32 ms | 2.96 ms |
| Medium | 1000 | 11.63 ms | 11.28 ms | 11.97 ms |
| Large | 5000 | 135.98 ms | 133.06 ms | 138.02 ms |

## Notes
- Small/medium show Go’s strength: minimal runtime overhead.
- Large payloads (5000 items) show a sharp increase; possibly due to JSON allocation patterns.
- RAM usage is extremely low: ~12 MB RSS — most memory-efficient of the three.

## Raw Data
- `results/benchmark_raw.json`
- `results/payload_small.json`
- `results/payload_medium.json`
- `results/payload_large.json`
