import json
import urllib.request
import urllib.parse


class AdGuard:

    def __init__(self, url):
        self.url = url.rstrip("/")

    def get(self, endpoint, params=None):
        url = self.url + endpoint

        if params:
            url += "?" + urllib.parse.urlencode(params)

        with urllib.request.urlopen(
            url, timeout=10
        ) as response:
            return json.load(response)

    def status(self):
        return self.get("/control/status")

    def clients(self):
        return self.get("/control/clients")

    def querylog(self, limit=500, older_than=None):
        params = {"limit": limit}

        if older_than:
            params["older_than"] = older_than

        return self.get("/control/querylog", params)
