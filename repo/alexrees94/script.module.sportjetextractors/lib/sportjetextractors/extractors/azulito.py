import requests, re
from bs4 import BeautifulSoup

domain = ["jmutech.xyz", "fabtech.work"]
site_name = "Azulito"
short_id = "AZ"

def get_m3u8(url):
    r = requests.get(url).text
    m3u8 = re.findall(r"source src=\"(.+?)\"", r)[0]
    return m3u8 + "|Referer=" + url

def get_games():
    games = []
    r = requests.get("https://" + domain[0]).text
    soup = BeautifulSoup(r, "html.parser")
    for game in soup.select("li.g1-collection-item"):
        title = game.select_one("h3.entry-title").text
        href = game.select_one("a").get("href")
        icon = game.select_one("img").get("src")
        league = game.select_one("a.entry-category").text.replace(" Streams", "")
        games.append({
            "title": title,
            "links": [href],
            "icon": icon,
            "league": league,
            "time": ""
        })

    return games
