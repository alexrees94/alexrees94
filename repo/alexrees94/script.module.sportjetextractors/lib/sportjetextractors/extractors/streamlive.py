import requests, re

domain = ["streamlive.to"]
site_name = "Streamlive"
short_id = "SL"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"

def get_m3u8(url):
    r = requests.get(url, headers={"User-Agent": user_agent}).text
    vars = re.findall("var\s*([^\s=]+)\s*=\s*(\[[^\]]+\])\s*;", r)
    var_map = {}
    for v in vars: var_map[v[0]] = "".join(eval(v[1]))
    ids = re.findall('id\s*=\s*([^<]+)>([^<]+)', r)
    id_map = {}
    for i in ids: id_map[i[0]] = i[1]
    info = re.findall('(\[[^\]]+\]).join.+? \+\s*([a-zA-Z]+).join.+?\+.+?document.getElementById\([\"\']([^\"\']+)', r)[0]
    server = "https:" + "".join(eval(info[0])).replace('\\/','/')
    m3u8 = server + var_map[info[1]] + id_map[info[2]]
    return m3u8 + f"|Referer={url}"
