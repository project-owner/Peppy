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

import pygame
import os
import random

from ui.container import Container
from ui.component import Component
from weatherutil import WeatherUtil, BLACK
from today import Today
from forecast import Forecast
from screensaver.screensaver import Screensaver, PLUGIN_CONFIGURATION
from itertools import cycle
from util.config import BACKGROUND, SCREEN_BGR_COLOR, COLORS, COLOR_DARK_LIGHT, CURRENT, LANGUAGE

SCREENSAVER = "screensaver"
WEATHER = "peppyweather"
FONT_SIZE = 18
CITY = "city"
LATITUDE = "latitude"
LONGITUDE = "longitude"
UNIT = "unit"
API_KEY = "api.key"
WEATHER_REFRESH_PERIOD = "weather.update.period"

class Peppyweather(Container, Screensaver):
    """ Main PeppyWeather class """
    
    def __init__(self, util=None):
        """ Initializer
        
        :param util: utility object
        """
        self.name = WEATHER
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, self.name, util, plugin_folder)
        self.ready = True

        self.city_label = self.plugin_config_file.get(PLUGIN_CONFIGURATION, CITY)
        self.latitude = self.plugin_config_file.get(PLUGIN_CONFIGURATION, LATITUDE)
        self.longitude = self.plugin_config_file.get(PLUGIN_CONFIGURATION, LONGITUDE)
        self.unit = self.plugin_config_file.get(PLUGIN_CONFIGURATION, UNIT)
        self.api_key = self.plugin_config_file.get(PLUGIN_CONFIGURATION, API_KEY)
        self.counter = 0

        try:
            weather_refresh_period = self.plugin_config_file.getint(PLUGIN_CONFIGURATION, WEATHER_REFRESH_PERIOD)
            self.weather_refresh_counter = int(weather_refresh_period / self.update_period)
        except:
            self.weather_refresh_counter = 0

        if not self.api_key:
            self.weather_refresh_counter = 0
            self.api_key = util.k3

        util.weather_config = {}

        self.config = None
        self.util = None
        self.set_util(util)
        self.rect = util.screen_rect
        self.util.weather_config["screen.rect"] = util.screen_rect

        self.images = []
        bgr = util.config[BACKGROUND][SCREEN_BGR_COLOR]
        bgr_count = util.image_util.get_background_count() - 1
        if bgr_count > 1:
            count = 4
        else:
            count = 1

        r = random.sample(range(0, bgr_count), count)

        br = 4
        for n in r:
            img = util.get_background(self.name + "." + str(n), bgr, index=n, blur_radius=br)
            self.images.append((img[3], img[2]))

        self.indexes = cycle(range(len(self.images)))
        Container.__init__(self, self.util, self.rect, BLACK)

    def set_util(self, util):
        """ Set utility object
        
        :param util: external utility object
        """
        self.config = util.config
        util.weather_config[LANGUAGE] = util.get_weather_language_code(util.config[CURRENT][LANGUAGE])
        path = os.path.join(os.getcwd(), SCREENSAVER, WEATHER)

        self.util = WeatherUtil(util, self.api_key, util.weather_config, self.config["labels"], self.unit, path)

        if not self.latitude and not self.longitude and not self.unit:
            self.ready = False
        
        self.util.pygame_screen = util.pygame_screen
        self.rect = util.screen_rect
        self.util.weather_config["screen.rect"] = self.rect
        self.util.get_font = util.get_font

    def set_weather(self, weather):
        """ Reads weather data and sets it in UI classes 
        
        :param weather: weather parameters
        """
        self.components.clear()
        
        try:
            dark_light = self.config[COLORS][COLOR_DARK_LIGHT]
        except:
            pass

        semi_transparent_color = (dark_light[0], dark_light[1], dark_light[2], 210)
        
        today_bgr = self.images[0]
        self.today = Today(self.util, today_bgr, semi_transparent_color, self.config[COLORS], self.config["labels"], self.city_label)
        self.today.set_weather(weather)
        self.today.draw_weather()
        self.today.set_visible(True)
        
        if len(self.images) > 1:
            forecast_bgr = self.images[1]
        else:
            forecast_bgr = self.images[0]
        self.forecast = Forecast(self.util, forecast_bgr, semi_transparent_color, self.config[COLORS])
        self.forecast.set_weather(weather)
        self.forecast.draw_weather()
        self.forecast.set_visible(False)
        
        self.add_component(self.today)
        self.add_component(self.forecast)

    def is_ready(self):
        """ Check if screensaver is ready """

        weather = self.util.load_json(self.latitude, self.longitude)
        if weather == None:
            self.ready = False
        else:
            self.ready = True
        
        return self.ready

    def start(self):
        """ Start PeppyWeather screensaver """
        
        weather = self.util.load_json(self.latitude, self.longitude)
        self.set_weather(weather)
        self.clean()
        self.draw()
        Component.update(self, self.bounding_box)
        pygame.event.clear()

    def update(self, area=None):
        """  Update screensaver """

        pass
    
    def refresh(self, init=False):
        """ Refresh PeppyWeather. Used to switch between Today and Forecast screens. 

        :param init: initial call
        """
        if init:
            return

        if self.weather_refresh_counter != 0:
            if self.counter == self.weather_refresh_counter:
                weather = self.util.load_json(self.latitude, self.longitude, force=True)
                self.set_weather(weather)
                self.counter = 0
            else:
                self.counter += 1

        i = next(self.indexes)
        image = self.images[i]
        
        if self.today.visible == True:
            self.today.set_visible(False)
            self.forecast.components[0].content = image
            self.forecast.set_visible(True)                       
        else:
            self.today.components[0].content = image
            self.today.set_visible(True)
            self.forecast.set_visible(False)
            
        self.clean()
        self.draw()
        return self.bounding_box
    