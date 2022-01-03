import re, requests, math, json
from random import random
from bs4 import BeautifulSoup
import dateutil
domain = ["topstreams.info"]
site_name = "Topstreams"
short_id = "TS"

def get_m3u8(url):
    page_data = requests.get(url).text
    server = re.findall(r'-1\';\s*var server=\'([^\']*)', page_data)[0]
    key = get_key(page_data)
    return "http://%s/%s.m8" % (server, key)

def get_key(page_data):
    alledges = json.loads(re.compile(r"var alledges=({.+?});").findall(page_data)[0])
    edges = {}
    for vkey in alledges:
        if vkey != "primary" and int(alledges[vkey]) < 1000:
            edges[vkey] = alledges[vkey]

    if len(edges.keys()) == 0:
        for vkey in alledges:
            if vkey != "primary":
                edges[vkey] = alledges[vkey]

    edgeslength = len(edges.keys()) - 1
    randomIndex = int(math.floor(random() * edgeslength))
    key = list(edges.keys())[randomIndex]
    return key

def get_games():
    games = []
    base_url = "http://topstreams.info"
    r_home = requests.get(base_url).text
    soup_home = BeautifulSoup(r_home, "html.parser")
    for game in soup_home.select("div.item.upcoming"):
        try:
            title = game.select_one("div.home div.name").get_text() + " vs. " + game.select_one("div.away div.name").get_text()
            icon = game.select_one("div.away img.teamlogo").get("src")
            time = dateutil.parser.parse(re.compile(r"moment\('(.+?)'\)").findall(str(game))[0])
            href = game.select_one("div.list a.item").get("href")
            games.append({
                "title": title,
                "links": [href],
                "icon": icon,
                "league": "",
                "time": time
            })
        except:
            continue
    return games