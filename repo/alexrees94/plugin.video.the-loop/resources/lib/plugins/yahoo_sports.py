from ..plugin import Plugin
from ..DI import DI
import requests, json, xbmcgui, xbmc, time, calendar
from resources.lib.plugin import run_hook
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from sportjetextractors.extractors import sportsbay

class YahooSports(Plugin):
    name = "Yahoo Sports"
    priority = 100

    def process_item(self, item):
        if "yahoo_sports" in item:
            link = item.get("yahoo_sports", "")
            item["link"] = f"yahoo_sports/games/{link}" 
            item["is_dir"] = True
            item["list_item"] = xbmcgui.ListItem(item.get("title", item.get("name", "")))
            return item

    def routes(self, plugin):
        @plugin.route("/yahoo_sports/games/<league>")
        def games(league):
            if league == "all": leagues = ["NBA", "NCAAB","NFL","NCAAF","WNBA", "NHL", "MLB", "Soccer"]
            else: leagues = [league]
            jen_list = []
            current_date = datetime.now()

            for league in leagues:
                if league == "Soccer": continue
                try:
                    r_scores = requests.get("https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard", params={"leagues": league.lower(), "date": current_date.strftime("%Y-%m-%d")}).json()
                    scoreboard = r_scores["service"]["scoreboard"]
                    teams = scoreboard["teams"]
                    for game in scoreboard["games"].values():
                        home_team_name = teams[game["home_team_id"]]["full_name"]
                        icon = scoreboard["teamsportacularLogo"][game["home_team_id"]]
                        away_team_name = teams[game["away_team_id"]]["full_name"]
                        home_score = 0
                        away_score = 0
                        for period in game["game_periods"]:
                            home_score += int(period["home_points"]) if period["home_points"] != "X" else 0
                            away_score += int(period["away_points"]) if period["away_points"] != "X" else 0
                        status = game["status_display_name"]
                            
                        game_title = "%s vs. %s" % (home_team_name, away_team_name)
                        game_title = "[COLORorange]%s %s-%s[/COLOR]: %s" % (status, str(home_score), str(away_score), game_title)
                        game_time = datetime(*(time.strptime(game["start_time"], "%a, %d %b %Y %H:%M:%S +0000")[:6]))
                        jen_list.append({
                            "title": f"{league} | {game_title}\n{self.format_time(game_time)}",
                            "thumbnail": icon,
                            "fanart": icon,
                            "sportjetextractors": "search/" + teams[game["home_team_id"]]["last_name"],
                            "type": "dir"
                        })
                except Exception as e:
                    continue
            
            if "Soccer" in leagues:
                soccer_games = {}
                for soccer_site in ["https://sportsontvusa.com", "https://ukfootballontv.co.uk"]:
                    r = requests.post(soccer_site, {"opSearch": 1}).text
                    soup = BeautifulSoup(r, "html.parser")
                    table = soup.select_one("table.table")
                    try: table_date = datetime(*(time.strptime(table.select_one("td.dia-partido").next.replace("Today ", ""), "%A, %B %d, %Y")[:6]))
                    except: table_date = datetime(*(time.strptime(table.select_one("td.dia-partido").next.replace("Today ", ""), "%A, %d %B %Y")[:6]))
                    for game in table.select("tr.event-row"):
                        game_time = game.select_one("td.hora").next
                        game_time_split = game_time.split(":")
                        game_hour = int(game_time_split[0])
                        game_minute = int(game_time_split[1])
                        game_date = table_date.replace(hour=game_hour, minute=game_minute) + timedelta(hours=4)
                        teams = [team.get("title") for team in game.select("span")]
                        try: game_icon = game.select_one("img").get("data-ezsrc")
                        except: game_icon = ""
                        if len(teams) > 1: game_title = "%s vs %s" % (teams[0], teams[1])
                        else: game_title = game.select_one("td.evento").text
                        if game_title not in soccer_games:
                            soccer_games[game_title] = {
                                "title": f"Soccer | {game_title}\n{self.format_time(game_date)}",
                                "thumbnail": game_icon,
                                "time": game_date,
                                "fanart": game_icon,
                                "sportjetextractors": "search/" + teams[0],
                                "type": "dir"
                            }
                soccer_games = sorted(soccer_games.values(), key=lambda x: x["time"])
                jen_list += soccer_games
            
            jen_list = [run_hook("process_item", item) for item in jen_list]
            jen_list = [run_hook("get_metadata", item, return_item_on_failure=True) for item in jen_list]
            run_hook("display_list", jen_list)

    def format_time(self, date):
        return self.utc_to_local(date).strftime("%m/%d %I:%M %p") if date != "" else ""

    # https://stackoverflow.com/questions/4563272/convert-a-python-utc-datetime-to-a-local-datetime-using-only-python-standard-lib
    def utc_to_local(self, utc_dt):
        timestamp = calendar.timegm(utc_dt.timetuple())
        local_dt = datetime.fromtimestamp(timestamp)
        assert utc_dt.resolution >= timedelta(microseconds=1)
        return local_dt.replace(microsecond=utc_dt.microsecond)