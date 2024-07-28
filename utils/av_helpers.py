from constants import ALPHA_VANTAGE_URL, ECONOMIC_FUNCTIONS
import pandas as pd
import os
import requests
from other import initialize_logger


def get_economic_data(func, api_key, **kwargs):
    if func not in ECONOMIC_FUNCTIONS:
        raise ValueError(f"function {func} not supported")
    for key in kwargs.keys():
        if key not in ('interval','maturity'):
            raise ValueError(f"kwarg {key} not accepted")
    
    params = {
        'function': func,
        'apikey': api_key
    }
    params.update(kwargs)
    
    if 'maturity' in params:
        if func != 'TREASURY_YIELD':
            params.pop('maturity')
        else:
            maturities = ('3month', '2year', '5year', '7year', '10year', '30year')
            if params['maturity'] not in maturities:
                raise ValueError(f"Maturity has to be one of {maturities}")
    if 'interval' in params:
        if func in ('FEDERAL_FUNDS_RATE', 'TREASURY_YIELD'):
            intervals = ('daily', 'weekly', 'monthly')
        elif func == 'REAL_GDP':
            intervals = ('quarterly', 'annual')
        elif func == 'CPI':
            intervals = ('monthly', 'semiannual')
        else:
            raise RuntimeError(f"interval provided for a Economic Function that doesn't need it: {func}")
        if params['interval'] not in intervals:
            raise ValueError(f"Interval for {func} has to be one of {intervals}")

    resp = requests.get(ALPHA_VANTAGE_URL, params=params)
    if resp.status_code == 200:
        df = pd.json_normalize(
            data=resp.json(),
            record_path='data',
            meta= ['name','interval','unit']
            ).rename({'name': 'economic_indicator'},axis=1)
        return df
    else:
        raise requests.HTTPError(f"HTTP Error: {resp.status_code}")
