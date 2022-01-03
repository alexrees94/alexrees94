from re import L
import requests, json, time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import tz
from ..external.airtable.airtable import Airtable
# from airtable.airtable import Airtable
from unidecode import unidecode
current_date = datetime.now()
domain = []
site_name = "Direct_CH2"
short_id = "DIRECT2"

def get_games():
    channels_table = Airtable("appLN8hccpRoZIikO", "DIRECT_CHANNELS", api_key="keyvWT1TdSyCaibez")
    m3u8_table = Airtable("appLN8hccpRoZIikO", "IPTVmine1", api_key="keyvWT1TdSyCaibez")

    channels_records = channels_table.get_all()
    m3u8_records = m3u8_table.get_all()

    m3u8s = {}
    for m3u8_record in m3u8_records:
        record_id = unidecode(m3u8_record["id"])
        fields = m3u8_record["fields"]
        urls = []
        # if "url" in fields and "://" in fields["url"]: urls.append(unidecode(fields["url"]))
        if "SERVER2" in fields and "://" in fields["SERVER2"]: urls.append(unidecode(fields["SERVER2"]))
        # if "SERVER" in fields and "://" in fields["SERVER"]: urls.append("ffmpegdirect://" + unidecode(fields["SERVER"]))
        # if "test" in fields and "://" in fields["test"]: urls.append("PlayMedia(&quot;pvr://channels/tv/All%20channels/pvr.iptvsimple_" + unidecode(fields["test"]))
        # for i in range(1, 5):
        #     if "link" + str(i) in fields:
        #         url = fields["link" + str(i)]
        #         if "://" in url: urls.append(unidecode(url))
        m3u8s[record_id] = urls

    games = []
    for record in channels_records:
        fields = record["fields"]
        if "name" in fields:
            name = fields["name"]
            thumbnail = fields.get("icon", "")
            urls = []
            if "url" in fields and fields["url"] != "-": urls.append(fields["url"].strip())
            if "link1" in fields and fields["link1"] != "-": urls.append(fields["link1"].strip())
            if "IPTVmine1" in fields and fields["IPTVmine1"] != "-":
                for record_id in fields["IPTVmine1"]: urls.extend(m3u8s[record_id])
            # if "IPTVCAT" in fields and fields["IPTVCAT"] != "-":
                # for record_id in fields["IPTVCAT"]: urls.extend(m3u8s[record_id])    
            games.append({
                "title": name,
                "links": urls,
                "icon": thumbnail,
                "league": "",
                "time": ""
            })

    try:
        import xbmc
        games.insert(0, {
            "title": "TEST",
            "links": [],
            "icon": "",
            "league": "",
            "time": ""
        })
    except: pass
    
    return games