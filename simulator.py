# simulator.py
import sqlite3, random, time, json, os, threading
from datetime import datetime

DB = "fluxtier.db"
DATASETS = ["ds_"+str(i) for i in range(1,21)]

def seed_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(open("schema.sql").read())
    for d in DATASETS:
        # random sizes and initial location
        loc = random.choice(["on-prem","private","public"])
        size = round(random.uniform(1,200),2)
        c.execute("INSERT OR IGNORE INTO datasets(dataset_id,size_gb,location,cost_per_gb) VALUES (?,?,?,?)",
                  (d,size,loc,{"on-prem":0.01,"private":0.02,"public":0.025}[loc]))
    conn.commit()
    conn.close()

# simple in-memory queue (pub-sub)
QUEUE = []

def producer_loop(rate_per_sec=5):
    while True:
        ds = random.choice(DATASETS)
        latency = random.gauss(50,20)
        action = random.choices(["read","write"], weights=[0.9,0.1])[0]
        event = {"dataset_id":ds, "ts": datetime.utcnow().isoformat(), "action":action, "latency_ms": max(1, latency)}
        QUEUE.append(event)
        time.sleep(1.0/max(rate_per_sec,1))

if __name__ == "__main__":
    seed_db()
    print("Seeding complete. Starting producer.")
    producer_loop()
