import requests, re, time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from ..scanners import m3u8_src
from . import sling, telerium

domain = ["freefeds.com"]
site_name = "Freefeds"
short_id = "FF"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"

def get_games():
    games = []
    r = requests.get("https://freefeds.com").text
    soup = BeautifulSoup(r, "html.parser")
    for tab in soup.select("div"):
        if "id" not in tab.attrs or not tab.attrs["id"].startswith("tab"): continue
        sport = tab.select_one("h3").text.replace(" schedule", "")
        date = datetime.now()
        date_ahead = date + timedelta(days=2)
        for child in tab.contents:
            if child == "\n": continue
            elif child.name == "h3":
                if child.text.endswith("schedule"): continue
                else: 
                    date = datetime(*(time.strptime(child.text, "%A, %B %d, %Y")[:6]))
            elif child.name == "div":
                title = child.select_one("h4").text.strip()
                title_split = title.split(" - ")
                time_split = title_split[0].split(":")
                game_time = date.replace(hour=int(time_split[0]), minute=int(time_split[1])) + timedelta(hours=4)
                if game_time > date_ahead: continue
                game_title = title_split[1].replace("'", "").replace('"', "")
                league = title_split[2]
                links = []
                for link in child.select("input.sm"):
                    if link.attrs["value"].startswith("http") and "/video/" not in link.attrs["value"]: links.append(link.attrs["value"])
                games.append({
                    "title": game_title,
                    "links": links,
                    "icon": "",
                    "league": "%s/%s" % (sport, league),
                    "time": game_time
                })
    return games

def get_m3u8(url):
    r = requests.get(url, headers={"User-Agent": user_agent, "Referer": "https://" + domain[0]}).text
    scan = m3u8_src.scan_page(url, r)
    if scan: return scan
    if "chNo=" in r:
        r_chno = re.findall(r"chNo=(.+?);", r)[0]
        r_sling = requests.get("https://cbd46b77.cdn.cms.movetv.com/cms/publish3/domain/summary/ums/1.json", headers={"User-Agent": user_agent}).json()
        mpd_url, license_url, _, start_time = sling.get_playlist(r_sling["channels"][1]["qvt_url"])
        mpd_url = mpd_url.replace(re.findall(r"(clipslist\/.+?)\/", mpd_url)[0], "clipslist/" + r_chno)
        return "inputstream://%s===%s===%s" % (mpd_url, license_url, str(start_time))
    if ".mpd?" in r:
        src = re.findall(r"var src = \"(.+?)\";", r)[0]
        payload = '{"channel_id": "6f6788bea06243da873b8b3450b4aaa0", "env": "production", "message": [D{SSM}], "user_id": "fcdda172-0060-11eb-b722-0a599a2ac821"}'
        license_key = '%s|Content-Type=text/plain&User-Agent=%s|%s|' % ("https://p-drmwv.movetv.com/widevine/proxy", USER_AGENT, quote(payload))
        return f"inputstream://{src}==="
    if "teleriumtv.com" in r:
        re_telerium = re.findall(r"src=\"(https:\/\/teleriumtv\.com\/embed\/.+?)\"", r)[0]
        return telerium.get_m3u8(re_telerium)
