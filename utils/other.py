
from datetime import datetime
import os
from pathlib import Path
import logging

def get_project_root() -> Path:
    """Gets Project base path to easily traverse project tree"""
    return Path(__file__).parent.parent

def check_date_format(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("begin_date not in YYYY-mm-dd format")
    return None

def convert_date_av_format(date: str):
    check_date_format(date)
    dt = datetime.strptime(date,"%Y-%m-%d")
    return dt.strftime('%Y%m%dT%H%M')

def convert_from_datetime(datetime_obj):
    """Convert Datetime object to format YYYY-MM-DD"""
    if isinstance(datetime_obj, datetime):
        month = datetime_obj.month if int(datetime_obj.month) > 10 else f"0{datetime_obj.month}"
        day = datetime_obj.day if int(datetime_obj.day) > 10 else f"0{datetime_obj.day}"
        return f"{datetime_obj.year}-{month}-{day}"
    else:
        raise ValueError(f"Only type datetime accepted. type {type(datetime_obj)} supplied")
    
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