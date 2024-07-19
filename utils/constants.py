BASE_NYT_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

Fl_PARAM = 'lead_paragraph,snippet,abstract,pub_date,headline,web_url,source'

MARKET_KEYWORD_SET_OLD = (
    ("earnings", "revenue", "profits", "growth", "sales", "market share", "financial results"),
    ("economic outlook", "GDP", "inflation", "interest rates", "Federal Reserve", "monetary policy"),
    ("fiscal policy", "unemployment", "labor market", "consumer spending", "technology sector"),
    ("healthcare sector", "energy sector", "financial sector", "industrial sector", "consumer goods"),
    ("retail sales", "global trade", "supply chain", "corporate earnings", "stock buybacks"),
    ("dividends", "market volatility", "investor sentiment", "mergers and acquisitions"),
    ("regulatory changes", "geopolitical", "climate change", "sustainability"),
    ("corporate governance", "cybersecurity", "innovation", "market competition")
)

MARKET_KEYWORD_SET = (
    ('corporate governance', 'cybersecurity', 'innovation'),
    ('retail sales', 'global trade', 'supply chain'),
    ("unemployment", "labor market"),
    ('earnings', 'revenue', 'profits'),
    ('regulatory changes', 'geopolitical', 'climate change', 'sustainability')
)


STOCK_SET = (
    ('Apple', 'AAPL'),
    ('Microsoft', 'MSFT'),
    ('Amazon', 'AMZN'),
    ('Tesla', 'TSLA'),
    ('NVIDIA', 'NVDA'),
    ('JPMorgan', 'JPM'),
    ('Johnson & Johnson', 'JNJ'),
    ('Walmart', 'WMT'),
    ('Procter & Gamble', 'PG'),
    ('Pepsi', 'PEP'),
    ('Intel', 'INTC'),
    ('Exxon Mobil', 'XOM'),
    ('Pfizer', 'PFE'),
    ('Bank of America', 'BAC'),
    ('Walt Disney', 'DIS'),
    ('Home Depot', 'HD'),
    ('Verizon', 'VZ'),
    ('Chevron', 'CVX'),
    ('Honeywell', 'HON'),
    ('3M Company', 'MMM'),
    ('Boeing', 'BA'),
    ('IBM', 'IBM'),
    ('General Electric', 'GE'),
    ('General Motors', 'GM'),
    ('Goldman Sachs', 'GS')
 )

STOCK_SET_OLD = (
    ("Apple", "AAPL"),
    ("Microsoft", "MSFT"),
    ("Amazon", "AMZN"),
    ("Tesla", "TSLA"),
    ("Google", "GOOGL"),
    ("Facebook", "META"),
    ("NVIDIA", "NVDA"),
    ("JPMorgan", "JPM"),
    ("Johnson & Johnson", "JNJ"),
    ("Walmart", "WMT"),
    ("Procter & Gamble", "PG"),
    ("Mastercard", "MA"),
    ("Visa", "V"),
    ("Coca-Cola", "KO"),
    ("Pepsi", "PEP"),
    ("Intel", "INTC"),
    ("Cisco", "CSCO"),
    ("Exxon Mobil", "XOM"),
    ("Pfizer", "PFE"),
    ("Bank of America", "BAC"),
    ("Walt Disney", "DIS"),
    ("Home Depot", "HD"),
    ("Netflix", "NFLX"),
    ("Comcast", "CMCSA"),
    ("PayPal", "PYPL"),
    ("Adobe", "ADBE"),
    ("Salesforce", "CRM"),
    ("AT&T", "T"),
    ("Verizon", "VZ"),
    ("Chevron", "CVX"),
    ("Merck & Co", "MRK"),
    ("AbbVie", "ABBV"),
    ("Medtronic", "MDT"),
    ("Honeywell", "HON"),
    ("UPS", "UPS"),
    ("Union Pacific", "UNP"),
    ("Caterpillar", "CAT"),
    ("3M Company", "MMM"),
    ("Boeing", "BA"),
    ("Lockheed Martin", "LMT"),
    ("Qualcomm", "QCOM"),
    ("Texas Instruments", "TXN"),
    ("IBM", "IBM"),
    ("General Electric", "GE"),
    ("Ford Motor", "F"),
    ("General Motors", "GM"),
    ("American Express", "AXP"),
    ("Goldman Sachs", "GS"),
    ("Morgan Stanley", "MS"),
    ("Citigroup", "C")
)