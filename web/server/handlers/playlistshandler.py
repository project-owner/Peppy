import os
import json

from util.config import SCREEN_INFO
from tornado.web import RequestHandler
from configparser import ConfigParser

class PlaylistsHandler(RequestHandler):
    def initialize(self, util):
        self.util = util

    def get(self):
        language = self.get_argument("language", None)
        genre = self.get_argument("genre", None)
        folder = self.get_argument("folder", None)

        playlist = self.util.load_radio_playlist(language, genre, folder)
        d = json.dumps(playlist)
        self.write(d)
        return

    def put(self):
        value = json.loads(self.request.body)
        languages = list(value.keys())
        for language in languages:
            genres = list(value[language].keys())
            for genre in genres:
                self.util.save_radio_playlist(language, genre, value[language][genre])