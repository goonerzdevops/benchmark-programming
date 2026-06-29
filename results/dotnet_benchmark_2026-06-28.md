# .NET 10 Minimal API Benchmark Report

**Date:** 2026-06-28
**Port:** 8891
**Stack:** .NET 10 Minimal API

## Summary
- Average response time across payloads: fastest among larger payloads
- Peak resource snapshot during run:
  - CPU: ~0.2% (post-benchmark snapshot)
  - RAM: ~90 MB RSS for the app process

## Response Time Results
| Payload | Items | Avg Response | Min | Max |
|---|---:|---:|---:|---:|
| Small | 100 | 5.10 ms | 4.11 ms | 6.49 ms |
| Medium | 1000 | 9.45 ms | 8.99 ms | 9.89 ms |
| Large | 5000 | 40.15 ms | 38.82 ms | 41.63 ms |

## Notes
- Server-side processing time was extremely low in the app code.
- Scaling stayed stable as payload grew.
- The actual OS-level snapshot after benchmark showed the app around 90 MB RSS.

## Raw Data
- `results/benchmark_raw.json`
- `results/payload_small.json`
- `results/payload_medium.json`
- `results/payload_large.json`
