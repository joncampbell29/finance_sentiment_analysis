import os
from dotenv import load_dotenv
import sqlite3
import pandas as pd
from utils.av_helpers import get_economic_data
from utils.constants import ECONOMIC_FUNCTIONS
from time import sleep
from tqdm import tqdm
import re
import numpy as np

load_dotenv()
key = os.getenv("ALPHA_VANTAGE_KEY")

db_path = 'data/financials.db'
con = sqlite3.connect(db_path)
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS economic_indicators (
    id INTEGER PRIMARY KEY,
    date TEXT,
    economic_indicator TEXT,
    value REAL,
    interval TEXT,
    unit TEXT,
    maturity TEXT
)
""")
con.commit()

full_data = []
for func in tqdm(ECONOMIC_FUNCTIONS):
    if func == 'TREASURY_YIELD':
        for maturity in ('3month', '2year', '5year', '7year', '10year', '30year'):
            data = get_economic_data(func=func, api_key=key, maturity=maturity)  
            full_data.append(data)
            sleep(10)  
    elif func == 'REAL_GDP':
        data = get_economic_data(func=func, api_key=key, interval='quarterly')
        full_data.append(data)  
        sleep(10)  
    else:
        data = get_economic_data(func=func, api_key=key)
        full_data.append(data) 
        sleep(10)  

data = pd.concat(full_data, axis=0)
data.reset_index(inplace=True, drop=True)
data.index.name = 'id'
data['date'] = pd.to_datetime(data['date'])
vals_to_replace = {
    'Consumer Price Index for all Urban Consumers': "CPI",
    'Unemployment Rate': "Unemployment",
    '10-Year Treasury Constant Maturity Rate': "10-Year Treasury Yield",
    '5-Year Treasury Constant Maturity Rate': "5-Year Treasury Yield",
    'Effective Federal Funds Rate': "Interest Rate",
    '7-Year Treasury Constant Maturity Rate': "7-Year Treasury Yield",
    '2-Year Treasury Constant Maturity Rate': "2-Year Treasury Yield",
    '30-Year Treasury Constant Maturity Rate': "30-Year Treasury Yield",
    '3-Month Treasury Constant Maturity Rate': "3-Month Treasury Yield",
    'Advance Retail Sales: Retail Trade': "Retail Trade",
    'Manufacturer New Orders: Durable Goods': "Durable Goods",
    'Real Gross Domestic Product per Capita': "GDP per Capita",
    'Real Gross Domestic Product': "GDP",
    'Inflation - US Consumer Prices': "Inflation"
}
data['economic_indicator'] = data['economic_indicator'].replace(vals_to_replace)

def split_text(text):
    pattern = re.compile(r'(^\d+-(?:Month|Year))\s(.*)')
    match = re.match(pattern, text)
    if match:
        return match.groups()
    else:
        return np.nan, text

data[['maturity','economic_indicator']] = data['economic_indicator'].apply(lambda x: pd.Series(split_text(x)))


data.to_sql(name="economic_indicators", con=con, if_exists='replace')
con.close()