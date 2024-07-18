# import requests
# import os
# from dotenv import load_dotenv
# load_dotenv()
# response = requests.get('https://httpbin.org/ip')
# print(f'Your IP is {response.json()['origin']}')
# print(os.getenv("TEST_APIKEY"))
from utils.api_helpers import gen_mkt_filter
from utils.constants import STOCK_SET
print(STOCK_SET)
print(gen_mkt_filter)
# import sys
# for i in sys.path:
#     print(i)