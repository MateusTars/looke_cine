import re
import os
import sys
import json
import html
import requests
import pycaption
from bs4 import BeautifulSoup

class LookeCineSubtitle(object):
    def __init__(self, url="", subtitle_type=""):
        self.url = url
        self.type = subtitle_type
        self.core = "http://ottvscaption.blob.core.windows.net/cap/{0}.{1}/{2}_pt-br.vtt"
        self.output = "{0}.{1}"
        self.session = requests.Session()
        self.session.headers.update({
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
        })

    def _print_help(self):
        print("usage: python looke_cine.py [url] [subtitle_type]")
        print("subtitle types: srt or vtt")
        return 1

    def _url_verify(self, url):
        if url.startswith("https"):
            return True
        else:
            return False

    def _build_core(self, url):
        p = url.split('/')[-2]
        prod, id = p.split('.')[0], p.split('.')[-1]
        url = self.core.format(prod, str(id).zfill(6), str(id).zfill(7))
        return url

    def _to_srt(self, name, response):
        response.encoding = 'utf-8'
        subtitle = pycaption.SRTWriter().write(pycaption.WebVTTReader().read(response.text))
        print("{} - successfully".format(self.output.format(name, "srt")))
        with open(self.output.format(name, "srt"), "w", encoding="utf-8") as f:
            f.write(subtitle)
            f.close()
        return True

    def _vtt(self, name, response):
        print("{} - successfully".format(self.output.format(name, "vtt")))
        with open(self.output.format(name, "vtt"), "wb") as f:
            f.write(response.content)
            f.close()
        return True

    def _process(self):

        if not self._url_verify(self.url):
            print("ERROR: invalid URL: {}".format(self.url))
            print("example url - Looke: {0} or Cinema Virtual: {1}".format(
                "https://www.looke.com.br/filmes/renascida-das-trevas",
                "https://www.cinemavirtual.com.br/filmes/a-deusa-dos-vagalumes"
            ))
            return 1

        try:
            resp = self.session.get(url=self.url)
            resp.raise_for_status()
        except:
            print("ERROR: movie request - status code: {0} - response: {1}".format(resp.status_code, resp.text))
            return 1

        soup = BeautifulSoup(resp.text, "html.parser")

        try:
            resp_json = json.loads("".join(soup.find("script", {"type":"application/ld+json"}).contents))
        except:
            print("ERROR: html parser(BeautifulSoup) - status code: {0} - response: {1}".format(resp.status_code, resp.text))
            return 1

        name = re.sub(r'[/\\:*?"<>|]', '', html.unescape(resp_json["name"]))
        subtitle_url = self._build_core(resp_json["image"]["url"])

        try:
            resp = self.session.get(url=subtitle_url)
            resp.raise_for_status()
        except:
            print("ERROR: subtitle download - status code: {0} - response: {1}".format(resp.status_code, resp.text))
            return 1

        if self.type == "srt":
            self._to_srt(name, resp)
        else:
            self._vtt(name, resp)

        return 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(LookeCineSubtitle()._print_help())
    sys.exit(LookeCineSubtitle(sys.argv[1], sys.argv[2])._process())