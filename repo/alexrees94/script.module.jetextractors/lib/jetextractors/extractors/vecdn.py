import requests, re

from ..models.Extractor import Extractor
from ..models.Link import Link

class VeCDN(Extractor):
    def __init__(self) -> None:
        self.domains = [".+vecdn.pw"]
        self.domains_regex = True

    def get_link(self, url):
        r = requests.get(url).text
        fid = re.findall(r"fid='(.+?)'", r)[0]
        r_ragnaru = requests.get("https://ragnaru.net/embed.php?player=desktop&live=" + fid, headers={"Referer": url}).text
        m3u8 = "".join(eval(re.findall(r"return\((\[.+?\])", r_ragnaru)[0])).replace("\\", "")
        return Link(address=m3u8, headers={"Referer": "https://ragnaru.net/"})