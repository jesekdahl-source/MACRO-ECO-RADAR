from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Metric:
    key: str
    label: str
    source: str
    series: Optional[str] = None
    ticker: Optional[str] = None
    transform: str = "last"
    unit: str = ""
    higher_is_risk: bool = True
    green: float = 0.0
    yellow: float = 0.0
    orange: float = 0.0
    weight: float = 1.0
    note: str = ""

CATEGORIES = {
    "Housing": {
        "icon": "🏠",
        "weight": 1.10,
        "metrics": [
            Metric(key="mortgage30", label="30Y mortgage rate", source="FRED", series="MORTGAGE30US", transform="last", unit="%", higher_is_risk=True, green=5.5, yellow=6.5, orange=7.5, weight=1.2),
            Metric(key="mortgage_delinq", label="Mortgage delinquency rate", source="FRED", series="DRSFRMACBS", transform="last", unit="%", higher_is_risk=True, green=2.0, yellow=3.0, orange=4.5, weight=1.3),
            Metric(key="home_price_yoy", label="Case-Shiller home prices YoY", source="FRED", series="CSUSHPINSA", transform="yoy_pct", unit="%", higher_is_risk=False, green=4.0, yellow=1.0, orange=-2.0, weight=0.9),
            Metric(key="housing_starts_yoy", label="Housing starts YoY", source="FRED", series="HOUST", transform="yoy_pct", unit="%", higher_is_risk=False, green=5.0, yellow=-5.0, orange=-15.0, weight=0.8),
        ],
    },
    "Consumer Credit": {
        "icon": "💳",
        "weight": 1.10,
        "metrics": [
            Metric(key="revolving_yoy", label="Revolving consumer credit YoY", source="FRED", series="REVOLSL", transform="yoy_pct", unit="%", higher_is_risk=True, green=3.0, yellow=7.0, orange=12.0, weight=0.7),
            Metric(key="cc_delinq", label="Credit-card delinquency rate", source="FRED", series="DRCCLACBS", transform="last", unit="%", higher_is_risk=True, green=2.5, yellow=3.5, orange=5.0, weight=1.5),
            Metric(key="consumer_credit_yoy", label="Total consumer credit YoY", source="FRED", series="TOTALSL", transform="yoy_pct", unit="%", higher_is_risk=True, green=2.0, yellow=5.0, orange=8.0, weight=0.6),
        ],
    },
    "Credit Tightness": {
        "icon": "🏦",
        "weight": 1.20,
        "metrics": [
            Metric(key="sloos_ci", label="Banks tightening C&I standards", source="FRED", series="DRTSCILM", transform="last", unit="net %", higher_is_risk=True, green=0.0, yellow=20.0, orange=40.0, weight=1.3),
            Metric(key="nfci", label="Chicago Fed NFCI", source="FRED", series="NFCI", transform="last", unit="", higher_is_risk=True, green=-0.50, yellow=0.0, orange=0.50, weight=1.0),
            Metric(key="hy_spread", label="US high-yield spread", source="FRED", series="BAMLH0A0HYM2", transform="last", unit="%", higher_is_risk=True, green=3.0, yellow=5.0, orange=8.0, weight=1.4),
        ],
    },
    "US10Y / Financing Costs": {
        "icon": "📈",
        "weight": 1.25,
        "metrics": [
            Metric(key="us10y", label="US 10Y Treasury", source="FRED", series="DGS10", transform="last", unit="%", higher_is_risk=True, green=4.0, yellow=4.75, orange=5.25, weight=1.4),
            Metric(key="real10y", label="10Y real yield", source="FRED", series="DFII10", transform="last", unit="%", higher_is_risk=True, green=1.5, yellow=2.0, orange=2.5, weight=1.0),
            Metric(key="mortgage30_fin", label="30Y mortgage rate", source="FRED", series="MORTGAGE30US", transform="last", unit="%", higher_is_risk=True, green=5.5, yellow=6.5, orange=7.5, weight=1.0),
        ],
    },
    "Oil / Inflation": {
        "icon": "🛢️",
        "weight": 1.10,
        "metrics": [
            Metric(key="wti", label="WTI crude", source="FRED", series="DCOILWTICO", transform="last", unit="$", higher_is_risk=True, green=75.0, yellow=90.0, orange=110.0, weight=1.0),
            Metric(key="cpi_yoy", label="CPI YoY", source="FRED", series="CPIAUCSL", transform="yoy_pct", unit="%", higher_is_risk=True, green=2.5, yellow=3.5, orange=5.0, weight=1.2),
            Metric(key="core_pce_yoy", label="Core PCE YoY", source="FRED", series="PCEPILFE", transform="yoy_pct", unit="%", higher_is_risk=True, green=2.5, yellow=3.2, orange=4.5, weight=1.2),
            Metric(key="breakeven10", label="10Y inflation breakeven", source="FRED", series="T10YIE", transform="last", unit="%", higher_is_risk=True, green=2.3, yellow=2.7, orange=3.2, weight=0.8),
        ],
    },
    "Low-Income Consumer": {
        "icon": "🛒",
        "weight": 1.10,
        "metrics": [
            Metric(key="cc_delinq_low", label="Credit-card delinquency rate", source="FRED", series="DRCCLACBS", transform="last", unit="%", higher_is_risk=True, green=2.5, yellow=3.5, orange=5.0, weight=1.3),
            Metric(key="real_wage_yoy", label="Real avg hourly earnings YoY", source="COMPOSITE", transform="real_wage_yoy", unit="%", higher_is_risk=False, green=1.5, yellow=0.0, orange=-1.5, weight=1.0),
            Metric(key="continuing_claims", label="Continuing jobless claims", source="FRED", series="CCSA", transform="last", unit="k", higher_is_risk=True, green=1700.0, yellow=2000.0, orange=2400.0, weight=1.0),
        ],
    },
    "AI CapEx": {
        "icon": "🤖",
        "weight": 0.80,
        "metrics": [
            Metric(key="msft_capex_yoy", label="Microsoft CapEx YoY", source="YF", ticker="MSFT", transform="capex_yoy", unit="%", higher_is_risk=False, green=20.0, yellow=5.0, orange=-10.0, weight=1.0),
            Metric(key="googl_capex_yoy", label="Alphabet CapEx YoY", source="YF", ticker="GOOGL", transform="capex_yoy", unit="%", higher_is_risk=False, green=20.0, yellow=5.0, orange=-10.0, weight=1.0),
            Metric(key="amzn_capex_yoy", label="Amazon CapEx YoY", source="YF", ticker="AMZN", transform="capex_yoy", unit="%", higher_is_risk=False, green=20.0, yellow=5.0, orange=-10.0, weight=1.0),
            Metric(key="meta_capex_yoy", label="Meta CapEx YoY", source="YF", ticker="META", transform="capex_yoy", unit="%", higher_is_risk=False, green=20.0, yellow=5.0, orange=-10.0, weight=1.0),
        ],
    },
    "Labor Market": {
        "icon": "👷",
        "weight": 1.25,
        "metrics": [
            Metric(key="unrate", label="Unemployment rate", source="FRED", series="UNRATE", transform="last", unit="%", higher_is_risk=True, green=4.0, yellow=4.7, orange=5.5, weight=1.3),
            Metric(key="payroll_yoy", label="Nonfarm payrolls YoY", source="FRED", series="PAYEMS", transform="yoy_pct", unit="%", higher_is_risk=False, green=2.0, yellow=1.0, orange=0.0, weight=1.0),
            Metric(key="jolts", label="JOLTS openings", source="FRED", series="JTSJOL", transform="last", unit="k", higher_is_risk=False, green=8500.0, yellow=7000.0, orange=5500.0, weight=0.8),
            Metric(key="initial_claims", label="Initial jobless claims", source="FRED", series="ICSA", transform="last", unit="k", higher_is_risk=True, green=225.0, yellow=275.0, orange=350.0, weight=1.0),
        ],
    },

    "Nasdaq 100": {
        "icon": "💻",
        "weight": 1.00,
        "metrics": [
            Metric(key="ndx_price", label="Nasdaq 100", source="YF_MARKET", ticker="^NDX", transform="last_price", unit="", higher_is_risk=False, green=0.0, yellow=-2.0, orange=-5.0, weight=0.6),
            Metric(key="ndx_1m", label="Nasdaq 100 1M return", source="YF_MARKET", ticker="^NDX", transform="return_1m", unit="%", higher_is_risk=False, green=3.0, yellow=0.0, orange=-7.0, weight=1.0),
            Metric(key="ndx_50dma", label="Distance vs 50DMA", source="YF_MARKET", ticker="^NDX", transform="distance_50dma", unit="%", higher_is_risk=False, green=3.0, yellow=0.0, orange=-5.0, weight=1.0),
            Metric(key="ndx_200dma", label="Distance vs 200DMA", source="YF_MARKET", ticker="^NDX", transform="distance_200dma", unit="%", higher_is_risk=False, green=5.0, yellow=0.0, orange=-8.0, weight=1.2),
            Metric(key="vix_ndx", label="VIX", source="YF_MARKET", ticker="^VIX", transform="last_price", unit="", higher_is_risk=True, green=16.0, yellow=22.0, orange=30.0, weight=1.1),
        ],
    },
    "S&P 500": {
        "icon": "📊",
        "weight": 1.00,
        "metrics": [
            Metric(key="spx_price", label="S&P 500", source="YF_MARKET", ticker="^GSPC", transform="last_price", unit="", higher_is_risk=False, green=0.0, yellow=-2.0, orange=-5.0, weight=0.6),
            Metric(key="spx_1m", label="S&P 500 1M return", source="YF_MARKET", ticker="^GSPC", transform="return_1m", unit="%", higher_is_risk=False, green=3.0, yellow=0.0, orange=-7.0, weight=1.0),
            Metric(key="spx_50dma", label="Distance vs 50DMA", source="YF_MARKET", ticker="^GSPC", transform="distance_50dma", unit="%", higher_is_risk=False, green=3.0, yellow=0.0, orange=-5.0, weight=1.0),
            Metric(key="spx_200dma", label="Distance vs 200DMA", source="YF_MARKET", ticker="^GSPC", transform="distance_200dma", unit="%", higher_is_risk=False, green=5.0, yellow=0.0, orange=-8.0, weight=1.2),
            Metric(key="vix_spx", label="VIX", source="YF_MARKET", ticker="^VIX", transform="last_price", unit="", higher_is_risk=True, green=16.0, yellow=22.0, orange=30.0, weight=1.1),
        ],
    },

}

CATEGORY_ORDER = list(CATEGORIES.keys())
