#!/usr/bin/env python3
# collector.py

from flask import Flask, request, abort
import os
import json
from datetime import datetime
import sys

app = Flask(__name__)

# Directory where incoming JSON batches will be written
LOG_DIR = "./defender_logs"
os.makedirs(LOG_DIR, exist_ok=True)

@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json(force=True)
    host = data.get("host")
    events = data.get("events")
    if not host or not isinstance(events, list):
        abort(400, "Invalid payload: must include 'host' (str) and 'events' (list)")

    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{host}_{now}.json"
    path = os.path.join(LOG_DIR, filename)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[collector] Wrote {len(events)} events to {path}")

    return "OK\n", 200

if __name__ == "__main__":
    # Usage: python collector.py [port]
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port '{sys.argv[1]}', defaulting to 5000")
    print(f"[collector] Starting on http://0.0.0.0:{port}/ingest")
    app.run(host="0.0.0.0", port=port)


