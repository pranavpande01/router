# processor.py
import sqlite3, time, json
from simulator import QUEUE
from datetime import datetime

DB="fluxtier.db"

def process_event(ev):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    ds = ev["dataset_id"]
    ts = ev["ts"]
    action = ev["action"]
    lat = ev["latency_ms"]
    c.execute("INSERT INTO access_log (dataset_id, action, latency_ms) VALUES (?,?,?)", (ds,action,lat))
    c.execute("UPDATE datasets SET access_count = access_count + 1, last_access = ?, avg_latency_ms = (avg_latency_ms + ?)/2 WHERE dataset_id = ?",
              (ts, lat, ds))
    conn.commit()
    conn.close()

def consumer_loop():
    while True:
        if QUEUE:
            ev = QUEUE.pop(0)
            process_event(ev)
        else:
            time.sleep(0.1)

if __name__ == "__main__":
    print("Starting consumer")
    consumer_loop()
