import requests, re
from ..util import jsunpack

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
domain = ["sawlive.tv", "www.sawlive.tv"]

def get_m3u8(url):
    r = requests.get(url, headers={"User-Agent": user_agent}).text
    re_js = jsunpack.unpack(re.compile(r"(eval\(function\(p,a,c,k,e,d\).+?{}\)\))").findall(r)[0])
    jameiei = eval(re.findall(r"var jameiei=(\[.+?\])", re_js)[0])
    m3u8 = "".join([chr(x) for x in jameiei])
    return m3u8