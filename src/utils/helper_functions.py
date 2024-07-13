import logging 
import requests 
from datetime import datetime
import pandas as pd
import time
from tqdm import tqdm
from math import ceil
from typing import List, Callable, Any
import os



def initialize_logger():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(current_dir, 'test_func.log')
    logging.basicConfig(
        level=logging.INFO,
        filename=log_file,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger(__name__)
    return logger

logger = initialize_logger()


def test_func(a,b):
    logger.info(f"first num is {a}")
    logger.info(f"second num is {b}")
    if a < 0:
        logger.warning(f"{a} is negative")
    if b < 0:
        logger.warning(f"{b} is negative")
    if a + b == 0:
        logger.error("sums to 0")
        raise ValueError("sums to 0")
    return a + b

BASE_NYT_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
Fl_PARAM = 'lead_paragraph,snippet,abstract,pub_date,headline,web_url,source'
MARKET_KEYWORD_SET = (
    ("earnings", "revenue", "profits", "growth", "sales", "market share", "financial results"),
    ("economic outlook", "GDP", "inflation", "interest rates", "Federal Reserve", "monetary policy"),
    ("fiscal policy", "unemployment", "labor market", "consumer spending", "technology sector"),
    ("healthcare sector", "energy sector", "financial sector", "industrial sector", "consumer goods"),
    ("retail sales", "global trade", "supply chain", "corporate earnings", "stock buybacks"),
    ("dividends", "market volatility", "investor sentiment", "mergers and acquisitions"),
    ("regulatory changes", "geopolitical", "climate change", "sustainability"),
    ("corporate governance", "cybersecurity", "innovation", "market competition")
)
STOCK_SET = (
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

def gen_stock_filter(stock_name: str, ticker: str) -> str:
    '''
    Generates a NYT Compatible fq parameter string from a stock name and its ticker
    
    Args:
        stock_name: String name of a stock
        
        ticker: The ticker associated with the stock name. Does not need to be the ticker for 
        
        the stock_name, but that is preferred

    Returns:
        A string combining all conditions with ' AND '.
    '''
    return f'(headline:("{stock_name}") AND body:("{stock_name}")) OR (body:("{ticker}"))'

def gen_mkt_filter(*args: str) -> str:
    '''
    Generates a NYT Compatible fq parameter string from a list or tuple of general market keywords 
    
    Args:
        *args: A variable number of string arguments representing market conditions.

    Returns:
        A string combining all conditions with ' OR ' plus the news_desk parameter from NYT API.
    '''
    
    filts = [f'(headline:("{arg}") AND body:("{arg}"))' for arg in args]
    return " OR ".join(filts) + ' AND news_desk:("Business", "Financial")'


def make_api_call(parameters: dict, key: str, fq_filter: str, page: int = None) -> List[dict]:
    '''
    Makes a call to the NYT ArticleSearch API Endpoit
    
    Args:
        parameters: Query params to pass to API Call. Can be empty
        
        key: Valid NYT API key
        
        fq_filter: Properly formatted fq parameter used in the API call
        
        page: The page for the API call (Calls return a max of 10 articles per page)

    Returns:
        A dictionary with the article data in list format (a list of dictionaries representing 
        Articles with headline, snippet, lead paragraph, publication date) and the total number of hits
    '''
    
    parameters['api-key'] = key
    parameters['fq'] = fq_filter
    if page:
        parameters['page'] = page

    try:
        resp = requests.get(BASE_NYT_URL, params=parameters)
        logger.info(f"Request made with status code {resp.status_code}")
    except requests.RequestException as e:
        logger.error("Requests.get() Error: %s | Parameters: %s | Values: %s", e, 
                      list(parameters.keys()), 
                      list(parameters.values()))
        
    if resp.status_code == 200:
        logger.info("200 Status Code Success")
        resp_data = resp.json()
        num_hits = resp_data['response']['meta']['hits']
        
        if num_hits == 0:
            logger.debug("No hits")
            return []
        else:
            logger.info(f"Hits: {num_hits}")
        for art in resp_data['response']['docs']:
            if art['abstract'] == art['snippet']:
                art['snippet'] = ''
            art['headline'] = art['headline'].get('main')
            art['pub_date'] = datetime.fromisoformat(art['pub_date'])
        
        # time.sleep()
        return {
            'num_hits': num_hits,
            'data': resp_data['response']['docs']
        }
    else:
        return f"Status Code: {resp.status_code}"
    
    
def gather_article_set(
    api_key: str,
    begin_date: str,
    fq_generator_func: Callable,
    end_date: str = None,
    **kwargs: Any,
    
): 
    '''
        Makes multiple calls to the NYT API provided a singe filter to get all the articles 
        the have from that filter
    
    Args:
        api_key: NYT API key
        
        begin_date: Date in the format YYYY-MM-DD
        
        fq_generator_func: Either gen_mkt_filter or gen_stock_filter
        
        **kwargs: arguments to go in the provided function. If gen_mkt_filter should be in the format
        keywords = (keyword1, keyword2,...). If gen_stock_filter, stock_name and ticker should be 
        provided: For example stock_name = "Apple", ticker = "AAPL"

    Returns:
        Pass
    
    '''
    if fq_generator_func.__name__ == 'gen_mkt_filter':
        args = kwargs.values()
        args = [k for k in kwargs.values()]
        if len(args) == 1:
            args = args[0]
        else:
            raise ValueError("Kwargs input for gen_mkt_filter in wrong format")
        filter_query = fq_generator_func(*args)
        meta = {
            'article_type': 'general_mkt',
            'arguments': args
        }
    elif fq_generator_func.__name__ == 'gen_stock_filter':
        filter_query = fq_generator_func(**kwargs)
        meta = {
            'article_type': 'stock',
            'arguments': tuple(kwargs.values())
        }
    else:
        raise ValueError("Neither gen_mkt_filter nor gen_stock_filter was provided")

    try:
        datetime.strptime(begin_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("begin_date not in YYYY-mm-dd format")
    
    payload = {
        'begin_date': begin_date,
        'api-key': api_key,
        'fl': Fl_PARAM,
    }
    if end_date:
        payload['end_date'] = end_date
    
    curr_page = 0
    res = make_api_call(
        parameters=payload,
        key=api_key,
        fq_filter=filter_query,
        page=curr_page
        )
    curr_page += 1
    if isinstance(res, (str, list)):
        return pd.json_normalize([])
    else:
        num_hits = res['num_hits']
        data = res['data']
    
    remaining_calls = ceil(num_hits / 10) - 1
    full_data = []
    if remaining_calls == 0:
        if len(full_data) != 0:
            for art in full_data:
                art['meta'] = meta
        else:
            return pd.json_normalize([])
        return pd.json_normalize(full_data)
    else:
        full_data.extend(data)
    
    for _ in tqdm(range(remaining_calls), desc = "Processing Articles", unit= "page"):
        res = make_api_call(
            parameters=payload,
            key=api_key,
            fq_filter=filter_query,
            page=curr_page
            )
        curr_page += 1
        if isinstance(res, (str, list)):
            logger.warning("Stopped early due to error: %s", res)
            print(res)
            if len(full_data) != 0:
                for art in full_data:
                    art['meta'] = meta
                return pd.json_normalize(full_data)
            else:
                return pd.json_normalize([])
        # return pd.json_normalize(full_data)
        else:
            full_data.extend(res['data'])
        time.sleep(15)
    else:
        print("All Articles Returned")
    
    if len(full_data) != 0:
        for art in full_data:
            art['meta'] = meta
    return pd.json_normalize(full_data)
        

    

