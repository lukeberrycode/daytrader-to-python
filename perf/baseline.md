# NFR-1 baseline: the legacy app under load

DayTrader's own JMeter workload (`legacy/daytrader8/jmeter_files/daytrader8.jmx`), run by `perf/run-baseline.sh 10 180` on 24 October 2026, following the procedure in DayTrader's FAQ: reset, 60-second warm-up, reset, then 180 seconds measured. Raw figures: `perf/results/20261024T181948Z/` (`statistics.json`, `environment.txt`).

## Conditions

- 10 JMeter threads, no think time, users `uid:0` to `uid:499`, stocks `s:0` to `s:999`.
- Legacy image as pinned in `legacy/docker/Dockerfile` (Open Liberty 26.0.0.9, Java 8), started fresh, default configuration.
- One laptop: Intel Core i7-7600U, 4 logical CPUs, 19 GB memory (about 2 GB free), with JMeter 5.6.3 in a container on the same machine. Nothing else used the app during the run.

The figures hold only for this machine. NFR-1 compares the new slice with the legacy app **on the same machine, by the same script**, not with these numbers.

## Results

| | Value |
|---|---|
| Requests | 183,231 |
| Errors | 0 |
| Throughput | 1,018 requests a second |
| Response time: mean / median | 9.3 ms / 5 ms |
| Response time: 90th / 95th / 99th percentile | 13 / 16 / 24 ms |
| Response time: maximum | 1,215 ms |

Main operations (JSP interface unless marked "Faces", which is the JSF interface):

| Operation | Requests | Mean (ms) | 95th percentile (ms) |
|---|---|---|---|
| Quotes | 46,779 | 6.1 | 11 |
| Portfolio | 23,315 | 9.8 | 19 |
| Home | 21,820 | 8.6 | 17 |
| Account | 16,199 | 7.0 | 16 |
| Login | 4,182 | 15.3 | 33 |
| Buy | 2,923 | 23.8 | 50 |
| Sell | 2,595 | 23.8 | 47 |
| Register | 1,224 | 18.2 | 36 |
| Quotes - JAX-RS (REST API) | 1,246 | 11.4 | 26 |
| Quotes Faces | 8,282 | 17.1 | 39 |
| Buy Faces | 477 | 39.1 | 83 |
| Market summary WebSocket ("WS2 existing") | 9,140 | 3.3 | 9 |

## Notes for the gate

- The workload drives **both** web interfaces, JSP and JSF (scope decision S1), plus the REST API and the market-summary WebSocket (S4). If the new slice has one web UI, the script needs adapting, and NFR-1 should compare like with like.
- Buying never fails for lack of cash under this workload because of KF-1. If KF-1 is fixed, the script's users may run out of cash during a run; a load-test setting may be needed (see KF-1).
- The whole run makes 0 errors, so the HTTP 500s in KF-3, KF-5, KF-13 and KF-16 aren't reached by DayTrader's own workload: its quantities are whole numbers from 1 to 200 (`${__Random(1,200)}`), and it logs in only with the users' own passwords.
