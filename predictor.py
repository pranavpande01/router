# predictor.py
import sqlite3, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta
import joblib

DB="fluxtier.db"
MODEL_PATH="hot_predictor.pkl"

def build_features():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT dataset_id, size_gb, access_count, avg_latency_ms, last_access, location FROM datasets", conn)
    conn.close()
    df["last_access_age"] = (pd.Timestamp.utcnow() - pd.to_datetime(df["last_access"], errors="coerce")).dt.total_seconds().fillna(1e6)
    # label: hot if access_count > threshold (this is synthetic training)
    df["label"] = (df["access_count"] > 20).astype(int)
    X = df[["size_gb","access_count","avg_latency_ms","last_access_age"]].fillna(0)
    y = df["label"]
    return X,y,df

def train():
    X,y,df = build_features()
    if len(X) < 5:
        print("Not enough data to train yet")
        return
    m = RandomForestClassifier(n_estimators=50, random_state=42)
    m.fit(X,y)
    joblib.dump(m, MODEL_PATH)
    print("Model trained and saved.")

def predict():
    import joblib
    m = joblib.load(MODEL_PATH)
    X,y,df = build_features()
    preds = m.predict_proba(X)[:,1]
    df["hot_prob"]=preds
    return df[["dataset_id","location","access_count","hot_prob"]]

if __name__=="__main__":
    train()
