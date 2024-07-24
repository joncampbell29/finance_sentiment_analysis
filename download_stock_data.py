import logging
from dotenv import load_dotenv
import pandas as pd
import os
from tqdm import tqdm
from utils.constants import BASE_NYT_URL, STOCK_SET, BASE_BEGIN_DATE
from utils.nyt_api_helpers import (
    gen_stock_filter,
    gather_article_set,
    initialize_logger
)
from utils.feature_helpers import combine_text_args_df, gen_full_text_df, clean_df

load_dotenv()
key = os.getenv("NYT_API_KEY")
if not key:
    raise ValueError("No API Key")

stock_download_logger = initialize_logger("stock_download_logger", level=logging.INFO)

final_data = []
    
for stock, ticker in tqdm(STOCK_SET, desc="Stocks"):
    stock_download_logger.info("%s Started", stock)
    try:
        df = gather_article_set(
            api_key=key,
            begin_date=BASE_BEGIN_DATE,
            fq_generator_func=gen_stock_filter,
            stock_name=stock,
            ticker=ticker
        )
        final_data.append(df)
    except Exception as e:
        stock_download_logger.error("Something wrong with Stock Set %s", (stock,ticker), exc_info=e)
        
    stock_download_logger.info("%s Completed", stock)

final_df = pd.concat(final_data, ignore_index=True)
final_df = combine_text_args_df(gen_full_text_df(clean_df(final_df)), keep_all_cols=False)
# final_df.to_csv("data/nyt/raw/raw_stock_articles.csv")