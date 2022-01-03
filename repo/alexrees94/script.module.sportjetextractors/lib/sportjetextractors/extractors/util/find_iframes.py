import requests, re

try: from urllib.parse import urlparse
except: from urlparse import urlparse

ad_hosts = ""
def find_iframes(url, links = [], checked = []):
    try:
        
        links = links
        checked = checked
        r = requests.get(url, allow_redirects=True, timeout=7, headers={"Referer": url})
        if r.status_code == 200:
            urls = re.findall('i?frame\s*.+?src=[\"\']?([^\"\']+)', r.text, flags=re.IGNORECASE)
            urls = __customUrls(r.text, url, urls)
            for u in urls:
                if urlparse(u).netloc == '':
                    if u.startswith('/'):	
                        u = 'http://' + urlparse(url).netloc + '/' + u
                    else:
                        u = 'http://' + urlparse(url).netloc + '/'.join(urlparse(url).path.split('/')[:-1]) +  '/' + u
                if urlparse(u).scheme == '':
                    u = 'http://' + u.replace('//','')


                u = re.sub(r'\n+', '', u)
                u = re.sub(r'\r+', '', u)
                
                if not isAd(u) and u not in checked and __checkUrl(u) and u not in links and len(links)<15:
                    links.append(u + ("|Referer=" + url if "wigistream" in u else ""))
                    links += find_iframes(u, links, checked)
                    checked.append(u)
            return list(set(links))
        return []
    except: return []

def isAd(host):
    global ad_hosts
    if ad_hosts == "":
        ad_hosts = requests.get('https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts').text
    h = urlparse(host).netloc
    return (h in ad_hosts) or "/ad" in host

def __checkUrl(url):
		blacklist = ['chatango', 'adserv', 'live_chat', 'ad4', 'cloudfront', 'image/svg', 'getbanner.php','/ads', 'ads.', 'adskeeper', '.js', '.jpg', '.png', '/adself.', 'min.js', 'mail.ru']
		return not any(w in url for w in blacklist)

def __customUrls(r, ref, urls):
    fid = re.findall('id\s*=\s*[\"\']([^\"\']+).+?jokersplayer.+?\.js', r)
    tiny = re.findall('href\s*=\s*[\"\']([^\"\']+).+?class\s*=\s*[\"\']btn\s*btn\-secondary', r)
    unes = re.findall('=\s*[\"\']([^\"\']+)[\"\']+[^\"\']+unescape', r)
    multiline = re.findall('i?frame\s*.+?src=[\"\']?([^\"\']+)', r, flags=re.IGNORECASE | re.DOTALL)
    telerium = re.findall('id\s*=\s*[\"\']([^\"\']+).+?embed.telerium.+?\.js', r)
    url_in_url = bool(re.search('streamlink\.slice\(4\)', r))
    us = []
    if len(fid) > 0:
        u = 'http://www.jokersplayer.xyz/embed.php?u=' + fid[0]
        us.append(u)

    if len(telerium) > 0:
        u = 'http://telerium.club/embed/' + telerium[0] +'.html'
        us.append(u)

    if len(tiny) > 0:
        urls.append(tiny[0])

    if len(unes) > 0:
        u = unes[0].replace('@', '%')
        import urllib
        html = urllib.unquote(u).decode('utf8')
        try:
            u = re.findall('i?frame\s*.+?src=[\"\']?([^\"\']+)', html, re.IGNORECASE)[0]
            us.append(u)
        except:
            pass
    if len(multiline)>0:

        for u in multiline:
            us.append(u)
    if url_in_url:
        u = re.findall('\?.{3}([^$]+)', ref)[0]
        us.append(u)
    for u in us:
        if not isAd(u) and __checkUrl(u) and u not in urls:
            urls.append(u)
    return urls