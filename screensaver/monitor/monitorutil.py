# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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

import pygame
import os

from ui.component import Component
from svg import Parser, Rasterizer
from pyowm import OWM
from pyowm.utils.config import get_default_config
from datetime import datetime

LOCATION = "location"
WIND_LABEL = "wind"
WIND = "wnd"
ASTRONOMY = "astronomy"
CONDITION = "condition"
CHILL = "chill"
DIRECTION = "direction"
SPEED = "speed"
TEMPERATURE = "temp"
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
    
    def __init__(self, app_key, weather_config, labels, unit, path):
        """ Initializer 
        
        :param app_key: OpenWeather API key
        :param weather_config: weather config object
        :param labels: labels
        :param unit: unit
        :param path: base path
        """
        self.app_key = app_key
        self.weather_config = weather_config
        self.labels = labels
        self.base_path = path
        self.unit_config = unit
        
        config_dict = get_default_config()
        config_dict['language'] = weather_config["language"]
        owm = OWM(app_key, config_dict)
        self.weather_manager = owm.weather_manager()

        if unit.lower() == "f":
            self.unit = "imperial"
        else:
            self.unit = "metric"

        self.image_cache = {}
        self.code_image_map = {}
        self.code_image_map["01d"] = "01d.svg"
        self.code_image_map["01n"] = "01n.svg"
        self.code_image_map["02d"] = "02d.svg"
        self.code_image_map["02n"] = "02n.svg"
        self.code_image_map["03d"] = "03d.svg"
        self.code_image_map["03n"] = "03n.svg"
        self.code_image_map["04d"] = "04d.svg"
        self.code_image_map["04n"] = "04n.svg"
        self.code_image_map["09d"] = "09d.svg"
        self.code_image_map["09n"] = "09n.svg"
        self.code_image_map["10d"] = "10d.svg"
        self.code_image_map["10n"] = "10n.svg"
        self.code_image_map["11d"] = "11d.svg"
        self.code_image_map["11n"] = "11n.svg"
        self.code_image_map["13d"] = "13d.svg"
        self.code_image_map["13n"] = "13n.svg"
        self.code_image_map["50d"] = "50d.svg"
        self.code_image_map["50n"] = "50n.svg"
        
        self.weather_json = None
        self.last_load_timestamp = None
        
    def load_json(self, latitude, longitude, force=False):
        """ Load weather json object from OpenWeather 
        
        :param latitude: latitude
        :param longitude: longitude
        :param force: enforce loading

        :return: weather object
        """
        self.weather = None
        return self.weather

        # if not latitude and not longitude:
        #     self.city = None
        #     return None

        # now = datetime.now()

        # if self.last_load_timestamp and not force:
        #     diff = now.minute - self.last_load_timestamp.minute 
        #     if diff <= 10:
        #         return self.weather

        # self.weather = self.current_observation = self.forecasts = None
        # try:
        #     self.weather = self.weather_manager.one_call(lat=float(latitude), lon=float(longitude), exclude='minutely,hourly,alerts', units=self.unit)
        # except:
        #     return None

        # if self.weather and self.weather.current and self.weather.forecast_daily:
        #     self.current_observation = self.weather.current
        #     self.forecasts = self.weather.forecast_daily
        # else:
        #     self.weather = None

        # self.last_load_timestamp = now
        # return self.weather
    
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
            SPEED: str(self.current_observation.wnd[SPEED]),
        }
    
    def get_atmosphere(self):
        """ Get atmosphere section
        
        :return: atmosphere section
        """
        return {
            HUMIDITY: str(self.current_observation.humidity)
        }
    
    def get_astronomy(self):
        """ Get astronomy section (sunrise/sunset)
        
        :return: astronomy section
        """
        astronomy = {
            SUNRISE: self.current_observation.srise_time,
            SUNSET: self.current_observation.sset_time
        }
        return astronomy
    
    def get_condition(self):
        """ Get condition section
        
        :return: condition section
        """
        condition = {
            TEMPERATURE: self.get_temperature(self.current_observation.temp[TEMPERATURE]),
            IMAGE_CODE: self.current_observation.weather_icon_name,
            STATUS: self.current_observation.detailed_status.capitalize()
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
    
    def load_multi_color_svg_icon(self, folder,  image_name, bounding_box=None):
        """ Load SVG image
        
        :param folder: icon folder
        :param image_name: svg image file name
        :param bounding_box: image bounding box
        
        :return: bitmap image rasterized from svg image
        """
        if image_name == None: return None
        name = self.code_image_map[image_name]
        path = os.path.join(self.base_path, folder, name)        
        cache_path = path + "." + str(bounding_box.w) + "." + str(bounding_box.h)
        
        try:
            i = self.image_cache[cache_path]
            return (cache_path, i)
        except KeyError:
            pass
        
        try:
            svg_image = Parser.parse_file(path)
        except:
            return None
        
        w = svg_image.width + 2
        h = svg_image.height + 2        
        k_w = bounding_box.w / w
        k_h = bounding_box.h / h
        scale_factor = min(k_w, k_h)
        w_final = int(w * scale_factor)
        h_final = int(h * scale_factor)
        
        r = Rasterizer()        
        buff = r.rasterize(svg_image, w_final, h_final, scale_factor)    
        image = pygame.image.frombuffer(buff, (w_final, h_final), 'RGBA')
        
        self.image_cache[cache_path] = image 
        
        return (cache_path, image)
    
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
