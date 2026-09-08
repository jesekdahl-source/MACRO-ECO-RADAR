\
from __future__ import annotations
import io
import math
from datetime import datetime, timezone
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import requests
import yfinance as yf

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"

def fetch_fred(series: str, timeout: int = 20) -> pd.Series:
    r = requests.get(FRED_CSV.format(series=series), timeout=timeout, headers={"User-Agent": "macro-dashboard/1.0"})
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    if df.shape[1] < 2:
        raise ValueError(f"Unexpected FRED response for {series}")
    date_col, value_col = df.columns[0], df.columns[1]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[value_col] = pd.to_numeric(df[value_col].replace(".", np.nan), errors="coerce")
    s = df.dropna().set_index(date_col)[value_col].sort_index()
    s.name = series
    return s

def transform_series(s: pd.Series, transform: str) -> pd.Series:
    s = s.dropna().astype(float)
    if transform == "last":
        return s
    if transform == "yoy_pct":
        # FRED series have mixed frequencies; 12 periods is appropriate for monthly,
        # 4 for quarterly, and 52 for weekly. Infer from median spacing.
        if len(s) < 3:
            return pd.Series(dtype=float)
        gaps = s.index.to_series().diff().dt.days.dropna()
        med = gaps.median() if not gaps.empty else 30
        periods = 12
        if med <= 10:
            periods = 52
        elif med >= 70:
            periods = 4
        return s.pct_change(periods=periods) * 100.0
    raise ValueError(f"Unknown transform: {transform}")

def _get_capex_series(ticker: str) -> pd.Series:
    qcf = yf.Ticker(ticker).quarterly_cashflow
    if qcf is None or qcf.empty:
        raise ValueError("No quarterly cash-flow data")
    candidates = [
        "Capital Expenditure",
        "Capital Expenditures",
        "Purchase Of PPE",
        "Purchases Of Property Plant And Equipment",
    ]
    row = None
    for c in candidates:
        if c in qcf.index:
            row = qcf.loc[c]
            break
    if row is None:
        # fuzzy fallback
        for idx in qcf.index:
            if "capital" in str(idx).lower() and "expend" in str(idx).lower():
                row = qcf.loc[idx]
                break
    if row is None:
        raise ValueError(f"CapEx row unavailable for {ticker}")
    s = pd.to_numeric(row, errors="coerce").dropna()
    s.index = pd.to_datetime(s.index)
    s = s.sort_index()
    # cashflow CapEx often comes as a negative number; stress logic uses magnitude
    s = s.abs()
    return s

def fetch_capex_yoy(ticker: str) -> pd.Series:
    s = _get_capex_series(ticker)
    # Quarterly YoY, 4 quarters
    yoy = s.pct_change(4) * 100.0
    return yoy

def fetch_real_wage_yoy() -> pd.Series:
    earnings = fetch_fred("CES0500000003")
    cpi = fetch_fred("CPIAUCSL")
    df = pd.concat([earnings.rename("earnings"), cpi.rename("cpi")], axis=1).dropna()
    real = df["earnings"] / df["cpi"] * 100.0
    return real.pct_change(12) * 100.0



def fetch_yf_market(ticker: str, transform: str) -> pd.Series:
    """
    Returns a time series already transformed to the requested market metric.
    Uses daily Yahoo Finance history so it works without API keys.
    """
    hist = yf.download(ticker, period="2y", interval="1d", auto_adjust=False, progress=False, threads=False)
    if hist is None or hist.empty:
        raise ValueError(f"No market history for {ticker}")

    if isinstance(hist.columns, pd.MultiIndex):
        # yfinance may return MultiIndex columns even for one ticker
        close = hist["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
    else:
        close = hist["Close"]

    close = pd.to_numeric(close, errors="coerce").dropna()
    close.index = pd.to_datetime(close.index)
    close = close.sort_index()

    if transform == "last_price":
        return close
    if transform == "return_1m":
        return close.pct_change(21) * 100.0
    if transform == "distance_50dma":
        ma = close.rolling(50).mean()
        return (close / ma - 1.0) * 100.0
    if transform == "distance_200dma":
        ma = close.rolling(200).mean()
        return (close / ma - 1.0) * 100.0

    raise ValueError(f"Unknown YF market transform: {transform}")


def fetch_watchlist_quote(ticker: str):
    hist = yf.download(ticker, period="10d", interval="1d", auto_adjust=False, progress=False, threads=False)
    if hist is None or hist.empty:
        raise ValueError(f"No quote data for {ticker}")

    if isinstance(hist.columns, pd.MultiIndex):
        close = hist["Close"]
        high = hist["High"]
        low = hist["Low"]
        if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
        if isinstance(high, pd.DataFrame): high = high.iloc[:, 0]
        if isinstance(low, pd.DataFrame): low = low.iloc[:, 0]
    else:
        close, high, low = hist["Close"], hist["High"], hist["Low"]

    close = pd.to_numeric(close, errors="coerce").dropna()
    high = pd.to_numeric(high, errors="coerce").dropna()
    low = pd.to_numeric(low, errors="coerce").dropna()

    if close.empty:
        raise ValueError(f"No close data for {ticker}")

    latest = float(close.iloc[-1])
    prev = float(close.iloc[-2]) if len(close) >= 2 else np.nan
    change = latest - prev if not np.isnan(prev) else np.nan
    pct = change / abs(prev) * 100.0 if not np.isnan(prev) and prev != 0 else np.nan
    return {
        "ticker": ticker.upper(),
        "last": latest,
        "change": change,
        "pct": pct,
        "high": float(high.tail(5).max()) if not high.empty else np.nan,
        "low": float(low.tail(5).min()) if not low.empty else np.nan,
        "updated": close.index[-1],
    }

def fetch_metric(metric) -> Tuple[pd.Series, str]:
    if metric.source == "FRED":
        raw = fetch_fred(metric.series)
        return transform_series(raw, metric.transform), f"FRED:{metric.series}"
    if metric.source == "YF" and metric.transform == "capex_yoy":
        return fetch_capex_yoy(metric.ticker), f"Yahoo Finance:{metric.ticker}"
    if metric.source == "YF_MARKET":
        return fetch_yf_market(metric.ticker, metric.transform), f"Yahoo Finance:{metric.ticker}"
    if metric.source == "COMPOSITE" and metric.transform == "real_wage_yoy":
        return fetch_real_wage_yoy(), "FRED:CES0500000003/CPIAUCSL"
    raise ValueError(f"Unsupported metric source {metric.source}")

def get_latest_point(s: pd.Series):
    s = s.dropna()
    if s.empty:
        return None, None
    return s.index[-1], float(s.iloc[-1])

def data_age_days(ts) -> int | None:
    if ts is None:
        return None
    now = pd.Timestamp.now(tz="UTC").tz_localize(None)
    t = pd.Timestamp(ts).tz_localize(None) if pd.Timestamp(ts).tzinfo else pd.Timestamp(ts)
    return int((now.normalize() - t.normalize()).days)

def format_value(value, unit):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "N/A"
    if unit == "$":
        return f"${value:,.2f}"
    if unit == "%":
        return f"{value:.2f}%"
    if unit == "k":
        return f"{value:,.0f}k"
    if unit == "net %":
        return f"{value:.1f}%"
    return f"{value:,.2f}"
