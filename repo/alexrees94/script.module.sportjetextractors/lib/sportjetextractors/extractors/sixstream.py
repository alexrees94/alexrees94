import requests, re, dateutil.parser
from bs4 import BeautifulSoup
from datetime import timedelta
from unidecode import unidecode

user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
domain = ["6stream.xyz", "markkystreams.com", "6streams.tv"]
base_url = "http://6stream.xyz/"
site_name = "6stream"
short_id = "6S"
use_ffmpeg = True

def get_m3u8(url):
    r = requests.get(url).text
    m3u8 = re.compile(r'source: "(.+?)"').findall(r)[0] + "|Referer=%s&User-Agent=%s" % (url, user_agent)
    return m3u8

def get_games():
    games = []
    r = requests.get(base_url).text
    soup = BeautifulSoup(r, "html.parser")
    categories = soup.select("ul.nav > li.menu-item > a")
    categories = categories[:int(len(categories) / 2)] # Remove bottom nav buttons
    for category in categories:
        try:
            if "Streams" not in category.text:
                continue
            league = category.text.replace(" Streams", "")
            href = category.get("href")
            r_league = requests.get(href).text
            soup_league = BeautifulSoup(r_league, "html.parser")
            for game in soup_league.find_all("figure"):
                try:
                    icon = game.get("data-original")
                    sibling = game.next_sibling
                    title = sibling.select_one("h2.entry-title > a").get("title")
                    game_href = game.find("a").get("href")
                    utc_time = ""
                    if title.lower().endswith("et"): # this is dumb
                        time = " ".join(title.split(" ")[::-1][:3][::-1])
                        utc_time = dateutil.parser.parse(time.upper()) + timedelta(hours=4)
                        title = title.replace(time, "").strip()

                    games.append({
                        "title": unidecode(title),
                        "links": [game_href],
                        "icon": unidecode(icon),
                        "league": league,
                        "time": utc_time
                    })
                except:
                    continue
        except:
            continue
    return games