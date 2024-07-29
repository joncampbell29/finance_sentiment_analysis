import logging
from dotenv import load_dotenv
import pandas as pd
import os
import sqlite3
from datetime import datetime, timedelta
from tqdm import tqdm
from utils.constants import BASE_NYT_URL, MARKET_KEYWORD_SET, BASE_BEGIN_DATE
from utils.nyt_api_helpers import (
    gen_mkt_filter,
    gather_article_set,
    initialize_logger
)
from utils.feature_helpers import combine_text_args_df, gen_full_text_df, clean_df

load_dotenv()
key = os.getenv("NYT_API_KEY")
if not key:
    raise ValueError("No API Key")

mkt_download_logger = initialize_logger("mkt_download_logger", level=logging.INFO)

final_data = []

db_path = os.path.join(os.path.dirname(os.getcwd()), 'data/test.db')
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS NYT_Artiles (
    id INTEGER PRIMARY KEY,
    pub_date TEXT,
    full_text TEXT,
    combined_text TEXT,
    source REAL,
    web_url TEXT
)
""")
con.commit()

cur.execute('SELECT max(id), max(pub_date) FROM NYT_Articles')
max_id, max_date = cur.fetchone()




for mkt_ks in tqdm(MARKET_KEYWORD_SET, desc="Market Keywords"):
    mkt_download_logger.info("%s Started", mkt_ks)

    try:
        df = gather_article_set(
            api_key= key,
            begin_date=BASE_BEGIN_DATE,
            fq_generator_func=gen_mkt_filter,
            args=mkt_ks
        )
        final_data.append(df)
    except Exception as e:
        mkt_download_logger.error("Something wrong with Mkt Set %s", mkt_ks, exc_info=e)
        
    mkt_download_logger.info("%s Completed", mkt_ks)

final_df = pd.concat(final_data, ignore_index=True)
final_df = combine_text_args_df(gen_full_text_df(clean_df(final_df)), keep_all_cols=False)
# final_df.to_csv("data/nyt/raw/raw_mkt_articles.csv")
