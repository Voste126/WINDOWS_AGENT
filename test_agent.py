#!/usr/bin/env python3
# test_agent.py

import socket
import requests
from datetime import datetime, timedelta
import os

# Point at whatever port your collector is running on:
COLLECTOR_PORT = int(os.getenv("COLLECTOR_PORT", "5000"))
COLLECTOR_URL = f"http://localhost:{COLLECTOR_PORT}/ingest"

BATCH_SIZE = 5

def fetch_defender_events():
    """
    Stubbed fetch: generate a small list of fake Defender events.
    """
    now = datetime.utcnow()
    events = []
    for i in range(BATCH_SIZE):
        ts = (now - timedelta(minutes=i*2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        events.append({
            "TimeGenerated": ts,
            "EventID": 1000 + i,
            "Source": "Windows Defender (fake)",
            "Message": f"Fake event #{i+1} generated at {ts}"
        })
    return list(reversed(events))  # oldest first

def send_to_collector(events):
    payload = {
        "host": socket.gethostname(),
        "events": events
    }
    resp = requests.post(COLLECTOR_URL, json=payload, timeout=10)
    resp.raise_for_status()
    print(f"[agent] Successfully sent {len(events)} events to {COLLECTOR_URL}")

if __name__ == "__main__":
    evts = fetch_defender_events()
    try:
        send_to_collector(evts)
    except Exception as e:
        print("[agent] Error sending to collector:", e)
