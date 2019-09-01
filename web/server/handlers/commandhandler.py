import os
import json

from util.config import SCREEN_INFO
from tornado.web import RequestHandler
from configparser import ConfigParser

class CommandHandler(RequestHandler):
    def initialize(self, peppy):
        self.peppy = peppy

    def get(self, command):
        if command == "ping":
            d = json.dumps("success")
            self.write(d)
            return

    def post(self, command):
        if command == "reboot":
            self.reboot()
        elif command == "shutdown":
            self.shutdown()

    def reboot(self):
        self.peppy.reboot()

    def shutdown(self):
        self.peppy.shutdown()