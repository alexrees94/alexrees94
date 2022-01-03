import re, requests, base64
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"

def scan_page(url, html=None, headers={}):
    res = None
    if headers == {}: headers["User-Agent"] = user_agent
    if html == None: html = requests.get(url, headers=headers).text
    url = url.replace("&", "_")
    r = re.findall(r"source src=\"(.+?\.m3u8)\"", html)
    r_var = re.findall(r"var source.?=.?(?:\"|')(.+?)(?:\"|')", html)
    r2 = re.findall(r"source\s*:\s+?(?:\"|')(.+?)(?:\"|')", html)
    r3 = re.findall(r"(?:\"|')(http.*?\.m3u8.*?)(?:\"|')", html)
    r_b64 = re.findall(r"atob\((?:\"|')(aHR.+?)(?:\"|')", html)
    if len(r) > 0: res = r[0]
    elif len(r_var) > 0:
        for match in r_var:
            if ".m3u8" in match: 
                res = match
                break
    elif len(r2) > 0:
        for match in r2:
            if ".m3u8" in match: 
                res = match
                break
    elif len(r3) > 0:
        for match in r3:
            if ".m3u8" in match:
                res = match
                break
    elif len(r_b64) > 0:
        for match in r_b64:
            b64 = base64.b64decode(match).decode("ascii")
            if ".m3u8" in b64: res = b64
    
    if type(res) == str:
        if res.startswith("//"): res = ("https:" if url.startswith("https") else "http:") + res
        if "aces2" not in url: res = res + "|Referer=%s&User-Agent=%s" % (url, user_agent)
        
    return res