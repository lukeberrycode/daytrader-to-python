# RFC-0001 spikes

Throwaway code that produced the evidence in `../../rfc-0001-destination-stack.md`. Not part of the new slice.

- `run.sh`: the throughput spike. Starts Postgres (`schema.sql`), then serves the same page with Django (`django_app.py`) and FastAPI (`fastapi_app.py`), one at a time, and loads each, then the legacy app's home page, with `oha`. `WORKERS=8 ./run.sh` for 8 workers. Needs the legacy app on port 9080.
- `json_money.py`: how each option writes `Decimal` money to JSON.
- `money.py`, `home.html`: shared by both apps, so they compute and render the same thing.
- `results/`: raw `oha` output per run, server logs and the machine's details; `json_money.txt`.
