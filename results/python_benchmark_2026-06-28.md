# Python FastAPI Benchmark Report

**Date:** 2026-06-28
**Port:** 8892
**Stack:** Python FastAPI

## Summary
- متوسط response time grows much faster than .NET 10.
- Peak resource snapshot during run:
  - CPU: ~2.9% (active process snapshot)
  - RAM: ~55 MB RSS for the uvicorn process

## Response Time Results
| Payload | Items | Avg Response | Min | Max |
|---|---:|---:|---:|---:|
| Small | 100 | 5.85 ms | 4.99 ms | 7.17 ms |
| Medium | 1000 | 26.74 ms | 23.90 ms | 30.94 ms |
| Large | 5000 | 106.47 ms | 88.89 ms | 121.51 ms |

## Notes
- Small payload performance is close to .NET.
- Medium and large payloads are significantly slower.
- Memory footprint stays moderate, lower than .NET snapshot and much lower than Go’s raw process tree snapshot from this run.

## Raw Data
- `results/benchmark_raw.json`
- `results/payload_small.json`
- `results/payload_medium.json`
- `results/payload_large.json`
