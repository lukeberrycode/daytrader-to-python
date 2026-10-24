#!/usr/bin/env bash
# NFR-1 baseline: the legacy app under DayTrader's own JMeter workload (daytrader8.jmx),
# following the procedure in its FAQ: reset, warm up, reset, measure.
# Usage: perf/run-baseline.sh [threads] [seconds]. Needs the legacy app on localhost:9080.
# Results go to perf/results/<timestamp>/: statistics.json and environment.txt (committed), and
# results.jtl, report/ and jmeter.log (ignored by git).
set -euo pipefail
cd "$(dirname "$0")/.."
threads="${1:-10}"
seconds="${2:-180}"
out="perf/results/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$out"
docker build -q -t daytrader-jmeter perf >/dev/null

run() { # $1 = duration, $2 = results file or empty
  docker run --rm --network host -v "$PWD/legacy/daytrader8/jmeter_files:/scripts:ro" -v "$PWD/$out:/out" \
    daytrader-jmeter -n -t /scripts/daytrader8.jmx \
    -JHOST=localhost -JPORT=9080 -JTHREADS="$threads" -JRAMP="$threads" -JDURATION="$1" \
    -JTOPUID=499 -JSTOCKS=999 -JWEBSOCKET_TIMEOUT=5 ${2:+-l "/out/$2" -e -o /out/report} -j /out/jmeter.log >/dev/null
}

curl -fs -o /dev/null "http://localhost:9080/daytrader/config?action=resetTrade"
run 60 ""                                  # warm-up: lets the JIT compile the code paths
curl -fs -o /dev/null "http://localhost:9080/daytrader/config?action=resetTrade"
run "$seconds" results.jtl

{
  echo "date: $(date -u +%FT%TZ)"
  echo "threads: $threads; measured seconds: $seconds; warm-up seconds: 60; think time: 0"
  echo "legacy image: $(docker inspect legacy --format '{{.Image}}')"
  echo "cpu: $(nproc) x $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs)"
  echo "memory: $(free -g | awk '/Mem:/ {print $2}') GB"
  echo "jmeter: 5.6.3; app and load generator on the same machine"
} > "$out/environment.txt"
cp "$out/report/statistics.json" "$out/statistics.json"
echo "$out"
