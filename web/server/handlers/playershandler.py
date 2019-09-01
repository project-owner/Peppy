import os
import json

from util.config import SCREEN_INFO
from tornado.web import RequestHandler

class PlayersHandler(RequestHandler):
    def initialize(self, config_class):
        self.config_class = config_class

    def get(self):
        d = json.dumps(self.config_class.get_players())
        self.write(d)
        return

    def put(self):
        value = json.loads(self.request.body)
        try:
            self.config_class.save_players(value)
        except Exception as e:
            print(e)