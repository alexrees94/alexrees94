import requests, re
from bs4 import BeautifulSoup
from dateutil.parser import parse
from datetime import timedelta
from unidecode import unidecode
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
domain = ["a.crackstreams.net", "crackstreams.net", "nflstreams.link"]
site_name = "Crackstreams"
short_id = "CS"

def get_m3u8(url):
    request = requests.Session()
    request.cookies.set("challenge", "BitMitigate.com", domain="crackstreams.net", path="/")
    m3u8 = ""
    try:
        video_html = request.get(url).text
        video = BeautifulSoup(video_html, "html.parser")
        stream_url = video.find_all("iframe")[0].get("src")
        stream_html = requests.get(stream_url, headers={"Referer": url}).text
        soup_stream = BeautifulSoup(stream_html, "html.parser")
        if len(soup_stream.find_all("iframe")) > 0:
            iframe = soup_stream.find("iframe").get("src")
            r_iframe = requests.get(iframe).text
            m3u8 = re.compile(r"source: '(.+?)'").findall(r_iframe)[0]
        elif "Clappr.Player" in stream_html:
            m3u8 = re.compile(r'source: "(.+?)"').findall(stream_html)[0]        

        if "hdstreamss" in m3u8:
            m3u8 = m3u8 + "|Referer=http://hdstreamss.club/"
        return m3u8
    except:
        raise "no link found"

def get_games():
    games = []
    base_url = "http://a.crackstreams.net"
    request = requests.Session()
    request.cookies.set("challenge", "BitMitigate.com", domain="crackstreams.net", path="/")
    r = request.get(base_url).text
    soup = BeautifulSoup(r, "html.parser")
    categories = soup.select("ul.nav > li > a")
    for category in categories:
        league = category.text.replace(" streams", "")
        league_href = base_url + category.get("href")
        r_league = request.get(league_href).text
        soup_league = BeautifulSoup(r_league, "html.parser")
        for body in soup_league.find_all("a", {"class": "btn-block"}):
            href = base_url + body.get("href") if body.get("href").startswith("/") else body.get("href")
            icon = "-"
            title = body.find("h4").text.strip()
            time = body.find("p").text
            if "Stream" in time:
                continue
            utc_time = ""
            if time != "":
                try:
                    utc_time = parse(time) + timedelta(hours=4)
                except:
                    pass
            games.append({
                "title": unidecode(title),
                "links": [
                    href
                ],
                "icon": unidecode(icon),
                "league": league,
                "time": utc_time
            })
    return games
