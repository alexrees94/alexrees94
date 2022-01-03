import requests, re, time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
try: from urlparse import urlparse
except: from urllib.parse import urlparse
from ..util import sportscentral_streams

domain = ["scor.nbabite.com", "reddit.nflbite.com", "nhlbite.com", "mlbshow.com", "cricketstreams.cc", "formula1stream.cc", "live.mmastreams.cc", "watch.boxingstreams.cc", "wwestreams.cc", "olympicstreams.net"]
site_name = "NBAbite"
short_id = "NBAB"

def get_games():
    games = []
    for site in domain:
        try:
            r = requests.get("https://" + site).text
            soup = BeautifulSoup(r, "html.parser")
            date = datetime(*(time.strptime(soup.select_one("div.date").text.strip(), "%a %d %b %Y")[:6]))
            other_sites = soup.select("a.other-site")
            league = ""
            for other_site in other_sites:
                if urlparse(other_site.get("href")).netloc == site:
                    league = other_site.select_one("div.site-name").text.strip().replace(" Streams", "")
            if "olympic" in site:
                for competition in soup.select("div.competition"):
                    competition_name = competition.select_one("div.name").text
                    for game in soup.select("div.col-md-12"):
                        title = game.select_one("div.team-name").text
                        href = game.select_one("a").get("href")
                        games.append({
                            "title": title,
                            "icon": "",
                            "time": "",
                            "league": f"{league} {competition_name}",
                            "links": ["links://" + href]
                        })
            else:
                for game in soup.select("div.col-md-6"):
                    team_names = [team.text for team in game.select("div.team-name")]
                    title = "%s vs %s" % (team_names[0], team_names[1])
                    status = game.select_one("div.status")
                    game_time = ""
                    if "live-indicator" not in status.attrs["class"] and ":" in status.text:
                        split = status.text.split(":")
                        hour = int(split[0])
                        minute = int(split[1])
                        game_time = date.replace(hour=hour, minute=minute) + timedelta(hours=4)
                    else:
                        title = "[COLORyellow]%s[/COLOR] - %s" % (status.text, title)
                    score = game.select("div.score")
                    if len(score) > 0 and score[0].text:
                        scores = [i.text for i in score]
                        title =  "%s [COLORyellow](%s-%s)[/COLOR]" % (title, scores[0], scores[1])
                    icon = game.select_one("img").get("src")
                    href = game.select_one("a").get("href")
                    
                    games.append({
                        "title": title,
                        "icon": icon,
                        "time": game_time,
                        "league": league,
                        "links": ["links://" + href]
                    })
        except:
            continue
    
    return games

def get_links(url):
    r = requests.get(url).text
    match_id = re.findall(r"var streamsMatchId = (.+?);", r)[0]
    match_sport = re.findall(r"var streamsSport = \"(.+?)\"", r)[0]
    streams = sportscentral_streams.get_streams(match_id, match_sport, domain[0])
    return streams


