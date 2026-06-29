# Go net/http Benchmark v2

**Date:** 2026-06-28
**Port:** 8893

## Response Time Results
| Payload | Items | Avg | Min | Max |
|---|---:|---:|---:|---:|
| Small | 100 | 4.83 ms | 3.41 ms | 7.44 ms |
| Medium | 1000 | 15.54 ms | 13.17 ms | 17.96 ms |
| Large | 5000 | 145.44 ms | 140.38 ms | 155.53 ms |

## Notes
- Go is still very RAM-friendly.
- For very large payloads, JSON work dominates and response time climbs hard.
