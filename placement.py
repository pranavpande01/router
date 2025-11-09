# placement.py
import sqlite3, shutil, os, time
from predictor import predict

DB="fluxtier.db"
STORAGE_ROOT="./stores"  # stores/on-prem, stores/private, stores/public
os.makedirs(STORAGE_ROOT, exist_ok=True)
for s in ["on-prem","private","public"]:
    os.makedirs(os.path.join(STORAGE_ROOT,s), exist_ok=True)

def move_dataset(dataset_id, src, dest):
    # simulate move by creating file markers
    srcf = os.path.join(STORAGE_ROOT, src, dataset_id+".meta")
    dstf = os.path.join(STORAGE_ROOT, dest, dataset_id+".meta")
    # write metadata
    with open(dstf, "w") as f:
        f.write(f"{dataset_id} moved {time.time()}")
    if os.path.exists(srcf):
        os.remove(srcf)
    # record migration
    conn = sqlite3.connect(DB); c=conn.cursor()
    c.execute("INSERT INTO migrations(dataset_id,from_loc,to_loc,status,info) VALUES (?,?,?,?,?)",
              (dataset_id, src, dest, "done", "simulated"))
    c.execute("UPDATE datasets SET location=?, last_migration=CURRENT_TIMESTAMP, version=version+1 WHERE dataset_id=?",(dest,dataset_id))
    conn.commit(); conn.close()
    print(f"Moved {dataset_id} {src} -> {dest}")

def policy_loop():
    while True:
        df = predict()
        for row in df.itertuples():
            ds = row.dataset_id
            loc = row.location
            p = row.hot_prob
            # policy: if hot_prob > .7 and not on-prem, move to private (fast)
            if p > 0.7 and loc != "private":
                move_dataset(ds, loc, "private")
            # if p < .2, move to public (cheaper)
            elif p < 0.2 and loc != "public":
                move_dataset(ds, loc, "public")
        time.sleep(10)

if __name__=="__main__":
    policy_loop()
