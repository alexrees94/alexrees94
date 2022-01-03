from ..plugin import Plugin
from ..DI import DI
import xbmcgui, xbmc, calendar
from resources.lib.plugin import run_hook
from datetime import datetime, timedelta
from jetextractors.extractors import sportsbay

class Sportsbay(Plugin):
    name = "Sportsbay"
    priority = 100

    def process_item(self, item):
        if "sportsbay" in item:
            link = item.get("sportsbay", "")
            item["link"] = f"sportsbay/games/{link}" 
            item["is_dir"] = True
            item["list_item"] = xbmcgui.ListItem(item.get("title", item.get("name", "")))
            return item

    def routes(self, plugin):
        @plugin.route("/sportsbay/games/<league>")
        def games(league):
            if league == "all": leagues = []
            else: leagues = [league]
            jen_list = []
            sportsbay_games = sportsbay.get_games()
            for game in sportsbay_games:
                if len(leagues) > 0 and leagues[0] not in game["league"]: continue
                
                jen_list.append({
                    "title": f"{game['league']} | {game['title']}\n{self.format_time(game['time'])}",
                    "thumbnail": game["icon"],
                    "fanart": game["icon"],
                    "sportjetextractors": "search/" + ((game["teams"][0].split(" ")[-1] if len(game["teams"][0].split(" ")[-1]) > 3 else game["teams"][0]) if len(game["teams"]) > 0 else game["title"]),
                    "type": "dir"
                })
            
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