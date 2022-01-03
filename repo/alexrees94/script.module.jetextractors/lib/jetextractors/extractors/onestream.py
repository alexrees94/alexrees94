import requests, re, base64
from ..models.Extractor import Extractor
from ..models.Link import Link

class Onestream(Extractor):
    def __init__(self) -> None:
        self.domains = ["1stream.top"]

    def get_link(self, url):
        r = requests.get(url, headers={"User-Agent": self.user_agent}).text
        re_b64 = re.findall(r"window\.atob\('(.+?)'\)", r)[0]
        re_cdn = re.findall(r'const cdn = \["(.+?)"', r)[0]
        host = base64.b64decode(re_b64).decode("ascii")
        host = host.replace(host.replace("https://", "").split(".")[0], re_cdn)
        return Link(address=host, headers={"Referer": url})