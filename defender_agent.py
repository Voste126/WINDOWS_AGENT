import socket
import json
import requests
import win32evtlog  # pip install pywin32

# CONFIGURATION
COLLECTOR_URL = "https://logs.mybank.internal/ingest"  # your central server
EVENT_LOG_NAME  = "Microsoft-Windows-Windows Defender/Operational"
BATCH_SIZE      = 200

def fetch_defender_events(server="localhost"):
    hand = win32evtlog.OpenEventLog(server, EVENT_LOG_NAME)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = []
    while len(events) < BATCH_SIZE:
        batch = win32evtlog.ReadEventLog(hand, flags, 0)
        if not batch:
            break
        for ev in batch:
            events.append({
                "TimeGenerated": ev.TimeGenerated.isoformat(),
                "EventID":       ev.EventID,
                "Source":        ev.SourceName,
                "Message":       win32evtlog.FormatMessage(ev).strip()
            })
            if len(events) >= BATCH_SIZE:
                break
    return list(reversed(events))  # oldest first

def send_to_collector(events):
    payload = {
        "host": socket.gethostname(),
        "events": events
    }
    resp = requests.post(COLLECTOR_URL, json=payload, timeout=10)
    resp.raise_for_status()

if __name__ == "__main__":
    evts = fetch_defender_events()
    if evts:
        try:
            send_to_collector(evts)
            print(f"Pushed {len(evts)} events")
        except Exception as e:
            print("Failed to send logs:", e)
