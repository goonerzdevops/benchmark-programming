# Python FastAPI Benchmark v2

**Date:** 2026-06-28
**Port:** 8892

## Response Time Results
| Payload | Items | Avg | Min | Max |
|---|---:|---:|---:|---:|
| Small | 100 | 11.05 ms | 6.88 ms | 17.30 ms |
| Medium | 1000 | 47.31 ms | 33.67 ms | 73.01 ms |
| Large | 5000 | 155.10 ms | 147.29 ms | 159.61 ms |

## Notes
- FastAPI scales noticeably worse under larger JSON payloads.
- Server-side measured processing is tiny; most latency is serialization/runtime overhead.
