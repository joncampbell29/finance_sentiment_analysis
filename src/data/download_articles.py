import requests
import os 
import logging
import time
from dotenv import load_dotenv
import pandas as pd
import sys
import os
from collections import namedtuple
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

import pandas as pd
hmm = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
print(hmm)
hmm.to_csv(path = "data/test.csv")