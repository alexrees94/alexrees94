import requests, re
from .plytv_sdembed import plytv_sdembed

domain = ["embedstream.me"]

def embedstream(id):
    r_embedstream = requests.get("https://embedstream.me/" + id).text
    re_zmid = re.compile(r'zmid = "(.+?)"').findall(r_embedstream)[0]
    return plytv_sdembed(re_zmid, "https://embedstream.me/")

def get_m3u8(url):
    return embedstream(url.replace("https://embedstream.me/", ""))

# Test
if __name__ == "__main__":
    print(embedstream("nfl-network-stream-1"))