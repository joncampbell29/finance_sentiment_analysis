import logging 
import requests 
from datetime import datetime
import pandas as pd
import time
from tqdm import tqdm
from math import ceil
from typing import List, Callable, Any
import os
from pathlib import Path
from utils.constants import STOCK_SET, MARKET_KEYWORD_SET, Fl_PARAM, BASE_NYT_URL

def get_project_root() -> Path:
    """Gets Project base path to easily traverse project tree"""
    return Path(__file__).parent.parent

class TooManyRequestsException(Exception):
    """Exception raised for Too Many Requests (HTTP 429)."""
    pass

class MakeAPIRequestReturnException(Exception):
    '''Make Api Request not returning what it should'''
    pass

def initialize_logger(func_file_name: str, level: int) -> logging.Logger:
    '''
    Creates a logger for a function. For use at module level only, not outside
    '''
    os.makedirs("logs", exist_ok=True)
    log_file = f'logs/{func_file_name}.log'
    
    logger = logging.getLogger(func_file_name)
    handler = logging.FileHandler(log_file)
    date_format = '%Y-%m-%d %I:%M:%S %p'
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt=date_format)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


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


def check_date_format(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("begin_date not in YYYY-mm-dd format")
    return None


_api_call_logger = initialize_logger("make_api_call", logging.WARNING)
def make_api_call(parameters: dict, key: str, fq_filter: str, page: int = None, time_delay=False) -> List[dict]:
    '''
    Makes a call to the NYT ArticleSearch API Endpoint. pub_date, snippet, abstract,and headline requeired in f1 parameter
    
    Args:
        parameters: Query params to pass to API Call. Can be empty
        
        key: Valid NYT API key
        
        fq_filter: Properly formatted fq parameter used in the API call
        
        page: The page for the API call (Calls return a max of 10 articles per page)

    Returns:
        A dictionary with the article data in list format (a list of dictionaries representing 
        Articles with headline, snippet, lead paragraph, publication date) and the total number of hits
    '''
    if key:
        parameters['api-key'] = key
    else:
        raise ValueError("Need API Key")
    if fq_filter:
        parameters['fq'] = fq_filter
    if page:
        try:
            parameters['page'] = int(page)
        except Exception as e:
            raise ValueError(f"{e}: page parameter problem")

    if "begin_date" in parameters:
        check_date_format(parameters["begin_date"])
    if "end_date" in parameters:
        check_date_format(parameters["end_date"])
    
    try:
        resp = requests.get(BASE_NYT_URL, params=parameters)
        _api_call_logger.info(f"Request made with status code {resp.status_code}")
    except Exception as e:
        _api_call_logger.error("Requests.get() Error: %s | Parameters: %s | Values: %s", e, 
                      list(parameters.keys()), 
                      list(parameters.values()))
        
        
    if resp.status_code == 200:
        
        resp_data = resp.json()
        num_hits = resp_data['response']['meta']['hits']
        _api_call_logger.info("Status Code 200 | Hits %s", num_hits)
        if num_hits == 0:
            _api_call_logger.warning("No hits")
            if time_delay:
                time.sleep(15)
            return {
                'num_hits': num_hits,
                'data': [],
                'meta': {'status_code': resp.status_code}
            }
        else:
            _api_call_logger.info(f"Hits: {num_hits}")
        for art in resp_data['response']['docs']:
            if art['abstract'] == art['snippet']:
                art['snippet'] = ''
            art['headline'] = art['headline'].get('main')
            art['pub_date'] = datetime.fromisoformat(art['pub_date'])
        
        if time_delay:
            time.sleep(15)
        return {
            'num_hits': num_hits,
            'data': resp_data['response']['docs'],
            'meta': {'status_code': resp.status_code}
        }
    elif resp.status_code == 401:
        raise ValueError("Unauthorized: Check API Key")
    elif resp.status_code == 429:
        _api_call_logger.fatal("Too Many Requests")
        raise TooManyRequestsException("Status Code 429: Too Many Requests")
    
_article_set_logger = initialize_logger("gather_article_set", logging.INFO)
def gather_article_set(
    api_key: str,
    begin_date: str,
    fq_generator_func: Callable,
    end_date: str = None,
    **kwargs: Any
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

    _article_set_logger.info("Params - Article Type %s | Arguments %s", 
                        meta['article_type'],
                        meta['arguments'])
    
    check_date_format(begin_date)
    
    payload = {
        'begin_date': begin_date,
        'api-key': api_key,
        'fl': Fl_PARAM,
    }
    if end_date:
        check_date_format(end_date)
        payload['end_date'] = end_date
    
    curr_page = 0
    res = make_api_call(
        parameters=payload,
        key=api_key,
        fq_filter=filter_query,
        page=curr_page
        )
    curr_page += 1
    if not isinstance(res, dict):
        _article_set_logger.fatal("First Request Problem: %s", res,exc_info=True)
        raise MakeAPIRequestReturnException
    else:
        num_hits = res['num_hits']
        data = res['data']
    
    remaining_calls = ceil(num_hits / 10) - 1
    _article_set_logger.info("%s more requests", remaining_calls)
    full_data = []
    if remaining_calls == 0:
        if len(data) != 0:
            for art in data:
                art['meta'] = meta
        else:
            _article_set_logger.warning("No Data Returned")
            return pd.json_normalize([])

        return pd.json_normalize(data)
    else:
        full_data.extend(data)
    
    for i in tqdm(range(remaining_calls), desc = "Processing Articles", unit= "page"):
        res = make_api_call(
            parameters=payload,
            key=api_key,
            fq_filter=filter_query,
            page=curr_page
            )
        curr_page += 1
        if not isinstance(res, dict):
            _article_set_logger.warning("%s Request Problem: %s",i, res,exc_info=True)

            if len(full_data) != 0:
                for art in full_data:
                    art['meta'] = meta
                return pd.json_normalize(full_data)
            else:
                return pd.json_normalize([])
        
        else:
            full_data.extend(res['data'])
        time.sleep(15)
    else:
        _article_set_logger.info("All Articles Returned: %s requests made",remaining_calls+1)
    
    if len(full_data) != 0:
        for art in full_data:
            art['meta'] = meta
    return pd.json_normalize(full_data)

        

    

