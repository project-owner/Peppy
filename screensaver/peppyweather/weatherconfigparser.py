# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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
import codecs
import logging

from configparser import ConfigParser

WEATHER_CONFIG = "weather.config"
SCREEN_INFO = "screen.info"
WIDTH = "width"
HEIGHT = "height"
FRAME_RATE = "frame.rate"
UPDATE_PERIOD = "update.period"
USE_LOGGING = "use.logging"
BASE_PATH = "base.path"
CITY = "city"
CITY_LABEL = "city.label"
REGION = "region"
COUNTRY = "country"
UNIT = "unit"
DAY = "day"
CODE = "code"
MILITARY_TIME_FORMAT = "military.time.format"
DEGREE = "degree"
UNKNOWN = "?"
WEATHER_LABELS = "labels"
WEATHER_CONFIG_FILE = "weather-config.txt"
UTF8 = "utf8"
DEGREE_SYMBOL = "\u00B0"
NA_CODE = "3200"

HUMIDITY = "humidity"
WIND = "wind"
MPH = "mph"
SUNRISE = "sunrise"
SUNSET = "sunset"

SUNDAY = "sun"
MONDAY = "mon"
TUESDAY = "tue"
WEDNESDAY = "wed"
THURSDAY = "thu"
FRIDAY = "fri"
SATURDAY = "sat"

COLORS = "colors"
COLOR_DARK = "color.dark"
COLOR_DARK_LIGHT = "color.dark.light"
COLOR_MEDIUM = "color.medium"
COLOR_BRIGHT = "color.bright"
COLOR_CONTRAST = "color.contrast"

class WeatherConfigParser(object):
    """ Configuration file parser """
    
    def __init__(self, base_path):
        """ Initializer 
        
        :param base_path: base path
        """  
        self.weather_config = {BASE_PATH: base_path}
        c = ConfigParser()        
        
        for encoding in ["utf8", "utf-8-sig", "utf-16"]:
            try:
                path = os.path.join(base_path, WEATHER_CONFIG_FILE)
                c.read_file(codecs.open(path, "r", encoding))
                break
            except:
                pass
        
        self.weather_config[SCREEN_INFO] = {}
        self.weather_config[SCREEN_INFO][WIDTH] = c.getint(SCREEN_INFO, WIDTH)
        self.weather_config[SCREEN_INFO][HEIGHT] = c.getint(SCREEN_INFO, HEIGHT)        
        self.weather_config[SCREEN_INFO][FRAME_RATE] = c.getint(SCREEN_INFO, FRAME_RATE)
        
        self.weather_config[CITY] = c.get(WEATHER_CONFIG, CITY).strip()
        self.weather_config[CITY_LABEL] = c.get(WEATHER_CONFIG, CITY_LABEL)
        if len(self.weather_config[CITY_LABEL].strip()) == 0:
            self.weather_config[CITY_LABEL] = self.weather_config[CITY]
        self.weather_config[REGION] = c.get(WEATHER_CONFIG, REGION).strip()
        self.weather_config[COUNTRY] = c.get(WEATHER_CONFIG, COUNTRY).strip()
        self.weather_config[MILITARY_TIME_FORMAT] = c.getboolean(WEATHER_CONFIG, MILITARY_TIME_FORMAT)
        self.weather_config[UPDATE_PERIOD] = c.getfloat(WEATHER_CONFIG, UPDATE_PERIOD)
        self.weather_config[UNIT] = c.get(WEATHER_CONFIG, UNIT).strip()
        self.weather_config[USE_LOGGING] = c.getboolean(WEATHER_CONFIG, USE_LOGGING)
        
        self.weather_config[COLOR_DARK] = self.get_color_tuple(c.get(COLORS, COLOR_DARK))
        self.weather_config[COLOR_MEDIUM] = self.get_color_tuple(c.get(COLORS, COLOR_MEDIUM))
        self.weather_config[COLOR_DARK_LIGHT] = self.get_color_tuple(c.get(COLORS, COLOR_DARK_LIGHT))
        self.weather_config[COLOR_BRIGHT] = self.get_color_tuple(c.get(COLORS, COLOR_BRIGHT))
        self.weather_config[COLOR_CONTRAST] = self.get_color_tuple(c.get(COLORS, COLOR_CONTRAST))
        
        self.weather_config[DEGREE] = DEGREE_SYMBOL
        
        self.weather_config[SUNDAY] = c.get(WEATHER_LABELS, SUNDAY).strip()
        self.weather_config[MONDAY] = c.get(WEATHER_LABELS, MONDAY).strip()
        self.weather_config[TUESDAY] = c.get(WEATHER_LABELS, TUESDAY).strip()
        self.weather_config[WEDNESDAY] = c.get(WEATHER_LABELS, WEDNESDAY).strip()
        self.weather_config[THURSDAY] = c.get(WEATHER_LABELS, THURSDAY).strip()
        self.weather_config[FRIDAY] = c.get(WEATHER_LABELS, FRIDAY).strip()
        self.weather_config[SATURDAY] = c.get(WEATHER_LABELS, SATURDAY).strip()
        
        self.weather_config[HUMIDITY] = c.get(WEATHER_LABELS, HUMIDITY).strip()
        self.weather_config[WIND] = c.get(WEATHER_LABELS, WIND).strip()
        self.weather_config[MPH] = c.get(WEATHER_LABELS, MPH).strip()
        self.weather_config[SUNRISE] = c.get(WEATHER_LABELS, SUNRISE).strip()
        self.weather_config[SUNSET] = c.get(WEATHER_LABELS, SUNSET).strip()

        for n in range(48):
            k = str(n)
            self.weather_config[k] = c.get(WEATHER_LABELS, k)
        na = NA_CODE
        self.weather_config[na] = c.get(WEATHER_LABELS, na)

        
    def get_color_tuple(self, s):
        """ Convert string with comma separated colors into tuple with integer number for each color
        
        :param s: input string (e.g. "10, 20, 30" for RGB)        
        :return: tuple with colors (e.g. (10, 20, 30))
        """
        a = s.split(",")
        return tuple(int(e) for e in a)
    