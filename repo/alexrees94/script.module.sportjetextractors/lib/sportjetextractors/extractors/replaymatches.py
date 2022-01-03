import requests
from bs4 import BeautifulSoup

domain = ["replaymatches.net", "www.replaymatches.net"]
site_name = "ReplayMatches"
short_id = "RM"

def get_games():
    games = []
    r = requests.get(f"https://{domain[0]}/search?q=*&max-results=50&by-date=true").text
    soup = BeautifulSoup(r, "html.parser")
    for game in soup.select("div.post-outer"):
        game_title = game.select_one("h2.post-title").text.strip()
        try: game_league = game.select_one("a.label-info").text
        except: game_league = ""
        game_href = game.select("a")[2].get("href")
        game_icon = game.select("img")[1].get("src")
        games.append({
            "title": game_title,
            "links": [
                "links://" + game_href
            ],
            "icon": game_icon,
            "league": game_league,
            "time": "",
        })
    return games

def get_links(url):
    links = []
    r = requests.get(url).text
    soup = BeautifulSoup(r, "html.parser")
    if len(soup.select("a.link-iframe")) > 0:
        for link in soup.select("a.link-iframe"):
            embed = link.get("href")
            links.append(embed + f"({link.text})")
    else:
        iframe = soup.select_one("iframe")
        links.append(iframe.get("src") + "(Highlights)")
    return links
