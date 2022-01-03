import requests
from datetime import datetime, timedelta
site_name = "Yahoo Sports - NBA Highlights"
short_id = "YAHOO_HL"
domain = []

def _get_games(date):
    games = []
    for league in ["NBA"]:
        try:
            r_scores = requests.get("https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard", params={"leagues": league.lower(), "date": date.strftime("%Y-%m-%d")}).json()
            scoreboard = r_scores["service"]["scoreboard"]
            for _, highlight in scoreboard["gamehighlight"].items():
                games.append({
                    "title": highlight["title"],
                    "links": ["https://video.media.yql.yahoo.com/v1/video/sapi/hlsstreams/%s.m3u8?site=sports&region=US&lang=en-US&devtype=desktop&src=sapi" % highlight["uuid"]],
                    "icon": highlight["thumbnail"]["url"],
                    "league": league,
                    "time": date.replace(hour=12, minute=0)
                })
        except: continue
    return games

def get_games():
    games = _get_games(datetime.now()) + _get_games(datetime.now() - timedelta(days=1))
    return games
