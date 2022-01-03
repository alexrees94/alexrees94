import requests, re
from ..scanners import clappr

domain = ["givemenbastreams.com"]

def get_m3u8(url):
    r = requests.get(url).text
    iframe = re.findall(r'iframe class=\"embed-responsive-item\" src=\"(.+?)\"', r)[0]
    return clappr.scan_page(iframe)