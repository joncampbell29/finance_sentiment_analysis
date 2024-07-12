import requests
import os 
import logging
import time
from dotenv import load_dotenv
import pandas as pd
import sys
import os
from tqdm import tqdm
from time import sleep
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from utils.helper_functions import (
    BASE_NYT_URL,
    STOCK_SET,
    MARKET_KEYWORD_SET,
    gen_mkt_filter,
    gen_stock_filter,
    gather_article_set
)

load_dotenv()
key = os.getenv("NYT_API_KEY")
if not key:
    logging.fatal("No API Key")

## Log set up
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename="download_articles.log")

payload = {
    'begin_date': "2014-01-01",
    # 'end_date': "2022-05-31",
    'api-key': key,
    'fl': 'lead_paragraph,snippet,abstract,pub_date,headline',
    'page': 0
}
final_data = []
for mkt_ks in MARKET_KEYWORD_SET:
    df = gather_article_set(
        api_key= key,
        begin_date="2015-01-01",
        fq_generator_func=gen_mkt_filter,
        args= mkt_ks
    )
    final_data.append(df)
    
for stock, ticker in STOCK_SET:
    df = gather_article_set(
        api_key=key,
        begin_date="2015-01-01",
        fq_generator_func=gen_stock_filter,
        stock_name=stock,
        ticker=ticker
    )
    final_data.append(df)

final_df = pd.concat(final_data, ignore_index=True)
final_df.to_csv("data/raw_articles.csv")