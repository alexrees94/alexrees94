import requests, re, base64, json
from bs4 import BeautifulSoup
try: from urllib.parse import urlparse
except: from urlparse import urlparse
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
domain = ["yoursports.stream"]
site_name = "Yoursports"
short_id = "YS"

def get_regex_yoursports(text):
    if "rbnhd" in text:
        return r"var rbnhd = '(.+?)'"
    else:
        return r'var mustave.?=.?atob\((.+?)\)'

def get_m3u8(url):
    stream = requests.get(url, headers={"User-Agent": user_agent}).text
    try:
        link = re.compile(get_regex_yoursports(stream)).findall(stream)[0]
    except:
        iframe_src = re.compile('iframe.+?src="(.+?)" allowfullscreen="yes".+?>', re.DOTALL).findall(stream)[0]
        r_embed = requests.get(iframe_src, headers={"User-Agent": user_agent, "Referer": url}).text
        link = re.compile(get_regex_yoursports(r_embed)).findall(r_embed)[0]

    if not link.startswith("http") and not link.startswith("/"):
        link = base64.b64decode(link).decode("ascii").replace("'", "")
        if link.startswith('/'):
            try: link = "http://" + urlparse(iframe_src).netloc + link
            except: link = "http://%s" % domain[0] + link
    
    try: link = '%s|Referer=%s&User-Agent=%s' % (link, iframe_src, user_agent)
    except: link = "%s|Referer=%s&User-Agent=%s" % (link, domain[0], user_agent)

    return link