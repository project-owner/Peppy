# Copyright 2019-2021 Peppy Player peppy.player@gmail.com
# 
# This file is part of Peppy Player.
# 
# Peppy Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Peppy Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Peppy Player. If not, see <http://www.gnu.org/licenses/>.

import os
import json
import codecs
import logging

from tornado.web import RequestHandler
from configparser import ConfigParser
from util.keys import UTF8

SCREENSAVER_FOLDER = "screensaver"
CONFIG_FILE = "screensaver-config.txt"
PLUGIN = "Plugin Configuration"
UPDATE = "update.period"

class ScreensaversHandler(RequestHandler):
    def initialize(self, config):
        self.config = config
        self.names = ["clock", "logo", "lyrics", "random", "slideshow", "peppyweather"]

    def get(self):
        d = json.dumps(self.load_savers_config())
        self.write(d)
        return

    def put(self):
        value = json.loads(self.request.body)
        try:
            self.save_savers_config(value)
        except Exception as e:
            print(e)

    def load_savers_config(self):
        file = ConfigParser()

        path = os.path.join(os.getcwd(), SCREENSAVER_FOLDER, "clock", CONFIG_FILE)
        file.read(path)

        savers = { "clock": {
            UPDATE: file.getint(PLUGIN, UPDATE),
            "military.time.format": file.getboolean(PLUGIN, "military.time.format"),
            "animated": file.getboolean(PLUGIN, "animated"),
            "clock.size": file.getint(PLUGIN, "clock.size")
        }}

        path = os.path.join(os.getcwd(), SCREENSAVER_FOLDER, "logo", CONFIG_FILE)
        file.read(path)
        savers["logo"] = {
            UPDATE: file.getint(PLUGIN, UPDATE),
            "vertical.size.percent": file.getint(PLUGIN, "vertical.size.percent")
        }

        path = os.path.join(os.getcwd(), SCREENSAVER_FOLDER, "lyrics", CONFIG_FILE)
        file.read(path)
        savers["lyrics"] = {
            UPDATE: file.getint(PLUGIN, UPDATE)
        }

        path = os.path.join(os.getcwd(), SCREENSAVER_FOLDER, "random", CONFIG_FILE)
        file.read(path)
        savers["random"] = {
            UPDATE: file.getint(PLUGIN, UPDATE),
            "savers": file.get(PLUGIN, "savers")
        }

        path = os.path.join(os.getcwd(), SCREENSAVER_FOLDER, "slideshow", CONFIG_FILE)
        file.read(path)
        savers["slideshow"] = {
            UPDATE: file.getint(PLUGIN, UPDATE),
            "slides.folder": file.get(PLUGIN, "slides.folder"),
            "random": file.getboolean(PLUGIN, "random"),
            "use.cache": file.getboolean(PLUGIN, "use.cache")
        }

        path = os.path.join(os.getcwd(), SCREENSAVER_FOLDER, "peppyweather", CONFIG_FILE)
        file = ConfigParser()
        self.read_config_file(file, path)

        try:
            weather_update_period = file.getint(PLUGIN, "weather.update.period")
        except:
            weather_update_period = ""

        savers["peppyweather"] = {
            "city": file.get(PLUGIN, "city"),
            "latitude": file.get(PLUGIN, "latitude"),
            "longitude": file.get(PLUGIN, "longitude"),
            "unit": file.get(PLUGIN, "unit"),
            UPDATE: file.getint(PLUGIN, UPDATE),
            "api.key": file.get(PLUGIN, "api.key"),
            "weather.update.period": weather_update_period
        }

        return savers

    def save_savers_config(self, new_savers_config):
        old_savers_config = self.load_savers_config()

        for name in self.names:
            if new_savers_config[name] != old_savers_config[name]:
                self.save_file(name, new_savers_config[name])

    def save_file(self, name, config):
        path = os.path.join(os.getcwd(), SCREENSAVER_FOLDER, name, CONFIG_FILE)
        config_parser = ConfigParser()
        config_parser.optionxform = str
        self.read_config_file(config_parser, path)

        keys = list(config.keys())
        for key in keys:
            param = config[key]
            config_parser.set(PLUGIN, key, str(param))

        with codecs.open(path, 'w', UTF8) as file:
            config_parser.write(file)

    def read_config_file(self, config_parser, path):
        for encoding in ["utf8", "utf-8-sig", "utf-16"]:
            try:
                config_parser.read_file(codecs.open(path, "r", encoding))
                break
            except Exception as e:
                logging.error(e)
