import requests, re
from ..util import jsunpack
from ..scanners import m3u8_src
try: from urlparse import parse_qs
except: from urllib.parse import parse_qs
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
domain = ["wstream.to", "wigistream.to"]

def get_m3u8(url):
    options = url.split("|")
    if len(options) < 2 or "referer" not in options[1].lower():
        raise Exception("Must have referer in URL")
    url = url.replace("|" + options[1], "")
    parsed_qs = parse_qs(options[1].lower())
    r = requests.get(url, headers={"Referer": parsed_qs["referer"][0]}).text
    if len(re.findall(r'source\s+?:\s+?"(.+?)"', r)) > 0:
        m3u8 = re.compile(r'source\s+?:\s+?"(.+?)"').findall(r)[0]
    elif len(re.findall(r'src\s+?:\s+?"(.+?)"', r)) > 0:
        m3u8 = re.findall(r'src\s+?:\s+?"(.+?)"', r)[0]
    else:
        re_js = jsunpack.unpack(re.compile(r"(eval\(function\(p,a,c,k,e,d\).+?{}\)\))").findall(r)[0])
        m3u8 = m3u8_src.scan_page(url, re_js)
    return m3u8