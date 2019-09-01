import os
import json

from util.config import SCREEN_INFO
from tornado.web import RequestHandler

class ParametersHandler(RequestHandler):
    def initialize(self, config_class):
        self.config = config_class.load_config_parameters()
        self.config_class = config_class

    def get(self):
        section = self.get_argument("section", None)
        if section == None:
            d = json.dumps(self.config)
            self.write(d)
            return
        try:
            self.config[section]
        except:
            self.set_status(400)
            return self.finish("Wrong Section Name")

        property = self.get_argument("property", None)
        if property != None:
            try:
                self.config[section][property]
            except:
                self.set_status(400)
                return self.finish("Wrong Property Name")
            self.write(json.dumps(self.config[section][property]))
        else:
            self.write(json.dumps(self.config[section]))

    def put(self):
        value = json.loads(self.request.body)
        try:
            self.config_class.save_config_parameters(value)
        except Exception as e:
            print(e)
