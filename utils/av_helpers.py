from utils.constants import ALPHA_VANTAGE_URL, ECONOMIC_FUNCTIONS
import pandas as pd
import os
import requests
from utils.other import initialize_logger
import logging

_get_economic_data_logger = initialize_logger("get_economic_data", logging.INFO)
def get_economic_data(func, api_key, **kwargs):

    if func not in ECONOMIC_FUNCTIONS:
        _get_economic_data_logger.error(f"Function {func} not supported")
        raise ValueError(f"function {func} not supported")
    for key in kwargs.keys():
        if key not in ('interval','maturity'):
            _get_economic_data_logger.error(f"kwarg {key} not accepted")
            raise ValueError(f"kwarg {key} not accepted")
    
    params = {
        'function': func,
        'apikey': api_key
    }
    params.update(kwargs)
    
    if 'maturity' in params:
        if func != 'TREASURY_YIELD':
            _get_economic_data_logger.warning(f"Maturity parameter provided for non-TREASURY_YIELD function, removing maturity")
            params.pop('maturity')
        else:
            maturities = ('3month', '2year', '5year', '7year', '10year', '30year')
            if params['maturity'] not in maturities:
                _get_economic_data_logger.error(f"Maturity has to be one of {maturities}")
                raise ValueError(f"Maturity has to be one of {maturities}")
    if 'interval' in params:
        if func in ('FEDERAL_FUNDS_RATE', 'TREASURY_YIELD'):
            intervals = ('daily', 'weekly', 'monthly')
        elif func == 'REAL_GDP':
            intervals = ('quarterly', 'annual')
        elif func == 'CPI':
            intervals = ('monthly', 'semiannual')
        else:
            _get_economic_data_logger.error(f"interval provided for a function that doesn't need it: {func}")
            raise RuntimeError(f"interval provided for a Economic Function that doesn't need it: {func}")
        if params['interval'] not in intervals:
            _get_economic_data_logger.error(f"Interval for {func} has to be one of {intervals}")
            raise ValueError(f"Interval for {func} has to be one of {intervals}")
        
    _get_economic_data_logger.info(f"Calling API: func={func}; kwargs={kwargs}")
    resp = requests.get(ALPHA_VANTAGE_URL, params=params)
    if resp.status_code == 200:
        _get_economic_data_logger.info(f"Successful Call")
        df = pd.json_normalize(
            data=resp.json(),
            record_path='data',
            meta= ['name','interval','unit']
            ).rename({'name': 'economic_indicator'},axis=1)
        df['value'] = df['value'].astype(float)
        df['date'] = pd.to_datetime(df.date)
        return df
    else:
        _get_economic_data_logger.error(f"HTTP Error: {resp.status_code}")
        raise requests.HTTPError(f"HTTP Error: {resp.status_code}")

    