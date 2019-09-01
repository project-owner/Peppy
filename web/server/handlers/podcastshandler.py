import os
import json

from tornado.web import RequestHandler

class PodcastsHandler(RequestHandler):
    def initialize(self, util):
        self.podcasts_util = util.get_podcasts_util()

    def get(self):
        links_str = self.podcasts_util.get_podcasts_string()
        d = json.dumps(links_str)
        self.write(d)
        return

    def put(self):
        value = json.loads(self.request.body)
        try:
            self.podcasts_util.save_podcasts(value)
        except Exception as e:
            print(e)