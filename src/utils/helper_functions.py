import logging 
import requests 
import time
from math import ceil
from typing import List, Callable, Any
BASE_NYT_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"


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


def make_api_call(parameters: dict, key: str, fq_filter: str, page: int) -> List[dict]:
    '''
    Makes a call to the NYT ArticleSearch API Endpoit
    
    Args:
        parameters: pass
        
        key: Valid NYT API key
        
        fq_filter: Properly formatted fq parameter used in the API call
        
        page: The page for the API call (Calls return a max of 10 articles per page)

    Returns:
        A dictionary with the article data in list format (a list of dictionaries representing 
        Articles with headline, snippet, lead paragraph, publication date) and the total number of hits
    '''
    
    parameters['fq'] = fq_filter
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
    fq_generator_func: Callable,
    **kwargs: Any
): 
    '''
        Makes multiple calls to the NYT API provided a singe filter to get all the articles 
        the have from that filter
    
    Args:
        api_key: NYT API key
        
        fq_generator_func: Either gen_mkt_filter or gen_stock_filter
        
        **kwargs: arguments to go in the provided function. If gen_mkt_filter should be in the format
        kwargs = (keyword1, keyword2,...). If gen_stock_filter, stock_name and ticker should be 
        provided: For example stock_name = "Apple", ticker = "AAPL"

    Returns:
        Pass
    
    '''
    if fq_generator_func.__name__ == 'gen_mkt_filter':
        args = kwargs.values()
        filter_query = fq_generator_func(*args)
    elif fq_generator_func.__name__ == 'gen_stock_filter':
        filter_query = fq_generator_func(**kwargs)
    else:
        raise ValueError("Neither gen_mkt_filter nor gen_stock_filter was provided")
    
    

