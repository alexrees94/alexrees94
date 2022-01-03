import requests
from ..util.keys import Keys

domain = ["api.locastnet.org"]
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"

def get_m3u8(url):
    key = Keys.get_key(Keys.locast)
    r = requests.get(url, headers={"Authorization": "Bearer " + key, "User-Agent": user_agent}).json()
    return r["streamUrl"]