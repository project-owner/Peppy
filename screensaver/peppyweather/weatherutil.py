# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
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
import requests
import logging

from ui.component import Component
from datetime import datetime

LOCATION = "location"
WIND_LABEL = "wind"
WIND = "wnd"
ASTRONOMY = "astronomy"
CONDITION = "condition"
CHILL = "chill"
DIRECTION = "direction"
SPEED = "windSpeed"
TEMPERATURE = "temperature"
HUMIDITY = "humidity"
PRESSURE = "pressure"
PRESS = "press"
VISIBILITY = "visibility"
SUNRISE = "sunrise"
SUNSET = "sunset"
CODE = "code"
IMAGE_CODE = "weather_icon_name"
TEXT = "text"
DAY = "day"
HIGH = "high"
LOW = "low"
UNIT = "unit"
UNITS = "units"
ICONS_FOLDER = "icons"
CODE_UNKNOWN = "3200"
STATUS = "status"
DEG = "deg"
BLACK = (0, 0, 0)
DEGREE_SYMBOL = "\u00B0"
UNKNOWN = "?"
MPH = "mph"

GENERATED_IMAGE = "generated.img."

class WeatherUtil(object):
    """ Utility class """
    
    def __init__(self, util, app_key, weather_config, labels, unit, path):
        """ Initializer 
        
        :param app_key: OpenWeather API key
        :param weather_config: weather config object
        :param labels: labels
        :param unit: unit
        :param path: base path
        """
        self.util = util
        self.key = app_key
        self.weather_config = weather_config
        self.labels = labels
        self.base_path = path
        self.unit_config = unit

        if unit.lower() == "f":
            self.unit = "us" # imperial
        else:
            self.unit = "ca" # metric

        self.weather_json = None
        self.last_load_timestamp = None
        
    def load_json(self, latitude, longitude, force=False):
        """ Load weather json object from OpenWeather 
        
        :param latitude: latitude
        :param longitude: longitude
        :param force: enforce loading

        :return: weather object
        """
        if not latitude and not longitude:
            self.city = None
            return None

        now = datetime.now()

        if self.last_load_timestamp and not force:
            diff = now.minute - self.last_load_timestamp.minute 
            if diff <= 10:
                return self.weather

        self.weather = self.current_observation = self.forecasts = None
        try:
            url = f"https://api.pirateweather.net/forecast/{self.key}/{latitude},{longitude}?exclude=minutely,hourly,alerts&units={self.unit}"
            response = requests.get(url, timeout=(2, 2))
            if response == None:
                return None

            self.weather = response.json()
        except Exception as e:
            logging.debug(e)
            return None

        if self.weather and self.weather.get("currently") and self.weather.get("daily"):
            self.current_observation = self.weather.get("currently")
            self.forecasts = self.weather.get("daily")
        else:
            self.weather = None

        self.last_load_timestamp = now
        return self.weather
    
    def get_units(self):
        """ Get weather units
        
        :return: units
        """
        return self.unit_config.upper()
    
    def get_wind(self):
        """ Get wind section
        
        :return: wind section
        """
        return {
            SPEED: str(self.current_observation[SPEED]),
        }
    
    def get_atmosphere(self):
        """ Get atmosphere section
        
        :return: atmosphere section
        """
        return {
            HUMIDITY: str(self.current_observation[HUMIDITY])
        }
    
    def get_astronomy(self):
        """ Get astronomy section (sunrise/sunset)
        
        :return: astronomy section
        """
        astronomy = {
            # use forecst as there is no data for current
            SUNRISE: self.forecasts["data"][0]["sunriseTime"],
            SUNSET: self.forecasts["data"][0]["sunsetTime"]
        }
        return astronomy
    
    def get_condition(self):
        """ Get condition section
        
        :return: condition section
        """
        condition = {
            TEMPERATURE: self.get_temperature(self.current_observation[TEMPERATURE]),
            IMAGE_CODE: self.current_observation["icon"],
            STATUS: self.current_observation["summary"]
        }
        return condition
    
    def get_temperature(self, t):
        """ Create temperature string from the float number

        :param t: temperature as a float number

        :return: temperature as integre string
        """
        temp = str(t)

        index = temp.find(".")
        if index == -1:
            index = temp.find(",")    

        if index != -1:
            temp_current = temp[0 : index]
        else:
            temp_current = temp

        return temp_current

    def get_forecast(self):
        """ Get forecast section
        
        :return: forecast section
        """
        return self.forecasts
    
    def load_multi_color_svg_icon(self, folder,  image_name, bounding_box=None, scale=1.0):
        """ Load SVG image
        
        :param folder: icon folder
        :param image_name: svg image file name
        :param bounding_box: image bounding box
        
        :return: bitmap image rasterized from svg image
        """
        name = image_name + ".svg"
        path = os.path.join(self.base_path, folder, name)

        if not os.path.exists(path):
            path = os.path.join(self.base_path, folder, "unknown.svg")

        bounding_box.w /= scale
        bounding_box.h /= scale

        return self.util.image_util.load_multi_color_svg_icon(bounding_box=bounding_box, scale=scale, path=path)
    
    def get_text_width(self, text, fgr, font_height):
        """ Calculate text width
        
        :param text: text
        :param fgr: text color
        :param font_height: font height
        
        :return: text width
        """
        self.font = self.get_font(font_height)        
        size = self.font.size(text)
        label = self.font.render(text, 1, fgr)
        return label.get_size()[0]
        
    def get_text_component(self, text, fgr, font_height):
        """ Create text component using supplied parameters
        
        :param text: text
        :param fgr: text color
        :param font_height: font height
        
        :return: text component
        """
        self.font = self.get_font(font_height)        
        label = self.font.render(text, 1, fgr)
        comp = Component(self, label)
        comp.text = text
        comp.text_size = font_height
        comp.fgr = fgr
        return comp
    
    def draw_image(self, image, x, y, container, rect, name):
        """ Draw background defined by input parameters
        
        :param image: image to draw
        :param x: x coordinate
        :param y: y coordinate
        :param container: container to which image will be added
        :param rect: bounding box
        :param name: component name
        """
        c = Component(self)
        c.name = name
        c.content = image
        c.content_x = x
        c.content_y = y
        c.image_filename = c.name
        c.bounding_box = rect
        container.add_component(c)
        return c
    
    def get_weekday(self, ms):
        """ Get weekday from milliseconds
        
        :param ms: milliseconds
        
        :return: weekday
        """
        dt = datetime.fromtimestamp(ms)
        wd = dt.weekday()
        return self.labels["weekday." + str(wd)]
    
    def get_time(self, t):
        """ Get time
        
        :param t: time input string
        
        :return: formatted time
        """
        dt = datetime.fromtimestamp(t)
        return dt.strftime("%H") + ":" + dt.strftime("%M")
