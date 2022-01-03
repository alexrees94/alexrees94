import requests
from bs4 import BeautifulSoup

def get_streams(match_id, match_sport, origin):
    url = "https://sportscentral.io/streams-table/%s/%s?new-ui=1&origin=%s" % (match_id, match_sport, origin)
    links = get_streams_table(url)
    return links

def get_streams_table(url):
    links = []
    r_streams = requests.get(url).text
    soup = BeautifulSoup(r_streams, "html.parser")
    for stream in soup.select("tbody > tr"):
        href = stream.get("data-stream-link")
        name = stream.select_one("span.first").text.strip()
        quality = stream.select_one("span.label-purple").text.strip()
        links.append(href + "(%s %s)" % (name, quality))
    return links