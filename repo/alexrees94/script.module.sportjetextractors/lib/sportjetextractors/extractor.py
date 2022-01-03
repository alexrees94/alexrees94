###########################################
#     GIVE CREDIT WHERE CREDIT IS DUE     #
#                                         #
#      T4ILS AND JETJET                   #
###########################################



import xbmc, xbmcgui, unidecode, requests, re
from . import extractors
from .util.keys import Keys
from unidecode import unidecode
try: from urlparse import urlparse
except: from urllib.parse import urlparse
from .util.find_iframes import find_iframes
from . import scanners
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"

def __extract_m3u8(url, recursing=False):
    url = unidecode(url.strip())
    if url.startswith("links://"):
        links = get_links(url.replace("links://", ""))
        url = link_dialog(links)
        if url == None: return

    try:
        domain = urlparse(url).netloc
        for module in extractors.__all__:
            if domain in module.domain and hasattr(module, "get_link"):
                xbmc.log("detected link domain: " + domain, xbmc.LOGINFO)
                url = module.get_link(url)
                domain = urlparse(url).netloc
        for module in extractors.__all__:
            if hasattr(module, "get_m3u8") and (domain in module.domain or (len(module.domain) > 0 and module.domain[0].startswith("*") and domain.endswith(module.domain[0][1:]))):
                xbmc.log("detected domain: " + domain, xbmc.LOGINFO)
                url = module.get_m3u8(url)
                if hasattr(module, "use_ffmpeg") and module.use_ffmpeg == True:
                    url = "ffmpegdirect://%s" % (url)
                return url
    except Exception as e:
        xbmc.log("jetextractors error (domain: %s): %s" % (domain, str(e)), xbmc.LOGERROR)
        return url
    

    direct_link = "direct://" in url or re.search(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", url) != None or ".m3u8" in url
    if not recursing and not direct_link and xbmcgui.Dialog().yesno("No extractor", "Jetextractors does not have an extractor for this site (%s). Would you like to attempt to search the page for a link?" % domain):
        try:
            r = requests.get(url, headers={"User-Agent": user_agent}).text
            for scanner in scanners.__all__:
                scan = scanner.scan_page(url, html=r)
                if scan: return scan
        except:
            pass
        iframes = find_iframes(url)
        if len(iframes) > 0:
            if len(iframes) > 1:
                idx = xbmcgui.Dialog().select("Choose a link", iframes)
                if idx != -1: link = iframes[idx]
                else: return False
            else: link = iframes[0]
            return __extract_m3u8(link, True)
        else: return None
    else:
        if direct_link: return url.replace("direct://" if url.startswith("direct://") else "", "")
        else: return False if not recursing else None
    
def link_dialog(links):
    if len(links) == 1: return links[0]
    options = []
    for i, link in enumerate(links):
        if "(" in link and link.endswith(")"):
            split = link.split('(')
            label = split[-1].replace(')', '')
            options.append("%s - %s" % (label, split[0]))
            links[i] = split[0]
        else:
            options.append(link)
    idx = xbmcgui.Dialog().select("Choose a link", options)
    if idx == -1: return None
    else: return links[idx]

def extract_m3u8(url):
    res = __extract_m3u8(url)
    if type(res) == str:
        if "mlb.com/" in res:
            if "|" in res: res = re.findall("(.+?)\|", res)[0]
            mlb_auth = Keys.get_key(Keys.mlb)
            res += "|Authorization=" + mlb_auth
        elif "nhl.com/" in res:
            if "|" in res: res = re.findall("(.+?)\|", res)[0]
            nhl_auth = Keys.get_key(Keys.nhl)
            res += "|Cookie=Authorization=" + nhl_auth
    return res

def get_links(url):
    url = unidecode(url)
    domain = urlparse(url).netloc
    for module in extractors.__all__:
        if domain in module.domain and hasattr(module, "get_links"):
            xbmc.log("detected links domain: " + domain, xbmc.LOGINFO)
            links = module.get_links(url)
            return links