import requests, re

domain = ["sawlive.tv", "www.sawlive.tv"]

def get_m3u8(url):
    r = requests.get(url).text
    embed = re.findall(r"src=\"(.+?)\"", r)[0]
    r_embed = requests.get(embed).text
    var1 = re.findall(r"([a-zA-Z]+)\.split", r_embed)[0]
    var2 = re.findall(r"var\s+{}\s*=\s*[\"\']([^\"\']+)".format(var1), r_embed)[0]
    split = var2.split(";")
    embedm = "http://" + domain[0] + "/embedm/stream/%s/%s" % (split[1], split[0])
    r_embedm = requests.get(embedm).text
    jameiei = eval(re.findall(r"var jameiei = (\[.+?\])", r_embedm)[0])
    m3u8 = "".join([chr(x) for x in jameiei])
    return m3u8