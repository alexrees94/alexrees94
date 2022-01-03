import re, requests, time
from .plytv_sdembed import plytv_sdembed
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from ..icons import icons

domain = ["buffstreams.tv"]
site_name = "Buffstreams"
short_id = "BUFF"

def get_zmid(url):
    r_game = requests.get(url).text
    zmid = re.compile(r'zmid = "(.+?)"').findall(r_game)[0]
    return zmid

def get_m3u8(url):
    r = requests.get(url).text
    if "zmid" in r:
        zmid = re.compile(r'zmid = "(.+?)"').findall(r)[0]
        url = plytv_sdembed(zmid, url)
    else:
        v_vpp = re.compile(r'v_vpp="(.+?)"').findall(r)[0]
        v_vid = re.compile(r'v_vid="(.+?)"').findall(r)[0]
        v_vpv = re.compile(r'v_vpv="(.+?)"').findall(r)[0]
        url = plytv_sdembed("https://www.tvply.me/hdembed?p=%s&id=%s&v=%s" % (v_vpp, v_vid, v_vpv), url)
    return url

def get_games():
    games = []
    base_url = "https://buffstreams.tv"
    r_home = requests.get(base_url).text
    soup_home = BeautifulSoup(r_home, "html.parser")
    for button in soup_home.find_all("div", {"class": "col-lg-3"}):
        href = base_url + button.find("a").get("href")
        category = href.replace("https://buffstreams.tv/watch-", "")
        r_category = requests.get(href).text
        soup_category = BeautifulSoup(r_category, "html.parser")
        for game in soup_category.find_all("a", {"class": "card"}):
            try:
                game_href = base_url + game.get("href")
                title = game.find_all("span")[-1].text
                game_time = datetime(*(time.strptime(game.find_all("span")[-2].get("content"), "%Y-%m-%dT%H:%M")[:6])) if game.find_all("span")[-2].get("content") != None else ""
                league = category
                games.append({
                    "title": title,
                    "links": [game_href],
                    "icon": icons[league.lower()],
                    "league": league.capitalize(),
                    "time": game_time
                })
            except Exception as e:
                continue
    return games