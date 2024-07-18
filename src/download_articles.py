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
from utils.constants import BASE_NYT_URL, STOCK_SET, MARKET_KEYWORD_SET
from utils.api_helpers import (
    gen_mkt_filter,
    gen_stock_filter,
    gather_article_set,
    initialize_logger
)

load_dotenv()
key = os.getenv("NYT_API_KEY")
if not key:
    raise ValueError("No API Key")

article_download_logger = initialize_logger("article_download_logger", level=logging.INFO)

final_data = []

for mkt_ks in tqdm(MARKET_KEYWORD_SET, desc="Market Keywords"):
    article_download_logger.info("%s Started", mkt_ks)

    try:
        df = gather_article_set(
            api_key= key,
            begin_date="2021-01-01",
            fq_generator_func=gen_mkt_filter,
            args= mkt_ks
        )
        final_data.append(df)
    except Exception as e:
        article_download_logger.error("Something wrong with Mkt Set %s", mkt_ks, exc_info=e)
        
    article_download_logger.info("%s Completed", mkt_ks)
        
    
for stock, ticker in tqdm(STOCK_SET, desc="Stocks"):
    article_download_logger.info("%s Started", stock)
    
    try:
        df = gather_article_set(
            api_key=key,
            begin_date="2021-01-01",
            fq_generator_func=gen_stock_filter,
            stock_name=stock,
            ticker=ticker
        )
        final_data.append(df)
    except Exception as e:
        article_download_logger.error("Something wrong with stock Set %s", (stock,ticker), exc_info=e)
        
    article_download_logger.info("%s Completed", stock)

final_df = pd.concat(final_data, ignore_index=True)
final_df.to_csv("data/raw_articles.csv")
