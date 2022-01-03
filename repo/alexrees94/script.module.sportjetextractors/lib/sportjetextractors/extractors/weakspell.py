import requests, re, base64, json, urllib, time
from unidecode import unidecode
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
try: 
    from urlparse import urlparse
    from urllib import quote
except: from urllib.parse import urlparse, quote
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
domain = ["weakstreams.com", "sporteks.net", "liveonscore.tv", "wpstream.tv"]
site_name = "Weakspell/LiveOnScore"
short_id = "WS"

def get_m3u8(url):
    base_url = "http://" + urlparse(url).netloc
    r_game = requests.get(url).text
    re_vidgstream = re.compile(r'var vidgstream = "(.+?)";').findall(r_game)[0]
    if base_url == "http://liveonscore.tv":
        re_gethlsUrl = re.compile(r'gethlsUrl\(vidgstream, (.+?), (.+?)\);').findall(r_game)[0]
        r_hls = requests.get(base_url + "/gethls.php?idgstream=%s&serverid=%s&cid=%s" % (quote(re_vidgstream, safe=""), re_gethlsUrl[0], re_gethlsUrl[1]), headers={"User-Agent": user_agent, "Referer": url, "X-Requested-With": "XMLHttpRequest"}).text
    else:
        r_hls = requests.get(base_url + "/gethls.php?idgstream=%s" % quote(re_vidgstream, safe=""), headers={"User-Agent": user_agent, "Referer": url, "X-Requested-With": "XMLHttpRequest"}).text
    json_hls = json.loads(r_hls)
    m3u8 = json_hls["rawUrl"]
    if m3u8 == None:
        raise "no link found"
    else:
        m3u8 = m3u8 + "|Referer=" + url
    return m3u8

def get_games():
    games = []
    r = requests.get(f"http://{domain[0]}").text
    soup = BeautifulSoup(r, "html.parser")
    categories = soup.select("ul.nav-menu > li > a")
    for category in categories:
        try:
            league = unidecode(category.text.replace(" Streams", ""))
            href = category.get("href")
            r_category = requests.get(unidecode(href)).text
            soup = BeautifulSoup(r_category, "html.parser")
            for game in soup.find_all("div", class_="competition"):
                try:
                    re_url = re.compile(r'<a href="(.+?)">').findall(game.decode_contents())[0]
                    re_game = re.compile(r'<span class="competition-cell-table-cell competition-cell-side1"><span class="name"> (.+?) <\/span><span class="logo"><img.+?src="(.+?)".+?><\/span><\/span><span class="competition-cell-table-cell competition-cell-score"><i class="fa fa-clock"><\/i><span class="competition-cell-status">(.+?)<\/span><\/span><span class="competition-cell-table-cell competition-cell-side2"><span class="logo"><img.+?src="(.+?)".+?><\/span><span class="name"> (.+?)<\/span><\/span>').findall(game.decode_contents())[0]
                    title = "%s vs %s" % (re_game[0], re_game[4])
                    time_str = re_game[2].replace(" ,", ",")
                    utc_time = ""
                    if time_str != "":
                        if "LIVE" in time_str: utc_time = datetime.now(timezone.utc)
                        else: utc_time = datetime(*(time.strptime(time_str + " 2021", "%b %d, %I:%M %p %Y")[:6])) + timedelta(hours=5)
                    games.append({
                        "title": unidecode(title),
                        "links": [
                            re_url
                        ],
                        "icon": re_game[1],
                        "league": league,
                        "time": utc_time
                    })
                except Exception as e:
                    continue
        except:
            continue
    return games

# def get_games():
#     games = []
#     r = requests.get(f"https://{domain[0]}").text
#     soup = BeautifulSoup(r, "html.parser")
#     for channel in soup.select("a.other-site-tv"):
#         url = channel.get("href")
#         icon = channel.select_one("img").get("src")
#         name = channel.select_one("div.site-name-tv").text
#         games.append({
#             "title": name,
#             "links": [
#                 url
#             ],
#             "icon": icon,
#             "league": "TV",
#             "time": ""
#         })
#     return games