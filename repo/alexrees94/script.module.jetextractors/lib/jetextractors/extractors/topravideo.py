import requests, re

from ..models.Extractor import Extractor
from ..models.Link import Link

class Topravideo(Extractor):
    def __init__(self) -> None:
        self.domains = ["topravideo.com", "vvtodmat.topravideo.com"]

    def get_link(self, url):
        r = requests.get(url).text
        re_m3u8 = re.findall(r"hls:'(.+?)'", r)
        return Link(address="https:" + re_m3u8[0])