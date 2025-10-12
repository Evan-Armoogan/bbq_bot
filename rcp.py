import requests
import pandas as pd
from io import StringIO

state_to_key = {
    "National": 0,
    "Wisconsin": 1,
    "Pennsylvania": 2,
    "Ohio": 3,
    "Michigan": 4,
    "Arizona": 5,
    "Nevada": 6,
    "North Carolina": 7,
    "Georgia": 8,
    "Florida": 9
}

def get_state_poll(state_name, table):
    return table.loc[state_to_key[state_name.lower().title()]]

def get_rcp_avgs():
    url = 'https://www.realclearpolling.com/polls/president/general/2024/trump-vs-harris'

    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get(url, headers=header)
    table = pd.read_html(StringIO(r.text))[2]

    swing = ['National', 'Arizona', 'Nevada', 'Wisconsin', 'Michigan', 'Pennsylvania', 'North Carolina', 'Georgia']
    return_str = ""
    for state in swing:
        spread = get_state_poll(state, table).iloc[1]
        colour = None
        if 'Trump' in spread:
            colour = ':red_circle:'
        elif 'Tie' in spread:
            colour = ':white_circle:'
        else:
            colour = ':blue_circle:'
        line = f'{colour} {state}: {spread}\n'
        return_str += line
    
    return_str = return_str[:-1] # remove extra endline
    
    return return_str

if __name__ == "__main__":
    print(get_rcp_avgs())
