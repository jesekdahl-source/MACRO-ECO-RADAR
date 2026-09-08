
NEWS_CONFIG = {
    "Housing": {
        "queries": [
            '"US housing market" mortgage delinquencies foreclosures home prices when:1d',
            '"mortgage rates" housing inventory homebuilders when:1d',
        ],
        "risk_up": [
            "delinquency", "delinquencies", "foreclosure", "foreclosures", "defaults",
            "mortgage rates rise", "mortgage rates jump", "home prices fall", "housing slowdown",
            "inventory surge", "sales plunge", "affordability crisis", "credit stress",
        ],
        "risk_down": [
            "mortgage rates fall", "mortgage rates drop", "home sales rise", "housing recovery",
            "delinquencies fall", "foreclosures fall", "affordability improves", "prices stabilize",
        ],
    },
    "Consumer Credit": {
        "queries": [
            '"consumer credit" credit card delinquencies charge-offs banks when:1d',
            '"credit limits" banks JPMorgan credit cards when:1d',
            '"auto loan" delinquencies subprime consumer when:1d',
        ],
        "risk_up": [
            "cut credit limits", "lower credit limits", "tighten credit limits", "delinquency",
            "delinquencies", "charge-off", "charge offs", "defaults", "late payments",
            "subprime stress", "credit card stress", "consumer debt stress",
        ],
        "risk_down": [
            "raise credit limits", "delinquencies fall", "charge-offs fall", "defaults fall",
            "consumer credit improves", "household balance sheets improve",
        ],
    },
    "Credit Tightness": {
        "queries": [
            '"bank lending standards" credit tightening loans banks when:1d',
            '"credit conditions" banks lending standards corporate credit when:1d',
            'JPMorgan banks "credit limits" lending when:1d',
        ],
        "risk_up": [
            "tighten lending", "tightening standards", "credit tightening", "restrict lending",
            "cut credit limits", "lower credit limits", "loan standards tighten", "banks pull back",
            "credit crunch", "funding stress", "spreads widen",
        ],
        "risk_down": [
            "ease lending", "easing standards", "credit conditions improve", "spreads narrow",
            "banks expand lending", "raise credit limits",
        ],
    },
    "US10Y / Financing Costs": {
        "queries": [
            '"10-year Treasury yield" borrowing costs financing costs when:1d',
            '"Treasury yields" mortgage rates corporate borrowing when:1d',
        ],
        "risk_up": [
            "yields rise", "yield rises", "yield jumps", "yield surges", "borrowing costs rise",
            "financing costs rise", "real yields rise", "mortgage rates rise",
        ],
        "risk_down": [
            "yields fall", "yield falls", "yield drops", "borrowing costs fall",
            "financing costs ease", "mortgage rates fall",
        ],
    },
    "Oil / Inflation": {
        "queries": [
            'WTI oil crude inflation gasoline OPEC when:1d',
            '"oil prices" inflation expectations energy when:1d',
            'EIA crude oil inventories gasoline when:1d',
        ],
        "risk_up": [
            "oil rises", "oil jumps", "oil surges", "crude rises", "crude jumps", "supply disruption",
            "production cut", "opec cuts", "inflation rises", "inflation accelerates",
            "gasoline prices rise", "energy prices rise",
        ],
        "risk_down": [
            "oil falls", "oil drops", "crude falls", "supply increases", "production rises",
            "inflation cools", "inflation eases", "gasoline prices fall", "energy prices fall",
        ],
    },
    "Low-Income Consumer": {
        "queries": [
            '"low income consumers" spending stress delinquencies when:1d',
            '"subprime consumers" credit card auto loan when:1d',
            'Walmart Dollar General consumer spending low income when:1d',
        ],
        "risk_up": [
            "consumer stress", "spending slows", "spending falls", "delinquency", "delinquencies",
            "late payments", "defaults", "food insecurity", "subprime stress", "wage pressure",
            "cut spending", "financial strain",
        ],
        "risk_down": [
            "spending improves", "real wages rise", "delinquencies fall", "defaults fall",
            "consumer confidence improves", "financial strain eases",
        ],
    },
    "AI CapEx": {
        "queries": [
            '"AI capex" Microsoft Meta Amazon Alphabet data centers when:1d',
            '"data center spending" AI infrastructure capex when:1d',
            'Nvidia AI demand hyperscaler capex when:1d',
        ],
        "risk_up": [
            "capex cut", "cuts capex", "spending cut", "spending slowdown", "demand weakens",
            "data center slowdown", "ai spending slows", "guidance cut",
        ],
        "risk_down": [
            "capex rises", "raises capex", "spending increase", "spending accelerates",
            "data center demand strong", "ai demand strong", "guidance raised",
        ],
    },
    "Labor Market": {
        "queries": [
            '"US labor market" unemployment payrolls layoffs jobless claims when:1d',
            'JOLTS hiring layoffs unemployment claims when:1d',
        ],
        "risk_up": [
            "layoffs", "job cuts", "unemployment rises", "jobless claims rise", "hiring slows",
            "payrolls miss", "jobs decline", "openings fall", "labor market weakens",
        ],
        "risk_down": [
            "hiring rises", "payrolls beat", "jobless claims fall", "unemployment falls",
            "openings rise", "labor market strengthens", "wage growth improves",
        ],
    },

    "Nasdaq 100": {
        "queries": [
            '"Nasdaq 100" technology stocks yields AI when:1d',
            'Nasdaq megacap tech market when:1d',
        ],
        "risk_up": [
            "nasdaq falls", "nasdaq drops", "tech selloff", "megacap selloff", "valuation concern",
            "yields rise", "risk-off", "semiconductor weakness", "ai spending concern",
        ],
        "risk_down": [
            "nasdaq rises", "nasdaq rallies", "tech rally", "megacap gains", "risk-on",
            "yields fall", "semiconductor strength", "ai demand strong",
        ],
    },
    "S&P 500": {
        "queries": [
            '"S&P 500" stocks market breadth earnings when:1d',
            '"S&P 500" yields inflation recession when:1d',
        ],
        "risk_up": [
            "s&p 500 falls", "stocks fall", "selloff", "market breadth weakens", "earnings warning",
            "recession risk", "yields rise", "risk-off",
        ],
        "risk_down": [
            "s&p 500 rises", "stocks rally", "market breadth improves", "earnings beat",
            "soft landing", "yields fall", "risk-on",
        ],
    },

}
