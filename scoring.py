\
from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

COLORS = {
    "green": "🟢",
    "yellow": "🟡",
    "orange": "🟠",
    "red": "🔴",
    "gray": "⚪",
}

def _piecewise_score(value: float, higher_is_risk: bool, green: float, yellow: float, orange: float) -> float:
    """
    Map a metric to 0..100 using three transparent heuristic breakpoints.
    green ~ 25 score, yellow ~ 45, orange ~ 70; beyond orange approaches 95.
    """
    if value is None or np.isnan(value):
        return np.nan

    if not higher_is_risk:
        value, green, yellow, orange = -value, -green, -yellow, -orange

    # higher value = more stress after inversion
    pts_x = np.array([green - abs(yellow-green), green, yellow, orange, orange + abs(orange-yellow)], dtype=float)
    pts_y = np.array([10, 25, 45, 70, 95], dtype=float)
    order = np.argsort(pts_x)
    x = pts_x[order]
    y = pts_y[order]
    score = float(np.interp(value, x, y, left=5, right=100))
    return max(0.0, min(100.0, score))

def score_metric(metric, value: float) -> float:
    return _piecewise_score(
        value=value,
        higher_is_risk=metric.higher_is_risk,
        green=metric.green,
        yellow=metric.yellow,
        orange=metric.orange,
    )

def score_to_band(score: float):
    if score is None or np.isnan(score):
        return "gray", "N/A"
    if score < 35:
        return "green", "Normal"
    if score < 50:
        return "yellow", "Watch"
    if score < 70:
        return "orange", "Warning"
    return "red", "High stress"

def weighted_average(items):
    valid = [(s, w) for s, w in items if s is not None and not np.isnan(s)]
    if not valid:
        return np.nan
    return sum(s*w for s,w in valid) / sum(w for _,w in valid)

def metric_trend(score_series: pd.Series) -> str:
    s = score_series.dropna()
    if len(s) < 2:
        return "→"
    recent = s.iloc[-1]
    prev = s.iloc[-2]
    delta = recent - prev
    if delta >= 4:
        return "↗"
    if delta <= -4:
        return "↘"
    return "→"

def category_summary(category_name: str, rows: List[dict], cat_score: float, trend: str) -> str:
    valid = [r for r in rows if r.get("score") is not None and not np.isnan(r.get("score"))]
    if not valid:
        return "Otillräcklig data för en säker lägesbedömning."
    stressors = sorted(valid, key=lambda r: r["score"], reverse=True)[:2]
    supports = sorted(valid, key=lambda r: r["score"])[:1]
    s1 = ", ".join(f'{r["label"]} ({r["display"]})' for r in stressors)
    s2 = ", ".join(f'{r["label"]} ({r["display"]})' for r in supports)
    direction = {"↗":"försämras", "↘":"förbättras", "→":"är relativt stabil"}[trend]
    return f"{category_name} {direction}. Största stressfaktorer: {s1}. Mest stödjande datapunkt: {s2}."

def domino_risk(category_scores: Dict[str, float], category_trends: Dict[str, str], weights: Dict[str, float]):
    weighted = weighted_average([(category_scores[k], weights.get(k,1.0)) for k in category_scores])
    rising = sum(1 for k,v in category_trends.items() if v == "↗" and category_scores.get(k,0) >= 50)
    red = sum(1 for v in category_scores.values() if v is not None and not np.isnan(v) and v >= 70)
    orange_plus = sum(1 for v in category_scores.values() if v is not None and not np.isnan(v) and v >= 50)
    # Interaction premium: simultaneous cross-category deterioration matters.
    premium = min(18, rising*3 + max(0, orange_plus-3)*2 + red*2)
    score = min(100, weighted + premium) if not np.isnan(weighted) else np.nan
    band, label = score_to_band(score)
    if score >= 70:
        text = f"Hög sammanlagd stress. {orange_plus}/8 områden är orange/röda och {rising} av dessa försämras samtidigt."
    elif score >= 50:
        text = f"Förhöjd systemrisk. {orange_plus}/8 områden är orange/röda. Följ särskilt samtidiga försämringar."
    else:
        text = f"Begränsad domino-risk just nu. {orange_plus}/8 områden är orange/röda."
    return score, band, text
