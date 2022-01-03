import requests, re, json, html

domain = ["ok.ru"]
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"

def get_m3u8(url):
    r_embed = requests.get(url, headers={"User-Agent": user_agent}).text
    embed_json = json.loads(html.unescape(re.compile(r'data-options="(.+?)"').findall(r_embed)[0]))
    metadata_json = json.loads(embed_json["flashvars"]["metadata"])
    return metadata_json["hlsManifestUrl"] + "|User-Agent=%s" % (user_agent)