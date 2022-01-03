import requests, re

from ..models.Extractor import Extractor
from .plytv_sdembed import PlyTv

class Embedstream(Extractor):
    def __init__(self) -> None:
        self.domains = ["embedstream.me"]

    def embedstream(self, id):
        r_embedstream = requests.get("https://embedstream.me/" + id).text
        re_zmid = re.compile(r'zmid = "(.+?)"').findall(r_embedstream)[0]
        return PlyTv().plytv_sdembed(re_zmid, "https://embedstream.me/")

    def get_link(self, url):
        return self.embedstream(url.replace("https://embedstream.me/", ""))