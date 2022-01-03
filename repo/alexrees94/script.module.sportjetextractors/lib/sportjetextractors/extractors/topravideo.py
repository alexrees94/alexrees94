import requests, re

domain = ["topravideo.com", "vvtodmat.topravideo.com"]

def get_m3u8(url):
    r = requests.get(url).text
    re_m3u8 = re.findall(r"hls:'(.+?)'", r)
    return "https:" + re_m3u8[0]