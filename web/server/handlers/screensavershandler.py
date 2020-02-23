# Copyright 2019 Peppy Player peppy.player@gmail.com
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

from util.config import SCREEN_INFO
from tornado.web import RequestHandler
from configparser import ConfigParser
from screensaver.peppyweather.weatherconfigparser import WeatherConfigParser
from util.keys import UTF8

SCREENSAVER_FOLDER = "screensaver"
CONFIG_FILE = "screensaver-config.txt"
PLUGIN = "Plugin Configuration"
UPDATE = "update.period"

class ScreensaversHandler(RequestHandler):
    def initialize(self, config):
        self.config = config
        self.names = ["clock", "logo", "lyrics", "random", "slideshow"]

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
            "animated": file.getboolean(PLUGIN, "animated")
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
            "random": file.getboolean(PLUGIN, "random")
        }

        languages = self.config["languages"]
        weather = {}
        for lang in languages:
            path = os.path.join(os.getcwd(), "languages", lang["name"])
            parser = WeatherConfigParser(path)
            config = parser.weather_config
            short_config = {
                UPDATE: config[UPDATE],
                "city": config["city"],
                "city.label": config["city.label"],
                "region": config["region"],
                "country": config["country"],
                "unit": config["unit"],
                "military.time.format": config["military.time.format"],
                "use.logging": config["use.logging"]
            }
            weather[lang["name"]] = short_config
        savers["peppyweather"] = weather

        return savers

    def save_savers_config(self, new_savers_config):
        old_savers_config = self.load_savers_config()

        for name in self.names:
            if new_savers_config[name] != old_savers_config[name]:
                self.save_file(name, new_savers_config[name])

        old_weather = old_savers_config["peppyweather"]
        new_weather = new_savers_config["peppyweather"]
        languages = list(old_weather.keys())
        for language in languages:
            if new_weather[language] != old_weather[language]:
                self.save_weather_file(language, new_weather[language])

    def save_file(self, name, config):
        path = os.path.join(os.getcwd(), SCREENSAVER_FOLDER, name, CONFIG_FILE)
        config_parser = ConfigParser()
        config_parser.optionxform = str
        config_parser.read_file(codecs.open(path, "r", UTF8))

        keys = list(config.keys())
        for key in keys:
            param = config[key]
            config_parser.set(PLUGIN, key, str(param))

        with codecs.open(path, 'w', UTF8) as file:
            config_parser.write(file)

    def save_weather_file(self, language, config):
        path = os.path.join(os.getcwd(), "languages", language, "weather-config.txt")
        config_parser = ConfigParser()
        config_parser.optionxform = str
        config_parser.read_file(codecs.open(path, "r", UTF8))

        keys = list(config.keys())
        for key in keys:
            param = config[key]
            config_parser.set("weather.config", key, str(param))

        with codecs.open(path, 'w', UTF8) as file:
            config_parser.write(file)
