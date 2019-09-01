import os
import json
import codecs

from util.config import SCREEN_INFO
from tornado.web import RequestHandler
from configparser import ConfigParser
from screensaver.peppyweather.weatherconfigparser import WeatherConfigParser
from util.keys import UTF8

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

        path = os.path.join(os.getcwd(), "screensaver", "clock", "screensaver-config.txt")
        file.read(path)
        savers = { "clock": {
            "update.period": file.getint("Plugin Configuration", "update.period"),
            "military.time.format": file.getboolean("Plugin Configuration", "military.time.format"),
            "animated": file.getboolean("Plugin Configuration", "animated")
        }}

        path = os.path.join(os.getcwd(), "screensaver", "logo", "screensaver-config.txt")
        file.read(path)
        savers["logo"] = {
            "update.period": file.getint("Plugin Configuration", "update.period"),
            "vertical.size.percent": file.getint("Plugin Configuration", "vertical.size.percent")
        }

        path = os.path.join(os.getcwd(), "screensaver", "lyrics", "screensaver-config.txt")
        file.read(path)
        savers["lyrics"] = {
            "update.period": file.getint("Plugin Configuration", "update.period")
        }

        path = os.path.join(os.getcwd(), "screensaver", "random", "screensaver-config.txt")
        file.read(path)
        savers["random"] = {
            "update.period": file.getint("Plugin Configuration", "update.period"),
            "savers": file.get("Plugin Configuration", "savers")
        }

        path = os.path.join(os.getcwd(), "screensaver", "slideshow", "screensaver-config.txt")
        file.read(path)
        savers["slideshow"] = {
            "update.period": file.getint("Plugin Configuration", "update.period"),
            "slides.folder": file.get("Plugin Configuration", "slides.folder")
        }

        languages = self.config["languages"]
        weather = {}
        for lang in languages:
            path = os.path.join(os.getcwd(), "languages", lang["name"])
            parser = WeatherConfigParser(path)
            config = parser.weather_config
            short_config = {
                "update.period": config["update.period"],
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
        path = os.path.join(os.getcwd(), "screensaver", name, "screensaver-config.txt")
        config_parser = ConfigParser()
        config_parser.optionxform = str
        config_parser.read_file(codecs.open(path, "r", UTF8))

        keys = list(config.keys())
        for key in keys:
            param = config[key]
            config_parser.set("Plugin Configuration", key, str(param))

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
