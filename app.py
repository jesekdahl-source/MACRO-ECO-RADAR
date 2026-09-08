
from __future__ import annotations
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from config import CATEGORIES, CATEGORY_ORDER
from data_sources import fetch_metric, get_latest_point, data_age_days, format_value, fetch_watchlist_quote
from scoring import score_metric, weighted_average
from news_sources import fetch_all_news, news_tone_summary

st.set_page_config(page_title="US Macro Stress Dashboard", page_icon="🇺🇸", layout="wide")

# Auto-reload the page every 30 minutes. News cache itself is 15 minutes.
components.html(
    """
    <script>
    setTimeout(function() {
        window.parent.location.reload();
    }, 1800000);
    </script>
    """,
    height=0,
)

CSS = """
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem; max-width: 1680px;}
html, body, [class*="css"] {font-family: Inter, Segoe UI, Arial, sans-serif;}
.hero-card {
    border: 1px solid rgba(128,128,128,0.22);
    border-radius: 18px;
    padding: 18px 18px 14px 18px;
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.015));
    min-height: 150px;
}
.category-shell {
    border: 1px solid rgba(128,128,128,0.22);
    border-radius: 20px;
    padding: 18px;
    background: rgba(255,255,255,0.02);
    margin-bottom: 16px;
}
.score-big {font-size: 2.1rem; font-weight: 800; line-height: 1.1;}
.label-dim {font-size: 0.82rem; letter-spacing: 0.02em; color: #A9B2BD;}
.summary-text {font-size: 1rem; line-height: 1.45;}
.kpi-chip {
    display: inline-block;
    padding: 7px 10px;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 999px;
    margin-right: 8px;
    margin-bottom: 8px;
    background: rgba(255,255,255,0.03);
    font-size: 0.85rem;
}
.news-badge {
    display: inline-block;
    min-width: 27px;
    padding: 3px 8px;
    border-radius: 999px;
    background: #D92D20;
    color: white;
    font-weight: 800;
    text-align: center;
    font-size: 0.82rem;
}
.tape-wrap {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    overflow-x: auto;
    overflow-y: hidden;
    margin-top: 12px;
    background: rgba(255,255,255,0.02);
}
.tape-table {
    width: 100%;
    min-width: 1120px;
    border-collapse: collapse;
    font-size: 0.90rem;
}
.tape-table thead th {
    background: #141a22;
    color: #F4F7FB;
    padding: 9px 10px;
    text-align: right;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    white-space: nowrap;
}
.tape-table thead th:first-child,
.tape-table tbody td:first-child {text-align:left;}
.tape-table tbody td {
    padding: 10px 10px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    white-space: nowrap;
    text-align:right;
}
.pos { color: #4DA3FF; font-weight: 700; }
.neg { color: #FF5C5C; font-weight: 700; }
.neu { color: #D5D9E0; }
.good { color: #61D88B; font-weight: 700; }
.warn { color: #F2C94C; font-weight: 700; }
.bad  { color: #FF8A47; font-weight: 700; }
.bad2 { color: #FF5C5C; font-weight: 700; }
.small-note {font-size: 0.85rem; color: #98A2AE;}
.news-card {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    padding: 14px 15px;
    margin-bottom: 10px;
    background: rgba(255,255,255,0.02);
}
.news-source {font-size:0.82rem; color:#9AA4B2;}
.tone-up {color:#FF6B6B; font-weight:750;}
.tone-down {color:#61D88B; font-weight:750;}
.tone-neutral {color:#C9D1D9; font-weight:750;}
.fact-head, .fact-row {
    display: grid;
    grid-template-columns: 52px 2.8fr 1.2fr 1.2fr 1.25fr 1.25fr 0.9fr 0.9fr;
    gap: 8px;
    align-items: center;
}
.fact-head {
    padding: 8px 10px;
    margin-top: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.10);
    color: #F4F7FB;
    font-size: 0.84rem;
    font-weight: 750;
}
.fact-row {
    padding: 8px 10px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.fact-row-wrap {
    border-radius: 12px;
    background: rgba(255,255,255,0.02);
    margin-bottom: 6px;
}
.fact-watch-card {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 8px;
    background: rgba(255,255,255,0.02);
}
@media (max-width: 1200px) {
    .fact-head, .fact-row {
        grid-template-columns: 52px 2.2fr 1.1fr 1.1fr 1.1fr 1.1fr 0.8fr 0.8fr;
        font-size: 0.82rem;
    }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def fmt_date(ts):
    if ts is None:
        return "N/A"
    return pd.Timestamp(ts).strftime("%Y-%m-%d")

def age_badge(days):
    if days is None:
        return "N/A"
    if days <= 7: cls = "good"
    elif days <= 30: cls = "warn"
    elif days <= 60: cls = "bad"
    else: cls = "bad2"
    return f'<span class="{cls}">{days}d</span>'

def compute_change_stats(history):
    if not isinstance(history, pd.Series):
        return {"delta": np.nan, "pct": np.nan, "high": np.nan, "low": np.nan}
    h = history.dropna()
    if h.empty:
        return {"delta": np.nan, "pct": np.nan, "high": np.nan, "low": np.nan}
    latest = float(h.iloc[-1])
    prev = float(h.iloc[-2]) if len(h) >= 2 else np.nan
    delta = latest - prev if not np.isnan(prev) else np.nan
    pct = (delta / abs(prev) * 100.0) if (not np.isnan(prev) and prev != 0) else np.nan
    recent = h.tail(120)
    return {
        "delta": delta, "pct": pct,
        "high": float(recent.max()) if not recent.empty else np.nan,
        "low": float(recent.min()) if not recent.empty else np.nan,
    }

def format_delta(delta, unit):
    if delta is None or (isinstance(delta, float) and np.isnan(delta)):
        return '<span class="neu">N/A</span>'
    if delta > 0:
        return f'<span class="pos">▲ {format_value(delta, unit)}</span>'
    if delta < 0:
        return f'<span class="neg">▼ {format_value(abs(delta), unit)}</span>'
    return f'<span class="neu">→ {format_value(delta, unit)}</span>'

def format_pct_change(pct):
    if pct is None or (isinstance(pct, float) and np.isnan(pct)):
        return '<span class="neu">N/A</span>'
    if pct > 0:
        return f'<span class="pos">▲ {pct:.2f}%</span>'
    if pct < 0:
        return f'<span class="neg">▼ {abs(pct):.2f}%</span>'
    return f'<span class="neu">→ {pct:.2f}%</span>'


def build_ticker_table(rows):
    parts = []
    for r in rows:
        stats = compute_change_stats(r["history"])
        parts.append(
            "<tr>"
            f"<td><b>{r['label']}</b></td>"
            f"<td>{r['display']}</td>"
            f"<td>{format_delta(stats['delta'], r['unit'])}</td>"
            f"<td>{format_pct_change(stats['pct'])}</td>"
            f"<td>{fmt_date(r['date'])}</td>"
            f"<td>{age_badge(r['age'])}</td>"
            f"<td>{format_value(stats['high'], r['unit']) if not np.isnan(stats['high']) else 'N/A'}</td>"
            f"<td>{format_value(stats['low'], r['unit']) if not np.isnan(stats['low']) else 'N/A'}</td>"
            "</tr>"
        )
    return (
        "<div class='tape-wrap'><table class='tape-table'>"
        "<thead><tr>"
        "<th>MARKET</th><th>LATEST</th><th>CHANGE</th><th>% CHANGE</th>"
        "<th>UPDATED</th><th>AGE</th><th>HIGH</th><th>LOW</th>"
        "</tr></thead>"
        f"<tbody>{''.join(parts)}</tbody></table></div>"
    )


def _get_watchlist_symbols():
    raw = st.query_params.get("watchlist", "")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""
    symbols = [x.strip().upper() for x in str(raw).split(",") if x.strip()]
    return list(dict.fromkeys(symbols))[:30]

def _set_watchlist_symbols(symbols):
    symbols = list(dict.fromkeys([x.strip().upper() for x in symbols if x.strip()]))[:30]
    if symbols:
        st.query_params["watchlist"] = ",".join(symbols)
    elif "watchlist" in st.query_params:
        del st.query_params["watchlist"]

@st.cache_data(ttl=60*5, show_spinner=False)
def load_watchlist_quotes(symbols_tuple):
    rows = []
    for symbol in symbols_tuple:
        try:
            rows.append(fetch_watchlist_quote(symbol))
        except Exception as e:
            rows.append({"ticker": symbol, "error": str(e)})
    return rows

def render_watchlist(rows):
    html_rows = []
    for r in rows:
        if "error" in r:
            html_rows.append(
                f"<tr><td><b>{r['ticker']}</b></td><td colspan='6' class='neg'>No data</td></tr>"
            )
            continue
        chg = r["change"]
        pct = r["pct"]
        if chg > 0:
            change_html = f'<span class="pos">▲ {chg:.2f}</span>'
            pct_html = f'<span class="pos">▲ {pct:.2f}%</span>'
        elif chg < 0:
            change_html = f'<span class="neg">▼ {abs(chg):.2f}</span>'
            pct_html = f'<span class="neg">▼ {abs(pct):.2f}%</span>'
        else:
            change_html = '<span class="neu">→ 0.00</span>'
            pct_html = '<span class="neu">→ 0.00%</span>'

        html_rows.append(
            "<tr>"
            f"<td><b>{r['ticker']}</b></td>"
            f"<td>{r['last']:.2f}</td>"
            f"<td>{change_html}</td>"
            f"<td>{pct_html}</td>"
            f"<td>{pd.Timestamp(r['updated']).strftime('%Y-%m-%d')}</td>"
            f"<td>{r['high']:.2f}</td>"
            f"<td>{r['low']:.2f}</td>"
            "</tr>"
        )

    if not html_rows:
        return "<div class='small-note'>Your watchlist is empty. Add a ticker below.</div>"

    return (
        "<div class='tape-wrap'><table class='tape-table'>"
        "<thead><tr><th>TICKER</th><th>LAST</th><th>CHANGE</th><th>% CHANGE</th>"
        "<th>UPDATED</th><th>5D HIGH</th><th>5D LOW</th></tr></thead>"
        f"<tbody>{''.join(html_rows)}</tbody></table></div>"
    )


def _get_fact_watchlist_items():
    raw = st.query_params.get("fact_watchlist", "")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""
    items = []
    for item in str(raw).split(","):
        item = item.strip()
        if not item or "::" not in item:
            continue
        items.append(item)
    return list(dict.fromkeys(items))[:60]

def _set_fact_watchlist_items(items):
    clean = list(dict.fromkeys([x.strip() for x in items if x.strip()]))[:60]
    if clean:
        st.query_params["fact_watchlist"] = ",".join(clean)
    elif "fact_watchlist" in st.query_params:
        del st.query_params["fact_watchlist"]

def _fact_id(category, row_key):
    return f"{category}::{row_key}"

def render_fact_watchlist(data, fact_ids):
    rows = []
    for fid in fact_ids:
        if "::" not in fid:
            continue
        cat, key = fid.split("::", 1)
        category_block = data.get(cat, {})
        for r in category_block.get("rows", []):
            if r.get("key") == key:
                stats = compute_change_stats(r["history"])
                rows.append({
                    "fact_id": fid,
                    "category": cat,
                    "label": r["label"],
                    "latest": r["display"],
                    "change": stats["delta"],
                    "pct": stats["pct"],
                    "updated": fmt_date(r["date"]),
                    "age": r["age"],
                    "unit": r["unit"],
                })
                break
    return rows

def render_interactive_fact_header():
    st.markdown(
        """<div class="fact-head">
            <div></div>
            <div>MARKET</div>
            <div>LATEST</div>
            <div>CHANGE</div>
            <div>% CHANGE</div>
            <div>UPDATED</div>
            <div>AGE</div>
            <div>LOW</div>
        </div>""",
        unsafe_allow_html=True
    )

def render_interactive_fact_rows(cat, rows, fact_watchlist):
    render_interactive_fact_header()
    for r in rows:
        fact_id = _fact_id(cat, r["key"])
        in_watch = fact_id in fact_watchlist
        stats = compute_change_stats(r["history"])
        low_txt = format_value(stats["low"], r["unit"]) if not np.isnan(stats["low"]) else "N/A"
        score_txt = "N/A" if np.isnan(r["score"]) else f"{r['score']:.0f}"

        wrap = st.container()
        with wrap:
            cols = st.columns([0.55, 3.0, 1.2, 1.2, 1.3, 1.25, 0.9, 0.9], vertical_alignment="center")
            with cols[0]:
                if in_watch:
                    clicked = st.button("✓", key=f"fact_add_{cat}_{r['key']}", help="Already in watchlist. Click to remove.")
                    if clicked:
                        fact_watchlist = [x for x in fact_watchlist if x != fact_id]
                        _set_fact_watchlist_items(fact_watchlist)
                        st.rerun()
                else:
                    clicked = st.button("＋", key=f"fact_add_{cat}_{r['key']}", help="Add this fact to your watchlist.")
                    if clicked:
                        fact_watchlist.append(fact_id)
                        _set_fact_watchlist_items(fact_watchlist)
                        st.rerun()
            cols[1].markdown(f"**{r['label']}**")
            cols[2].markdown(r["display"])
            cols[3].markdown(format_delta(stats["delta"], r["unit"]), unsafe_allow_html=True)
            cols[4].markdown(format_pct_change(stats["pct"]), unsafe_allow_html=True)
            cols[5].markdown(fmt_date(r["date"]))
            cols[6].markdown(age_badge(r["age"]), unsafe_allow_html=True)
            cols[7].markdown(low_txt)


@st.cache_data(ttl=60*60*6, show_spinner=False)
def load_all_data():
    results, histories, errors = {}, {}, []
    for cat_name, cfg in CATEGORIES.items():
        rows, hseries = [], []
        for m in cfg["metrics"]:
            try:
                s, src = fetch_metric(m)
                ts, val = get_latest_point(s)
                sc = score_metric(m, val) if val is not None else np.nan
                hs = s.dropna().tail(180).apply(lambda x: score_metric(m, float(x)))
                hs.name = m.key
                hseries.append((hs, m.weight))
                rows.append({
                    "key": m.key, "label": m.label, "value": val,
                    "display": format_value(val, m.unit), "date": ts,
                    "age": data_age_days(ts), "score": sc, "source": src,
                    "unit": m.unit, "history": s.tail(300),
                })
            except Exception as e:
                errors.append(f"{cat_name} / {m.label}: {e}")
                rows.append({
                    "key": m.key, "label": m.label, "value": None, "display": "N/A",
                    "date": None, "age": None, "score": np.nan, "source": m.source,
                    "unit": m.unit, "history": pd.Series(dtype=float)
                })

        results[cat_name] = {"rows": rows}
        histories[cat_name] = pd.Series(dtype=float)
    return results, histories, errors

@st.cache_data(ttl=60*15, show_spinner=False)
def load_news():
    return fetch_all_news(hours=24, max_items=25)

with st.spinner("Loading macro data and scanning fresh news/reports…"):
    data, histories, errors = load_all_data()
    news_data, news_errors = load_news()

if st.button("↻ Refresh now", type="secondary"):
    load_all_data.clear()
    load_news.clear()
    st.rerun()


st.title("🇺🇸 US Macro Stress Dashboard")
st.caption("Facts + sentiment monitor. Fresh news, reports and articles are scanned every refresh; no composite scores or advisory ratings are used.")



# ---------- My Watchlist ----------
st.subheader("My Watchlist")
st.caption("Use the ＋ button next to any fact row to add it to your fact watchlist. You can also keep a separate custom ticker watchlist.")

fact_watchlist = _get_fact_watchlist_items()
watch_symbols = _get_watchlist_symbols()

watch_tab1, watch_tab2 = st.tabs(["Watched Facts", "Ticker Watchlist"])

with watch_tab1:
    fact_rows = render_fact_watchlist(data, fact_watchlist)
    if not fact_rows:
        st.info("No watched facts yet. Open any category → Facts and click the ＋ button on the left side of a row.")
    else:
        for item in fact_rows:
            row_cols = st.columns([0.7, 2.8, 1.1, 1.2, 1.2, 1.2, 0.9], vertical_alignment="center")
            with row_cols[0]:
                if st.button("✕", key=f"remove_fact_{item['fact_id']}", use_container_width=True):
                    fact_watchlist = [x for x in fact_watchlist if x != item["fact_id"]]
                    _set_fact_watchlist_items(fact_watchlist)
                    st.rerun()
            row_cols[1].markdown(f"**{item['label']}**  \n<span class='small-note'>{item['category']}</span>", unsafe_allow_html=True)
            row_cols[2].markdown(item["latest"])
            row_cols[3].markdown(format_delta(item["change"], item["unit"]), unsafe_allow_html=True)
            row_cols[4].markdown(format_pct_change(item["pct"]), unsafe_allow_html=True)
            row_cols[5].markdown(item["updated"])
            row_cols[6].markdown(age_badge(item["age"]), unsafe_allow_html=True)

with watch_tab2:
    st.caption("Add your own Yahoo Finance tickers. The list is stored in the page URL, so it survives refreshes and remains personal to your link.")
    w1, w2 = st.columns([3, 1])

    with w1:
        new_symbol = st.text_input(
            "Add ticker",
            placeholder="Examples: AAPL, MSFT, NVDA, ^NDX, ^GSPC, GC=F, CL=F",
            label_visibility="collapsed",
            key="watchlist_add"
        )
    with w2:
        add_clicked = st.button("＋ Add to Watchlist", use_container_width=True)

    if add_clicked and new_symbol.strip():
        symbol = new_symbol.strip().upper()
        if symbol not in watch_symbols:
            watch_symbols.append(symbol)
            _set_watchlist_symbols(watch_symbols)
            load_watchlist_quotes.clear()
            st.rerun()

    if watch_symbols:
        quotes = load_watchlist_quotes(tuple(watch_symbols))
        st.markdown(render_watchlist(quotes), unsafe_allow_html=True)

        remove_cols = st.columns(min(6, len(watch_symbols)))
        for i, symbol in enumerate(watch_symbols):
            with remove_cols[i % len(remove_cols)]:
                if st.button(f"✕ {symbol}", key=f"remove_{symbol}", use_container_width=True):
                    watch_symbols = [s for s in watch_symbols if s != symbol]
                    _set_watchlist_symbols(watch_symbols)
                    load_watchlist_quotes.clear()
                    st.rerun()
    else:
        st.info("Your ticker watchlist is empty. Add a symbol above.")


# ---------- Macro Overview ----------
st.subheader("Macro Overview")
st.caption("A compact factual snapshot. No composite scores or advisory ratings are used.")

overview_rows = []
for cat in CATEGORY_ORDER:
    rows = data.get(cat, {}).get("rows", [])
    fresh = news_data.get(cat, {}).get("fresh_count", 0)
    latest_dates = [r["date"] for r in rows if r.get("date") is not None]
    latest_update = max(latest_dates).strftime("%Y-%m-%d") if latest_dates else "N/A"
    overview_rows.append({
        "Category": cat,
        "Facts tracked": len(rows),
        "Latest fact update": latest_update,
        "New news / 24h": fresh,
    })
st.dataframe(pd.DataFrame(overview_rows), use_container_width=True, hide_index=True)

# ---------- Category tabs with notification counts ----------
st.subheader("Categories")
tab_labels = []
for cat in CATEGORY_ORDER:
    n = news_data.get(cat, {}).get("fresh_count", 0)
    badge = f" 🔔{n}" if n else ""
    tab_labels.append(f"{CATEGORIES[cat]['icon']} {cat}{badge}")
tabs = st.tabs(tab_labels)

for tab, cat in zip(tabs, CATEGORY_ORDER):
    with tab:
        cfg = CATEGORIES[cat]
        d = data[cat]
        rows = d["rows"]
        fresh_count = news_data.get(cat, {}).get("fresh_count", 0)

        st.markdown(
            f"""<div class="category-shell">
                <div class="label-dim">{cfg["icon"]} {cat.upper()} • {len(rows)} fact indicators • 🔔 {fresh_count} new items / 24h</div>
                <div style="margin-top:8px"><b>Facts and source updates</b></div>
            </div>""",
            unsafe_allow_html=True
        )

        view = st.segmented_control(
            "View",
            options=["Facts", "Sentiment"],
            default="Facts",
            key=f"view_{cat}"
        )

        if view == "Facts":
            st.caption("Use the ＋ button on the left to add any fact directly to your watchlist on the home page.")
            render_interactive_fact_rows(cat, rows, fact_watchlist)
            st.markdown("**Summary:** Latest available factual indicators are shown above. Use the Sentiment view for related news, reports and articles.")

            c_left, c_right = st.columns([1.1, 1])
            with c_left:
                st.markdown("##### Full fact table")
                fact_rows = []
                for r in rows:
                    stats = compute_change_stats(r["history"])
                    fact_rows.append({
                        "Market": r["label"],
                        "Latest": r["display"],
                        "Change": format_value(stats["delta"], r["unit"]) if not np.isnan(stats["delta"]) else None,
                        "% Change": round(stats["pct"], 2) if not np.isnan(stats["pct"]) else None,
                        "Updated": fmt_date(r["date"]),
                        "Age (days)": r["age"],
                        "Source": r["source"],
                    })
                st.dataframe(pd.DataFrame(fact_rows), use_container_width=True, hide_index=True)
            with c_right:
                st.markdown("##### Latest fact updates")
                recent_updates = sorted(
                    [
                        {"Fact": r["label"], "Updated": fmt_date(r["date"]), "Age (days)": r["age"], "Source": r["source"]}
                        for r in rows
                    ],
                    key=lambda x: x["Updated"],
                    reverse=True
                )
                st.dataframe(pd.DataFrame(recent_updates), use_container_width=True, hide_index=True)

            st.markdown("##### Individual fact charts")
            metric_cols = st.columns(2)
            for i, r in enumerate(rows):
                h = r["history"]
                if isinstance(h, pd.Series) and not h.empty:
                    with metric_cols[i % 2]:
                        g = go.Figure(go.Scatter(x=h.index, y=h.values, mode="lines"))
                        g.update_layout(height=235, margin=dict(l=10,r=10,t=35,b=10), title=f'{r["label"]} • {r["source"]}')
                        st.plotly_chart(g, use_container_width=True, key=f"metric_chart_{cat}_{r['key']}")

        else:
            items = news_data.get(cat, {}).get("items", [])
            fresh_items = [x for x in items if x.get("fresh")]
            tone = news_tone_summary(fresh_items)

            n1, n2, n3, n4 = st.columns(4)
            n1.metric("New / 24h", len(fresh_items))
            n2.metric("Risk-up headlines", tone["risk_up"])
            n3.metric("Risk-down headlines", tone["risk_down"])
            n4.metric("News tone", tone["label"])

            st.caption(
                "Sentiment is based on headlines, reports and articles found in the last 24 hours. "
                "It is separate from the factual macro score and is intentionally not mixed into the score yet."
            )

            if not fresh_items:
                st.info("No fresh news or reports found for this category in the last 24 hours.")
            else:
                for item in fresh_items:
                    if item["tone"] == "Risk Up":
                        tone_html = '<span class="tone-up">▲ RISK UP</span>'
                    elif item["tone"] == "Risk Down":
                        tone_html = '<span class="tone-down">▼ RISK DOWN</span>'
                    else:
                        tone_html = '<span class="tone-neutral">● NEUTRAL</span>'

                    st.markdown(
                        f"""<div class="news-card">
                            <div>{tone_html} &nbsp; <span class="news-source">{item['source']} • {item['published_text']}</span></div>
                            <div style="font-size:1.02rem;font-weight:700;margin-top:6px">{item['title']}</div>
                        </div>""",
                        unsafe_allow_html=True
                    )
                    st.link_button("Open article", item["link"], key=f"news_{cat}_{abs(hash(item['link']))}")

st.subheader("Refresh & Sources")
st.write("Facts, news and reports are presented separately. The dashboard does not provide composite risk scores or advisory ratings.")

all_errors = errors + [f"News / {e}" for e in news_errors]
if all_errors:
    with st.expander(f"Data warnings ({len(all_errors)})"):
        for e in all_errors:
            st.code(e)

with st.expander("Methodology & limitations"):
    st.markdown("""
- The dashboard separates **Facts** from **Sentiment**.
- Facts are sourced from FRED, market data, and company financial statement data.
- News/report monitoring uses Google News RSS searches by category.
- The notification badge inside each category is simply the number of fresh items found within the last 24 hours.
- News tone uses a transparent headline classifier: **Risk Up / Risk Down / Neutral**.
- No composite score, overall rating, or investment advice is produced.
- Macro facts refresh on a six-hour cache; news scans refresh every 15 minutes; the page reloads every 30 minutes.
- This is an information and monitoring dashboard.
""")
