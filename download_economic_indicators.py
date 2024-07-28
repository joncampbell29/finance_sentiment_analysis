import os
from dotenv import load_dotenv
import sqlite3
import pandas as pd
from utils.av_helpers import get_economic_data
from utils.constants import ECONOMIC_FUNCTIONS
from time import sleep
from tqdm import tqdm

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
    unit TEXT
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

df = pd.concat(full_data, axis=0)
df.reset_index(inplace=True, drop=True)
df.index.name = 'id'
df.to_sql(name="economic_indicators", con=con, if_exists='replace')


