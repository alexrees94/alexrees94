###########################################
#     GIVE CREDIT WHERE CREDIT IS DUE     #
#                                         #
#          T4ILS AND JETJET               #
###########################################




import json, sys, time, operator, os
from ..util.dialogs import link_dialog
from xbmcvfs import translatePath
from concurrent.futures import ThreadPoolExecutor
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
from resources.lib.plugin import Plugin
from datetime import datetime, timedelta
import calendar, inputstreamhelper
from sportjetextractors import extractors, extractor
from resources.lib.plugin import run_hook
import urllib.parse

import operator, traceback

CACHE_TIME = 0  # change to wanted cache time in seconds
DEFAULT_DISABLED = ["Full Match TV",  "Topstreams", "Buffstreams","Sling", "USTVGO", "Yahoo Sports","Yahoo Sports - MLB Highlights","Yahoo Sports - NBA Highlights","Yahoo Sports - NCAAB Highlights","Yahoo Sports - NHL Highlights","Freefeds"]

addon_fanart = xbmcaddon.Addon().getAddonInfo('fanart')
addon_icon = xbmcaddon.Addon().getAddonInfo('icon')
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'

class sportjetextractors(Plugin):
    name = "sportjetextractors"
    priority = 100

    def process_item(self, item):
        if "sportjetextractors" in item:
            link = item.get("sportjetextractors", "")
            thumbnail = item.get("thumbnail", "")
            fanart = item.get("fanart", "")
            icon = item.get("icon", "")
            if not isinstance(link, list):
                if link.startswith("http"):
                    item["is_dir"] = False
                    item["link"] = "/play_video/" + urllib.parse.quote_plus(json.dumps(item))
                elif link == "extractor_settings":
                    item["is_dir"] = False
                    item["link"] = "sportjetextractors/extractor_settings"
                else:
                    item["link"] = "sportjetextractors/games/" + link if "search" not in link else "sportjetextractors/" + link
                    item["is_dir"] = True
                
                list_item = xbmcgui.ListItem(item.get("title", item.get("name", "")), offscreen=True)
                list_item.setArt({"thumb": thumbnail, "fanart": fanart})
                item["list_item"] = list_item
                return item
        
    def play_video(self, video: str):
        item = json.loads(video)
        link = item.get("sportjetextractors")
        title = item.get("title")
        thumbnail = item.get("thumbnail", "")
        if link:
            if isinstance(link, list):   
                link = link_dialog(link)  
                if link == None: return True

                if link.startswith("links://"):
                    links = extractor.get_links(link.replace("links://", ""))
                    link = link_dialog(links)
                    if link == None: return True
            link = extractor.extract_m3u8(link)
            if link == None:
                xbmcgui.Dialog().ok("sportjetextractors Error", "sportjetextractors could not find a playable link for this URL.")
                return True
            elif link == False: return True
            if link.startswith("inputstream://"):
                mpd_split = link.split("===")
                mpd_url = mpd_split[0].replace("inputstream://", "")
                license_key = mpd_split[1]
                is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
                if not is_helper.check_inputstream():
                    sys.exit()
                liz = xbmcgui.ListItem(item.get("title", mpd_url), path=mpd_url)
                if int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0]) >= 19: liz.setProperty('inputstream', 'inputstream.adaptive')
                else: liz.setProperty('inputstreamaddon', 'inputstream.adaptive')
                liz.setProperty('inputstream.adaptive.manifest_type', 'mpd')

                if license_key != '':
                    liz.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
                    liz.setProperty('inputstream.adaptive.license_key', license_key)
                liz.setMimeType('application/dash+xml')
                liz.setContentLookup(False)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
                xbmc.Player().play(mpd_url, listitem=liz)
            elif link.startswith("ffmpegdirect://"):
                m3u8_url = link.replace("ffmpegdirect://", "")
                liz = xbmcgui.ListItem(item.get("title", m3u8_url), path=m3u8_url)
                
                liz.setInfo('video', {'Title': title})
                liz.setArt({'thumb': thumbnail, 'icon': thumbnail})
                
                if int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0]) >= 19: liz.setProperty('inputstream', 'inputstream.ffmpegdirect')
                else: liz.setProperty('inputstreamaddon', 'inputstream.ffmpegdirect')
                liz.setProperty('inputstream.ffmpegdirect.is_realtime_stream', 'true')
                liz.setProperty('inputstream.ffmpegdirect.stream_mode', 'timeshift')
                liz.setProperty('inputstream.ffmpegdirect.manifest_type', 'hls')
                liz.setMimeType('application/x-mpegURL')
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
                xbmc.Player().play(m3u8_url, listitem=liz)
            else:
                liz = xbmcgui.ListItem(title)               
                liz.setInfo('video', {'Title': title})
                liz.setArt({'thumb': thumbnail, 'icon': thumbnail})
                xbmc.Player().play(link,liz)
            return True
        
            
    def routes(self, plugin):
        @plugin.route("/sportjetextractors/games/<path:site>")
        def get_games(site):
            for module in extractors.__all__:
                if hasattr(module, "site_name") and hasattr(module, "get_games") and site == module.site_name:
                    games = module.get_games()
                    # games.sort(key = operator.itemgetter('league', 'title', 'time' ), reverse = False)
                    jen_list = []
                    for game in games:
                        jen_data = {
                            "title": "[COLORdodgerblue]%s[COLORwhite] |[B][I] %s[/B][/I]\n  [COLORred]%s[/COLOR]" % (game["league"].replace("'", ""), game["title"], format_time(game["time"])),
                            "thumbnail": game["icon"],
                            "fanart": game["icon"],
                            "summary": game["title"],
                            "sportjetextractors": game["links"],
                            "type": "item"
                        }
                        jen_list.append(jen_data)
                    jen_list = [run_hook("process_item", item) for item in jen_list]
                    jen_list = [run_hook("get_metadata", item, return_item_on_failure=True) for item in jen_list]
                    run_hook("display_list", jen_list)
        
        @plugin.route("/sportjetextractors/search/<path:query>")
        def search_games(query):
            if query == "*":
                query = xbmcgui.Dialog().input("Search game")
                if query == "": return
            games = []
            empty_date = datetime(year=3000, month=12, day=31)
            with ThreadPoolExecutor(max_workers=128) as executor:
                running_tasks = []

                addon = xbmcaddon.Addon()
                USER_DATA_DIR = translatePath(addon.getAddonInfo("profile"))
                if not os.path.exists(os.path.join(USER_DATA_DIR, f"{self.name}_disabled.json")):
                    disabled = DEFAULT_DISABLED
                else:
                    f = open(os.path.join(USER_DATA_DIR, f"{self.name}_disabled.json"), "r")
                    disabled = json.load(f)
                    f.close()
                for module in extractors.__all__:
                    if hasattr(module, "site_name") and hasattr(module, "get_games") and module.site_name not in disabled:
                        running_tasks.append(executor.submit(lambda: [module.site_name, module.get_games()]))
                for running_task in running_tasks:
                    try:
                        site_name = running_task.result()[0]
                        site_games = running_task.result()[1]
                        for game in site_games:
                            if query.lower() not in game["title"].lower() and query.lower() not in game["league"].lower(): continue
                            jen_data = {
                                "title": "[COLORdodgerblue]%s[COLORwhite] |[B][I] %s[/B][/I]\n  [COLORred]%s | %s[/COLOR]" % (game["league"].replace("'", ""), game["title"], site_name, format_time(game["time"])),
                                "thumbnail": game["icon"],
                                "fanart": game["icon"],
                                "summary": game["title"],
                                "sportjetextractors": game["links"],
                                "time": game["time"].timestamp() if game["time"] != "" else empty_date.timestamp(),
                                "type": "item"
                            }
                            games.append(jen_data)
                    except Exception as e:
                        continue
            
            games = sorted(games, key=lambda x: x["time"])
            games = [run_hook("process_item", item) for item in games]
            games = [run_hook("get_metadata", item, return_item_on_failure=True) for item in games]
            run_hook("display_list", games)

        @plugin.route("/sportjetextractors/search_dialog/<path:query>")
        def search_dialog(query):
            query = urllib.parse.unquote_plus(query)
            if query == "*":
                query = xbmcgui.Dialog().input("Search game")
                if query == "": return
            games = []
            empty_date = datetime(year=3000, month=12, day=31)
            xbmcgui.Dialog().notification("Searching", "Searching for links...", xbmcgui.NOTIFICATION_INFO)
            with ThreadPoolExecutor(max_workers=128) as executor:
                running_tasks = []

                addon = xbmcaddon.Addon()
                USER_DATA_DIR = translatePath(addon.getAddonInfo("profile"))
                if not os.path.exists(os.path.join(USER_DATA_DIR, f"{self.name}_disabled.json")):
                    disabled = DEFAULT_DISABLED
                else:
                    f = open(os.path.join(USER_DATA_DIR, f"{self.name}_disabled.json"), "r")
                    disabled = json.load(f)
                    f.close()
                for module in extractors.__all__:
                    if hasattr(module, "site_name") and hasattr(module, "get_games") and module.site_name not in disabled:
                        running_tasks.append(executor.submit(lambda: [module.site_name, module.get_games()]))
                for running_task in running_tasks:
                    try:
                        site_name = running_task.result()[0]
                        site_games = running_task.result()[1]
                        for game in site_games:
                            if query.lower() not in game["title"].lower() and query.lower() not in game["league"].lower(): continue
                            jen_data = {
                                "title": f"[COLORdodgerblue]{site_name}[/COLOR] - {game['title']}",
                                "thumbnail": game["icon"],
                                "fanart": game["icon"],
                                "summary": game["title"],
                                "sportjetextractors": game["links"],
                                "time": game["time"].timestamp() if game["time"] != "" else empty_date.timestamp(),
                                "type": "item"
                            }
                            games.append(jen_data)
                    except Exception as e:
                        continue
            
            idx = link_dialog([game["title"] for game in games], return_idx=True, hide_links=False)
            if idx == None:
                return True
            self.play_video(json.dumps(games[idx]))
        
        @plugin.route("/sportjetextractors/play")
        def play():
            urls = plugin.args["urls"][0].split("***")
            return self.play_video(json.dumps({"sportjetextractors": urls}))

    
        @plugin.route("/sportjetextractors/extractor_settings")
        def extractor_settings():
            addon = xbmcaddon.Addon()
            USER_DATA_DIR = translatePath(addon.getAddonInfo("profile"))
            if not os.path.exists(USER_DATA_DIR):
                os.makedirs(USER_DATA_DIR)
            if not os.path.exists(os.path.join(USER_DATA_DIR, f"{self.name}_disabled.json")):
                f = open(os.path.join(USER_DATA_DIR, f"{self.name}_disabled.json"), "w")
                f.write(json.dumps(DEFAULT_DISABLED))
                f.close()
            
            options = list(filter(lambda module: hasattr(module, "site_name") and hasattr(module, "get_games"), extractors.__all__))
            option_names = [module.site_name for module in options]
            enabled = []
            f = open(os.path.join(USER_DATA_DIR, f"{self.name}_disabled.json"), "r+")
            disabled_extractors = json.load(f)
            for i, option in enumerate(option_names):
                if option not in disabled_extractors:
                    enabled.append(i)
            
            dialog = xbmcgui.Dialog().multiselect("Extractors", options=option_names, preselect=enabled)
            if dialog == None: return
            disabled = []
            for i in range(len(option_names)):
                if i not in dialog:
                    disabled.append(option_names[i])
            
            f.seek(0)
            f.write(json.dumps(disabled))
            f.truncate()
            f.close()
            xbmcgui.Dialog().ok("Success!", "Settings saved.")



def format_time(date):
    return utc_to_local(date).strftime("%m/%d %I:%M %p") if date != "" else ""

# https://stackoverflow.com/questions/4563272/convert-a-python-utc-datetime-to-a-local-datetime-using-only-python-standard-lib
def utc_to_local(utc_dt):
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)


