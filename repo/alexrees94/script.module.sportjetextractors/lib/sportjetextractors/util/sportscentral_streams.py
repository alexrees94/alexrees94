import requests
from bs4 import BeautifulSoup
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.344"

def get_streams(match_id, match_sport, origin):
    url = "https://sportscentral.io/streams-table/%s/%s?new-ui=1&origin=%s" % (match_id, match_sport, origin)
    links = get_streams_table(url)
    return links

def get_streams_table(url):
    links = []
    r_streams = requests.get(url, headers={"User-Agent": user_agent, "Referer": "https://nbabite.com"}).text
    soup = BeautifulSoup(r_streams, "html.parser")
    for stream in soup.select("tbody > tr"):
        href = stream.get("data-stream-link")
        name = stream.select_one("span.first").text.strip()
        quality = stream.select_one("span.label-purple").text.strip()
        links.append(href + "(%s %s)" % (name, quality))
    return links