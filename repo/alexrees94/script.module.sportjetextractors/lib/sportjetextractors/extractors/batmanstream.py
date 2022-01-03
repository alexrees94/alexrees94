import requests, re, json, time
from datetime import datetime, timedelta

domain = ["batman-stream.com"]
site_name = "Batmanstream"
short_id = "BMS"

def get_games():
    games = []
    r = requests.get("https://live.batstream.live/list.php").text
    ev_arr = re.findall(r"var ev_arr=(.+?\]);", r)[0]
    events = json.loads(ev_arr)
    chan_arr = re.findall(r"var chan_arr=(.+?\});", r)[0]
    channels = json.loads(chan_arr)
    for event in events:
        try:
            title = event["match"]
            icon = "https://live.batstream.live/img/countries/" + event["country"]
            sport = event["sport"]
            date = datetime(*(time.strptime(event["date"], "%Y-%m-%d %H:%M:%S")[:6])) - timedelta(hours=1)
            links = list(filter(lambda x: "advsmedia" not in x, [link["link"] for link in channels[event["id"]]]))
            games.append({
                "title": title,
                "icon": icon,
                "league": sport,
                "time": date,
                "links": links
            })
        except: continue
    return games