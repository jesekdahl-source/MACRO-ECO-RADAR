\
# 🇺🇸 US Macro Stress Dashboard

En dagligt uppdaterad Streamlit-dashboard för att övervaka åtta delar av USA-ekonomin:

1. Housing
2. Consumer credit
3. Credit tightness
4. US10Y / finansieringskostnad
5. Olja / inflation
6. Low-income consumer
7. AI CapEx
8. Arbetsmarknad

Dashboarden visar:
- 🟢🟡🟠🔴 riskstatus
- 0–100 stress-score
- trend ↗ → ↘
- senaste datapunkt och datans ålder
- kort automatisk sammanfattning per kategori
- detaljtabell och historik
- overall macro stress
- **Domino Risk** när flera stressade områden försämras samtidigt

## Kör lokalt

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Öppna sedan adressen som Streamlit visar, normalt `http://localhost:8501`.

## Datakällor

Majoriteten av makroserierna hämtas direkt från **Federal Reserve Economic Data (FRED)** via deras publika CSV-endpoint.

AI CapEx hämtas via `yfinance` för:
- Microsoft (MSFT)
- Alphabet (GOOGL)
- Amazon (AMZN)
- Meta (META)

### FRED-serier som används
- MORTGAGE30US – 30Y mortgage rate
- DRSFRMACBS – residential mortgage delinquency
- CSUSHPINSA – Case-Shiller home-price index
- HOUST – housing starts
- REVOLSL – revolving consumer credit
- DRCCLACBS – credit-card delinquency
- TOTALSL – total consumer credit
- DRTSCILM – bank tightening standards
- NFCI – Chicago Fed National Financial Conditions Index
- BAMLH0A0HYM2 – high-yield spread
- DGS10 – 10Y Treasury
- DFII10 – 10Y real yield
- DCOILWTICO – WTI
- CPIAUCSL – CPI
- PCEPILFE – core PCE price index
- T10YIE – 10Y breakeven inflation
- CES0500000003 – average hourly earnings
- ICSA / CCSA – initial / continuing claims
- UNRATE – unemployment
- PAYEMS – nonfarm payrolls
- JTSJOL – JOLTS openings

## Daglig uppdatering

Streamlit hämtar om data automatiskt efter 6 timmar (`st.cache_data(ttl=21600)`).

Projektet innehåller också `snapshot.py` och ett GitHub Actions-flöde som kan skapa `latest_snapshot.json` varje morgon.

## Viktigt om scoring

Stressgränserna i `config.py` är **heuristiska och transparenta**. De är inte en ekonometriskt kalibrerad recessionsmodell.

Det är avsiktligt: du kan se exakt vad som får en box att bli gul/orange/röd och justera gränserna efter historisk backtest.

Rekommenderat nästa steg är att backtesta score-systemet mot 2000–2002, 2007–2009, 2020 och 2022–2023 och därefter kalibrera vikterna.


## V5 additions

- Entire UI converted to English.
- Every category now has a **Facts / Sentiment** switch.
- Sentiment view scans fresh news, reports and articles via Google News RSS.
- Category tabs show notification counts such as `Oil / Inflation 🔔3`.
- News items are classified as **Risk Up / Risk Down / Neutral** from headline language.
- Fresh-news window: 24 hours.
- News cache: 15 minutes.
- Automatic page reload: every 30 minutes.
- The old bar-chart stress overview was replaced with a **combined multi-line stress chart** showing all eight categories together.
- News sentiment remains separate from the factual macro score.


## V6 additions

- Added a **personal watchlist** to the main page.
- Add/remove Yahoo Finance tickers directly in the dashboard.
- Watchlist persists through refreshes by storing the ticker list in the page URL.
- Added two new monitored categories:
  - **Nasdaq 100**
  - **S&P 500**
- Each market-index category includes:
  - current index level
  - 1-month return
  - distance vs 50-day moving average
  - distance vs 200-day moving average
  - VIX
- Nasdaq 100 and S&P 500 also have their own news/sentiment searches and notification badges.
