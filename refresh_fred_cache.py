
from __future__ import annotations
import io, time
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from config import CATEGORIES
FRED_CSV="https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
OUT=Path(__file__).resolve().parent/"data_cache"
OUT.mkdir(exist_ok=True)

def fred_series_ids():
    ids=set()
    for cfg in CATEGORIES.values():
        for m in cfg["metrics"]:
            if m.source=="FRED" and m.series: ids.add(m.series)
    ids.update(["CES0500000003","CPIAUCSL"])
    return sorted(ids)

def fetch_one(series,attempts=4):
    last=None
    for attempt in range(1,attempts+1):
        try:
            r=requests.get(FRED_CSV.format(series=series),timeout=(15,90),headers={"User-Agent":"macro-eco-radar-cache-bot/1.0"})
            r.raise_for_status()
            df=pd.read_csv(io.StringIO(r.text))
            if df.shape[1]<2: raise ValueError("Unexpected FRED response")
            dcol,vcol=df.columns[0],df.columns[1]
            df[dcol]=pd.to_datetime(df[dcol],errors="coerce")
            df[vcol]=pd.to_numeric(df[vcol].replace(".",np.nan),errors="coerce")
            out=df[[dcol,vcol]].dropna().rename(columns={dcol:"DATE",vcol:"VALUE"})
            if out.empty: raise ValueError("No usable rows")
            out.to_csv(OUT/f"{series}.csv",index=False)
            print(f"OK {series}: {len(out)} rows")
            return True
        except Exception as e:
            last=e
            print(f"Attempt {attempt}/{attempts} failed for {series}: {e}")
            time.sleep(min(20,attempt*5))
    print(f"FAILED {series}: {last}")
    return False

def main():
    failed=[x for x in fred_series_ids() if not fetch_one(x)]
    if failed: raise SystemExit("Failed FRED series: "+", ".join(failed))
if __name__=="__main__": main()
