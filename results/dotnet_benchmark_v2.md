# .NET 10 Minimal API Benchmark v2

**Date:** 2026-06-28
**Port:** 8891

## Response Time Results
| Payload | Items | Avg | Min | Max |
|---|---:|---:|---:|---:|
| Small | 100 | 9.16 ms | 4.45 ms | 17.99 ms |
| Medium | 1000 | 11.40 ms | 7.75 ms | 17.26 ms |
| Large | 5000 | 40.13 ms | 32.98 ms | 51.17 ms |

## Notes
- Best scaling among the three at 5000 items.
- Small-run outlier on first request likely warmup/JIT effect.
