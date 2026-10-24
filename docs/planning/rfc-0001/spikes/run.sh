#!/usr/bin/env bash
# RFC-0001 throughput spike. Same machine, same load tool (oha), same page shape, one at a time.
# Needs Docker and uv; the legacy app on 127.0.0.1:9080. Results: results/<name>.json
set -euo pipefail
cd "$(dirname "$0")"
R="results/workers-${WORKERS:-4}"; mkdir -p "$R"
OHA=ghcr.io/hatoo/oha@sha256:3ec3dbf549ea197793482d47a6324797411406bbf438c2fe8b91f244ec641a2f
PG=postgres:17.6@sha256:00bc86618629af00d2937fdc5a5d63db3ff8450acf52f0636ec813c7f4902929
DUR="${DUR:-60s}"; CONC="${CONC:-10}"; WORKERS="${WORKERS:-4}"

docker rm -f spike-pg >/dev/null 2>&1 || true
docker run -d --name spike-pg -p 127.0.0.1:5433:5432 -e POSTGRES_USER=spike -e POSTGRES_PASSWORD=spike -e POSTGRES_DB=spike "$PG" >/dev/null
until docker exec spike-pg pg_isready -U spike -q; do sleep 1; done; sleep 2
docker exec -i spike-pg psql -q -U spike spike < schema.sql

load() { # $1 name, $2 url, $3.. extra oha args
  local name=$1 url=$2; shift 2
  docker run --rm --network host "$OHA" -z 15s -c "$CONC" --no-tui "$@" "$url" >/dev/null  # warm-up
  docker run --rm --network host "$OHA" -z "$DUR" -c "$CONC" --no-tui --output-format json "$@" "$url" > "$R/$name.json"
  python3 -c "import json;d=json.load(open('$R/$name.json'));s=d['summary'];p=d['latencyPercentiles'];assert s['successRate'] == 1, f\"$name: success rate {s['successRate']}\";print(f\"$name: {s['requestsPerSec']:.0f} req/s, success {s['successRate']:.3f}, p50 {p['p50']*1000:.1f} ms, p95 {p['p95']*1000:.1f} ms, p99 {p['p99']*1000:.1f} ms\")"
}

DEPS=(--with django==6.1.2 --with "psycopg[binary]==3.3.6" --with gunicorn==26.2.0 --with fastapi==0.162.0
      --with "sqlalchemy[asyncio]==2.1.6" --with jinja2==3.1.6 --with "uvicorn[standard]==0.54.0")

serve() { # $1 port, then the server command; waits up to 120 s for it to answer
  local port=$1; shift
  if ss -ltn | grep -q "127.0.0.1:$port "; then echo "port $port is already in use" >&2; exit 1; fi
  uv run -q --no-project "${DEPS[@]}" "$@" > "$R/server-$port.log" 2>&1 & SERVER=$!
  for _ in $(seq 1 120); do curl -fs -o /dev/null "http://127.0.0.1:$port/home/uid:42" && return; sleep 1; done
  echo "server on $port didn't start; see $R/server-$port.log" >&2; exit 1
}

serve 8001 gunicorn -w "$WORKERS" -b 127.0.0.1:8001 --log-level warning django_app:application
load django "http://127.0.0.1:8001/home/uid:42"
kill $SERVER; sleep 3
serve 8002 uvicorn fastapi_app:app --workers "$WORKERS" --port 8002 --log-level warning --no-access-log
load fastapi "http://127.0.0.1:8002/home/uid:42"
kill $SERVER; sleep 3

# Legacy: the same page shape (its home page) for a logged-in seeded user.
COOKIE=$(curl -s -c - -o /dev/null "http://127.0.0.1:9080/daytrader/app?action=login&uid=uid:42&passwd=xxx" | awk '/JSESSIONID/ {print "JSESSIONID=" $7}')
load legacy "http://127.0.0.1:9080/daytrader/app?action=home" -H "Cookie: $COOKIE"

docker rm -f spike-pg >/dev/null
{ echo "date: $(date -u +%FT%TZ)"; echo "cpu: $(nproc) x $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs)";
  echo "python: $(uv run -q --no-project python --version)"; echo "load: oha, $CONC connections, $DUR after a 15 s warm-up; $WORKERS server workers; uvicorn[standard]"; } > "$R/environment.txt"
