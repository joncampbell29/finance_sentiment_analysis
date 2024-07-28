from utils.constants import ALPHA_VANTAGE_URL, ECONOMIC_FUNCTIONS
import pandas as pd
import os
import requests
from utils.other import initialize_logger
import logging

logging.basicConfig(level=logging.INFO, filename='economic_data.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

def get_economic_data(func, api_key, **kwargs):
    #Log the function entry parameters 
    logging.info(f"get_economic_data called with func={func},api_key={api_key}, kwargs={kwargs}")
    
    if func not in ECONOMIC_FUNCTIONS:
        logging.error(f"Function {func} not supported")
        raise ValueError(f"function {func} not supported")
    for key in kwargs.keys():
        if key not in ('interval','maturity'):
            logging.error(f"kwarg {key} not accepted")
            raise ValueError(f"kwarg {key} not accepted")
    
    params = {
        'function': func,
        'apikey': api_key
    }
    
    # Log the updated parameters
    logging.info(f"Parameters for API request: {params}")
    
    params.update(kwargs)
    
    if 'maturity' in params:
        if func != 'TREASURY_YIELD':
            logging.warning(f"Maturity parameter provided for non-TREASURY_YIELD function, removing maturity")
            params.pop('maturity')
        else:
            maturities = ('3month', '2year', '5year', '7year', '10year', '30year')
            if params['maturity'] not in maturities:
                logging.error(f"Maturity has to be one of {maturities}")
                raise ValueError(f"Maturity has to be one of {maturities}")
    if 'interval' in params:
        if func in ('FEDERAL_FUNDS_RATE', 'TREASURY_YIELD'):
            intervals = ('daily', 'weekly', 'monthly')
        elif func == 'REAL_GDP':
            intervals = ('quarterly', 'annual')
        elif func == 'CPI':
            intervals = ('monthly', 'semiannual')
        else:
            logging.error(f"interval provided for a function that doesn't need it: {func}")
            raise RuntimeError(f"interval provided for a Economic Function that doesn't need it: {func}")
        if params['interval'] not in intervals:
            logging.error(f"Interval for {func} has to be one of {intervals}")
            raise ValueError(f"Interval for {func} has to be one of {intervals}")   

    resp = requests.get(ALPHA_VANTAGE_URL, params=params)
    if resp.status_code == 200:
        df = pd.json_normalize(
            data=resp.json(),
            record_path='data',
            meta= ['name','interval','unit']
            ).rename({'name': 'economic_indicator'},axis=1)
        df['value'] = df['value'].astype(float)
        df['date'] = pd.to_datetime(df.date)
        return df
    else:
        raise requests.HTTPError(f"HTTP Error: {resp.status_code}")

# Log before making the API request
    logging.info(f"Making API request to {ALPHA_VANTAGE_URL} with params: {params}")
    