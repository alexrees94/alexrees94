import requests, re
from . import sawlive

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
domain = ["blueflag.ga", "www.blueflag.ga"]

def get_m3u8(url):
    r = requests.get(url, headers={"User-Agent": user_agent}).text
    iframe = re.findall(r"iframe src=\"(http:\/\/www\.sawlive\.tv\/.+?)\"", r)[0]
    return sawlive.get_m3u8(iframe)