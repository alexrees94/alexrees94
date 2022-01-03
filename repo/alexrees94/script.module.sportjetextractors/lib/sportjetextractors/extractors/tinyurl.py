
import requests, re
from ..util import hunter
domain = ["tinyurl.is"]

def get_link(url):
    r = requests.get(url).text
    re_hunter = re.compile(r'decodeURIComponent\(escape\(r\)\)}\("(.+?)",(.+?),"(.+?)",(.+?),(.+?),(.+?)\)').findall(r)[0]
    deobfus = hunter.hunter(re_hunter[0], int(re_hunter[1]), re_hunter[2], int(re_hunter[3]), int(re_hunter[4]), int(re_hunter[5]))
    link = re.findall(r'\.attr\(\"href\",\"(.+?)\"', deobfus)[1]
    return link
