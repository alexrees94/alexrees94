import requests, time
from datetime import datetime, timedelta
try: from urlparse import urlparse, parse_qs
except: from urllib.parse import urlparse, parse_qs
from ..util.sportscentral_streams import get_streams_table
from unidecode import unidecode

domain = ["sportscentral.io"]
site_name = "SportsCentral"
short_id = "SC"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.344"

def get_games():
    games = []
    current_date = datetime.now()
    today = current_date.replace(hour=3, minute=0, second=0)
    date_format = current_date.strftime("%Y-%m-%d")

    leagues = ["nba", "nfl", "mlb", "nhl", "mma", "motorsport", "cricket",]
    for league in leagues:
        r = requests.get("https://sportscentral.io/api/%s-tournaments?date=%s" % (league, date_format), headers={"Referer": "https://redditmlbstreams.live", "User_Agent": user_agent}).json()
        for game_league in r:
            for event in game_league["events"]:
                home_team = event["homeTeam"]["name"]
                away_team = event["awayTeam"]["name"]
                status = event["status"]["description"]
                if status == None: status = "N/A"
                if league != "mma":
                    home_score = event["homeScore"]["current"]
                    if home_score == "": home_score = "0"
                    away_score = event["awayScore"]["current"]
                    if away_score == "": away_score = "0"
                    title = "[COLORorange]%s %s-%s[/COLOR]: %s vs %s" % (status, home_score, away_score, home_team, away_team)
                else:
                    title = "[COLORorange]%s[/COLOR]: %s vs %s" % (status, home_team, away_team)
                icon = event["homeTeam"]["logo"]
                game_id = event["id"]
                game_time_str = "%sT%s" % (event["formatedStartDate"], event["startTime"])
                game_time = datetime(*(time.strptime(game_time_str, "%Y-%m-%dT%H:%M")[:6]))
                if game_time < today: continue
                sport = event["sport"]
                links_url = "https://sportscentral.io/streams-table/%s/%s?new-ui=1&origin=mlbstreams.to" % (str(game_id), sport)
                games.append({
                    "title": unidecode(title),
                    "icon": icon,
                    "time": game_time,
                    "league": game_league["uniqueName"],
                    "links": ["links://" + links_url]
                })
    
    # Soccer
    r = requests.get("https://sportscentral.io/new-api/matches?date=" + date_format, headers={"Referer": "https://redditmlbstreams.live", "User_Agent": user_agent}).json()
    for league in r:
        events = league["events"]
        logo = league["logo"]
        league_name = league["name"]
        for event in events:
            status = event["status"]["type"]
            if status != "inprogress": continue
            home_team = event["homeTeam"]["name"]
            home_score = event["homeScore"]["current"]
            away_team = event["awayTeam"]["name"]
            away_score = event["awayScore"]["current"]
            title = "[COLORorange]%s %s-%s[/COLOR]: %s vs %s" % (status.capitalize(), home_score, away_score, home_team, away_team)
            game_id = event["id"]
            game_time = datetime.fromtimestamp(event["startTimestamp"]) + timedelta(hours=7)
            links_url = "https://sportscentral.io/streams-table/%s/soccer?new-ui=1&origin=mlbstreams.to" % (str(game_id))
            games.append({
                "title": unidecode(title),
                "icon": unidecode(logo),
                "time": game_time,
                "league": unidecode(league_name),
                "links": ["links://" + unidecode(links_url)]
            })

    return games

def get_links(url):
    return get_streams_table(url)
