#fetch gif
import requests
import json
import random

lmt = 10

RandomURL = "https://api.tenor.com/v1/random?&key=%s&limit=%s"
SearchURL = "https://api.tenor.com/v1/search?key=%s&limit=%s&q=%s"

def fetch_tenor(keyword, TENOR_API_KEY):
    if(keyword == 'random'):
        r = requests.get( RandomURL % ( TENOR_API_KEY, lmt ) )
    else:
        r = requests.get( SearchURL % ( TENOR_API_KEY, lmt, keyword))
    if r.status_code == 200:
        top_10_gif = json.loads(r.content)
        try:
            return random.choice(top_10_gif['results'])['url']
        except IndexError:
            return "Sorry, No results"

    else:
        return None
