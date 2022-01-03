import requests, re
from bs4 import BeautifulSoup
from unidecode import unidecode

domain = ["ustvgo.tv"]
site_name = "USTVGO"
short_id = "USTVGO"

def get_m3u8(url):
    r = requests.get(url).text
    channel_id = re.compile(r"\?stream=(.+?)'").findall(r)[0]
    m3u8 = requests.post("https://ustvgo.tv/data.php", data={"stream": channel_id}).text
    return m3u8

def get_games():
    import xbmc
    games = []
    r = requests.get("https://ustvgo.tv/").text
    soup = BeautifulSoup(r, "html.parser")
    channels = soup.select("ol > li")
    for channel in channels:
        link = channel.select_one("a")
        games.append({
            "title": unidecode(link.text),
            "links": [link.get("href")],
            "icon": "",
            "league": "",
            "time": "",
        })
    return games