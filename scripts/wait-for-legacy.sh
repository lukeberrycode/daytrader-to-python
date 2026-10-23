#!/usr/bin/env bash
# Waits for the legacy DayTrader app to answer on http://localhost:9080/daytrader/ (up to 3 minutes).
set -euo pipefail
url="${LEGACY_URL:-http://localhost:9080/daytrader}/"
for _ in $(seq 1 90); do
  if curl -fs -o /dev/null "$url"; then
    echo "Legacy app is up at $url"
    exit 0
  fi
  sleep 2
done
echo "Legacy app did not start at $url" >&2
exit 1
