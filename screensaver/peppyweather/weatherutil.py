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

from component import Component
from urllib import request
from weatherconfigparser import CITY, REGION, COUNTRY, UNIT, BASE_PATH, \
    MILITARY_TIME_FORMAT 

QUERY = "query"
RESULTS = "results"
CHANNEL = "channel"
LOCATION = "location"
WIND = "wind"
ATMOSPHERE = "atmosphere"
ASTRONOMY = "astronomy"
ITEM = "item"
CONDITION = "condition"
FORECAST = "forecast"
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
DATE = "date"
TEMP = "temp"
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
    
    def __init__(self):
        """ Initializer """

        self.image_cache = {}
        self.code_image_map = {}
        self.code_image_map[0] = "tornado.png"
        self.code_image_map[1] = "storm.png"
        self.code_image_map[2] = "hurricane.png"
        self.code_image_map[3] = "storm.png"
        self.code_image_map[4] = "storm.png"
        self.code_image_map[5] = "rain-snow.png"
        self.code_image_map[6] = "rain-snow.png"
        self.code_image_map[7] = "rain-snow.png"
        self.code_image_map[8] = "drizzle.png"
        self.code_image_map[9] = "drizzle.png"
        self.code_image_map[10] = "rain.png"
        self.code_image_map[11] = "drizzle.png"
        self.code_image_map[12] = "drizzle.png"
        self.code_image_map[13] = "snow.png"
        self.code_image_map[14] = "snow-showers.png"
        self.code_image_map[15] = "snow.png"
        self.code_image_map[16] = "snow.png"
        self.code_image_map[17] = "hail.png"
        self.code_image_map[18] = "rain-snow.png"
        self.code_image_map[19] = "dust.png"
        self.code_image_map[20] = "fog.png"
        self.code_image_map[21] = "fog.png"
        self.code_image_map[22] = "fog.png"
        self.code_image_map[23] = "blustery.png"
        self.code_image_map[24] = "windy.png"
        self.code_image_map[25] = "cold.png"
        self.code_image_map[26] = "cloudy.png"
        self.code_image_map[27] = "mostly-cloudy-night.png"
        self.code_image_map[28] = "mostly-cloudy-day.png"
        self.code_image_map[29] = "partly-cloudy-night.png"
        self.code_image_map[30] = "partly-cloudy-day.png"
        self.code_image_map[31] = "clear-night.png"
        self.code_image_map[32] = "sunny.png"
        self.code_image_map[33] = "fair-night.png"
        self.code_image_map[34] = "fair-day.png"
        self.code_image_map[35] = "rain-hail.png"
        self.code_image_map[36] = "hot.png"
        self.code_image_map[37] = "storm.png"
        self.code_image_map[38] = "storm.png"
        self.code_image_map[39] = "storm.png"
        self.code_image_map[40] = "drizzle.png"
        self.code_image_map[41] = "snow.png"
        self.code_image_map[42] = "snow-showers.png"
        self.code_image_map[43] = "snow.png"
        self.code_image_map[44] = "cloudy.png"
        self.code_image_map[45] = "storm.png"
        self.code_image_map[46] = "snow-showers.png"
        self.code_image_map[47] = "storm.png"
        self.code_image_map[3200] = "unknown.png"
        
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
        
        weather_url_prefix = "https://query.yahooapis.com/v1/public/yql?q=select* from weather.forecast where woeid in (select woeid from geo.places(1) where text='"
        weather_url_unit = "') and u='"
        weather_url_suffix = "'&format=json"
        
        self.url = weather_url_prefix + city + "," + region + country + weather_url_unit + unit + weather_url_suffix
        self.url.encode('ascii')
        self.url = self.url.replace(" ", "%20")
        
    def load_json(self):
        """ Load weather json object from Yahoo Weather """
        
        logging.debug("request: " + self.url)
        req = request.Request(self.url)
        site = request.urlopen(req)        
        charset = site.info().get_content_charset()
        html = site.read()
        response = None
        try:
            response = html.decode(charset)
        except:
            pass
        
        logging.debug("response: " + response)
        
        self.weather = None
        self.weather = json.loads(response)
        
        if self.weather and self.weather[QUERY] and self.weather[QUERY][RESULTS]:
            self.channel = self.weather[QUERY][RESULTS][CHANNEL]
            
        self.item = None
        try:
            self.item = self.channel[ITEM]
        except:
            self.weather = None
            
        return self.weather
    
    def get_units(self):
        """ Get weather units
        
        :return: units
        """
        return self.channel[UNITS]
    
    def get_location(self):
        """ Get location section
        
        :return: location section
        """
        return self.channel[LOCATION]
    
    def get_wind(self):
        """ Get wind section
        
        :return: wind section
        """
        return self.channel[WIND]
    
    def get_atmosphere(self):
        """ Get atmosphere section
        
        :return: atmosphere section
        """
        return self.channel[ATMOSPHERE]
    
    def get_astronomy(self):
        """ Get astronomy section (sunrise/sunset)
        
        :return: astronomy section
        """
        return self.channel[ASTRONOMY]
    
    def get_condition(self):
        """ Get condition section
        
        :return: condition section
        """
        return self.item[CONDITION]    
    
    def get_forecast(self):
        """ Get forecast section
        
        :return: forecast section
        """
        return self.item[FORECAST]        
    
    def load_pygame_image(self, path):
        """ Check if image is in the cache.
         
        If yes, return the image from the cache.
        If not load image file and place it in the cache.
        
        :param path: image path
        
        :return: pygame image
        """
        image = None
        try:
            i = self.image_cache[path]            
            return (path, i)
        except KeyError:
            pass
            
        try:            
            image = pygame.image.load(path).convert_alpha()
        except:
            pass
            
        if image:
            self.image_cache[path] = image
            return (path, image)
        else:
            return None
    
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
    
    def load_image(self, folder, image_name):
        """ Load image
        
        :param folder: folder name
        :param image_name: the image name
        """
        base_path = self.weather_config[BASE_PATH]
        path = os.path.join(base_path, folder,  image_name)        
        return self.load_pygame_image(path)
    
    def scale_image(self, image, ratio):
        """ Scale image using specified ratio
        
        :param image: input image
        :param ratio: scaling ratio  
              
        :return: scaled image
        """
        if image == None:
            return None
        a = pygame.Surface(ratio, flags=pygame.SRCALPHA)
        if isinstance(image, tuple):
            image = image[1]
        if image:
            pygame.transform.smoothscale(image, ratio, a)
            return a
        else:
            return None   
    
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
        
        d = d[0 : d.rfind(" ")]       
        current_time = time.strptime(d, '%a, %d %b %Y %I:%M %p')
        return time.strftime(self.TIME_FORMAT, current_time)
    
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
        
    
