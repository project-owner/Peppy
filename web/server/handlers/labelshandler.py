import os
import json

from util.config import SCREEN_INFO
from tornado.web import RequestHandler
from configparser import ConfigParser

class LabelsHandler(RequestHandler):
    def initialize(self, util):
        self.util = util

    def get(self):
        language = self.get_argument("language", None)
        labels = self.util.get_labels_by_language(language)
        d = json.dumps(labels)
        self.write(d)
        return
