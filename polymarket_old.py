import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
import json

def get_polymarket_odds():
    url = 'https://polymarket.com/event/presidential-election-winner-2024'

    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get(url, headers=header)
    soup = BeautifulSoup(r.text, "html.parser")
    section = soup.find(id="__NEXT_DATA__").contents
    data = json.loads(section[0])['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['markets'][0]['outcomePrices']
    trump = float(data[0])*100
    harris = float(data[1])*100

    if trump > harris:
        colour = ':red_circle:'
    elif trump == harris:
        colour = ':white_circle:'
    else:
        colour = ':blue_circle'
    line = f"{colour} Trump: {trump:.2f}, Harris: {harris:.2f}"
    return line

if __name__ == "__main__":
    get_polymarket_odds()