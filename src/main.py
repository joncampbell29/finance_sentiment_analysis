import requests
import os
from dotenv import load_dotenv
load_dotenv()
response = requests.get('https://httpbin.org/ip')
print(f'Your IP is {response.json()['origin']}')
print(os.getenv("TEST_APIKEY"))