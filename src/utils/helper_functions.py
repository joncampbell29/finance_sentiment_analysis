import logging 
import requests 
from datetime import datetime
import time
from tqdm import tqdm
from math import ceil
from typing import List, Callable, Any
BASE_NYT_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
Fl_PARAM = 'lead_paragraph,snippet,abstract,pub_date,headline'


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
        logging.info("Request Made")
    except requests.RequestException as e:
        logging.error("Requests.get() Error: %s | Parameters: %s | Values: %s", e, 
                      list(parameters.keys()), 
                      list(parameters.values()))
        
    if resp.status_code == 200:
        logging.info("200 Status Code Success")
        resp_data = resp.json()
        num_hits = resp_data['response']['meta']['hits']
        
        if num_hits == 0:
            logging.debug("No hits")
            return []
        else:
            logging.info(f"Hits: {num_hits}")
        for art in resp_data['response']['docs']:
            if art['abstract'] == art['snippet']:
                art['snippet'] = ''
            art['headline'] = art['headline'].get('main')
        
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
        return res
    else:
        num_hits = res['num_hits']
        data = res['data']
    
    remaining_calls = ceil(num_hits / 10) - 1
    full_data = []
    if remaining_calls == 0:
        return {
            'data': data,
            'meta': meta
        }
    else:
        full_data.extend(data)
    
    for _ in tqdm(range(remaining_calls)):
        res = make_api_call(
            parameters=payload,
            key=api_key,
            fq_filter=filter_query,
            page=curr_page
            )
        curr_page += 1
        if isinstance(res, (str, list)):
            logging.WARNING("Stopped early due to error: %s", res)
            return full_data
        else:
            full_data.extend(res['data'])
        time.sleep(12)
    else:
        print("All Articles Returned")
        return full_data
        

    

