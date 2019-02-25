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

import pygame
import os
import time
import json
import logging
import base64
import oauth2 as oauth
import requests

from random import randint
from component import Component
from weatherconfigparser import CITY, REGION, COUNTRY, UNIT, BASE_PATH, \
    MILITARY_TIME_FORMAT
from svg import Parser, Rasterizer

CURRENT_OBSERVATION = "current_observation"
LOCATION = "location"
WIND = "wind"
ATMOSPHERE = "atmosphere"
ASTRONOMY = "astronomy"
CONDITION = "condition"
FORECASTS = "forecasts"
CHILL = "chill"
DIRECTION = "direction"
SPEED = "speed"
TEMPERATURE = "temperature"
HUMIDITY = "humidity"
PRESSURE = "pressure"
VISIBILITY = "visibility"
SUNRISE = "sunrise"
SUNSET = "sunset"
CODE = "code"
DATE = "pubDate"
TEXT = "text"
DAY = "day"
HIGH = "high"
LOW = "low"
UNITS = "units"
ICONS_FOLDER = "icons"
CODE_UNKNOWN = "3200"
BLACK = (0, 0, 0)

class WeatherUtil(object):
    """ Utility class """
    
    def __init__(self, app_id, app_key, app_sec):
        """ Initializer 
        
        :param util: utility object
        """
        self.app_id = app_id
        self.app_key = app_key
        self.app_sec = app_sec
        self.image_cache = {}
        self.code_image_map = {}
        self.code_image_map[0] = "tornado.svg"
        self.code_image_map[1] = "storm.svg"
        self.code_image_map[2] = "hurricane.svg"
        self.code_image_map[3] = "storm.svg"
        self.code_image_map[4] = "storm.svg"
        self.code_image_map[5] = "rain-snow.svg"
        self.code_image_map[6] = "rain-snow.svg"
        self.code_image_map[7] = "rain-snow.svg"
        self.code_image_map[8] = "drizzle.svg"
        self.code_image_map[9] = "drizzle.svg"
        self.code_image_map[10] = "rain.svg"
        self.code_image_map[11] = "drizzle.svg"
        self.code_image_map[12] = "drizzle.svg"
        self.code_image_map[13] = "snow.svg"
        self.code_image_map[14] = "snow-showers.svg"
        self.code_image_map[15] = "snow.svg"
        self.code_image_map[16] = "snow.svg"
        self.code_image_map[17] = "hail.svg"
        self.code_image_map[18] = "rain-snow.svg"
        self.code_image_map[19] = "dust.svg"
        self.code_image_map[20] = "fog.svg"
        self.code_image_map[21] = "fog.svg"
        self.code_image_map[22] = "fog.svg"
        self.code_image_map[23] = "blustery.svg"
        self.code_image_map[24] = "windy.svg"
        self.code_image_map[25] = "cold.svg"
        self.code_image_map[26] = "cloudy.svg"
        self.code_image_map[27] = "mostly-cloudy-night.svg"
        self.code_image_map[28] = "mostly-cloudy-day.svg"
        self.code_image_map[29] = "partly-cloudy-night.svg"
        self.code_image_map[30] = "partly-cloudy-day.svg"
        self.code_image_map[31] = "clear-night.svg"
        self.code_image_map[32] = "sunny.svg"
        self.code_image_map[33] = "fair-night.svg"
        self.code_image_map[34] = "fair-day.svg"
        self.code_image_map[35] = "rain-hail.svg"
        self.code_image_map[36] = "hot.svg"
        self.code_image_map[37] = "storm.svg"
        self.code_image_map[38] = "storm.svg"
        self.code_image_map[39] = "storm.svg"
        self.code_image_map[40] = "drizzle.svg"
        self.code_image_map[41] = "snow.svg"
        self.code_image_map[42] = "snow-showers.svg"
        self.code_image_map[43] = "snow.svg"
        self.code_image_map[44] = "cloudy.svg"
        self.code_image_map[45] = "storm.svg"
        self.code_image_map[46] = "snow-showers.svg"
        self.code_image_map[47] = "storm.svg"
        self.code_image_map[3200] = "unknown.svg"
        
        self.weather_json = None
    
    def set_url(self):
        """ Set Yahoo Weather URL """
        
        weather_config = self.weather_config
        city = weather_config[CITY].lstrip().rstrip()
        region = weather_config[REGION].lstrip().rstrip()
        if region:
            region += ","
        country = weather_config[COUNTRY].lstrip().rstrip()
        unit = weather_config[UNIT].lstrip().rstrip()
        
        weather_url_prefix = "https://weather-ydn-yql.media.yahoo.com/forecastrss?location="
        weather_url_unit = "&u="
        weather_url_suffix = "'&format=json"
        
        self.url = weather_url_prefix + city + "," + region + country + "&u=" + unit + "&format=json"
        self.url.encode('ascii')
        self.url = self.url.replace(" ", "%20")
    
    def load_json(self):
        """ Load weather json object from Yahoo Weather """
        
        header = {
            "Yahoo-App-Id": self.app_id,
            "Authorization": "OAuth",
            "oauth_consumer_key": self.app_key,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": oauth.generate_nonce(),
            "oauth_version": "1.0"
        }
        
        req = oauth.Request(method="GET", url=self.url, parameters=header)
        consumer = oauth.Consumer(key=self.app_key, secret=self.app_sec)
        signature = oauth.SignatureMethod_HMAC_SHA1().sign(req, consumer, None)
        req["oauth_signature"] = signature
        
        logging.debug("request url: " + self.url)
        response = None
        html = None
        
        try:
            site = requests.get(req.to_url())
            html = site.content
        except:
            pass
        
        if html == None:
            self.item = None
            return None
        
        try:
            response = html.decode("utf-8")
        except:
            pass
        
        self.weather = self.current_observation = self.forecasts = None
        self.weather = json.loads(response)        
        
        if self.weather and self.weather[CURRENT_OBSERVATION] and self.weather[FORECASTS]:
            self.current_observation = self.weather[CURRENT_OBSERVATION]
            self.forecasts = self.weather[FORECASTS]
        else:
            self.weather = None
            
        return self.weather
    
    def get_units(self):
        """ Get weather units
        
        :return: units
        """
        return self.weather_config[UNIT].upper()
    
    def get_location(self):
        """ Get location section
        
        :return: location section
        """
        return self.weather[LOCATION]
    
    def get_wind(self):
        """ Get wind section
        
        :return: wind section
        """
        return self.current_observation[WIND]
    
    def get_atmosphere(self):
        """ Get atmosphere section
        
        :return: atmosphere section
        """
        return self.current_observation[ATMOSPHERE]
    
    def get_astronomy(self):
        """ Get astronomy section (sunrise/sunset)
        
        :return: astronomy section
        """
        return self.current_observation[ASTRONOMY]
    
    def get_condition(self):
        """ Get condition section
        
        :return: condition section
        """
        return self.current_observation[CONDITION]    
    
    def get_forecast(self):
        """ Get forecast section
        
        :return: forecast section
        """
        return self.forecasts
    
    def load_svg_icon(self, folder,  image_name, bounding_box=None):
        """ Load SVG image
        
        :param folder: icon folder
        :param image_name: svg image file name
        :param bounding_box: image bounding box
        
        :return: bitmap image rasterized from svg image
        """
        base_path = self.weather_config[BASE_PATH]
        path = os.path.join(base_path, folder,  image_name)        
        cache_path = path + "." + str(bounding_box.w) + "." + str(bounding_box.h)
        
        try:
            i = self.image_cache[cache_path]
            return (cache_path, i)
        except KeyError:
            pass
        
        try:
            svg_image = Parser.parse_file(path)
        except:
            logging.debug("Problem parsing file %s", path)
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
        size = self.font.size(text)
        label = self.font.render(text, 1, fgr)
        comp = Component(self, label)
        comp.text = text
        comp.text_size = font_height
        comp.fgr = fgr
        return comp
    
    def draw_image(self, image, x, y, container, rect=None):
        """ Draw background defined by input parameters
        
        :param image: image to draw
        :param x: x coordinate
        :param y: y coordinate
        :param container: container to which image will be added
        :param rect: bounding box
        """
        c = Component(self)
        c.content = image
        c.content_x = x
        c.content_y = y
        if rect: c.bounding_box = rect
        container.add_component(c)
        return c
    
    def get_time_from_date(self, d):
        """ Get time from supplied date string
        
        :param d: date string
        
        :return: time
        """
        military_time_format = self.weather_config[MILITARY_TIME_FORMAT]
        if military_time_format:
            self.TIME_FORMAT = "%H:%M"
        else:
            self.TIME_FORMAT = "%I:%M %p"
        
        return d.strftime(self.TIME_FORMAT)
    
    def get_time(self, t):
        """ Get time
        
        :param t: time input string
        
        :return: formatted time
        """
        military_time_format = self.weather_config[MILITARY_TIME_FORMAT]
        c = t.find(":")
        i = t.find(" ")
        h = t[0 : c].strip()
        m = t[c + 1 : i].strip()
        p = t[i:].strip()
        
        if military_time_format:
            if p == "pm":
                if h == "12":
                    h = "12"
                else:
                    h = str(int(h) + 12)
            else:
                if h == "12":
                    h = "00"
                
            if len(h) == 1:
                h = "0" + h
            return h + ":" + m
        else:
            return t.upper()
        
    
