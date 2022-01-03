import requests, re

domain = ["iptvcat.com", "list.iptvcat.com"]

def get_m3u8(url):
    if not url.endswith(".m3u8"): return url
    r = requests.get(url).text
    m3u8 = re.compile(r'(http(?:s?):\/\/.+?)\?').findall(r)[0]
    location = re.compile(r'http(?:s?):\/\/.+?\/').findall(m3u8)[0]
    endpoint = m3u8.replace(location, "")
    link = "ffmpegdirect://%slive/%s.m3u8" % (location, endpoint) 
    return link