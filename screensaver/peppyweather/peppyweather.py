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
import sys
import time
import logging

from component import Component
from container import Container
from weatherutil import WeatherUtil, BLACK
from today import Today
from forecast import Forecast
from screensaverweather import ScreensaverWeather
from weatherconfigparser import WeatherConfigParser, SCREEN_INFO, WIDTH, HEIGHT, USE_LOGGING, \
    UPDATE_PERIOD, BASE_PATH, COLOR_DARK_LIGHT
from util.util import PACKAGE_SCREENSAVER
from itertools import cycle

SCREENSAVER = "screensaver"
WEATHER = "peppyweather"
FONT_SIZE = 18
DEFAULT_IMAGES_FOLDER = "images"

class Peppyweather(Container, ScreensaverWeather):
    """ Main PeppyWeather class """
    
    def __init__(self, util=None):
        """ Initializer
        
        :param util: utility object
        """
        ScreensaverWeather.__init__(self)
        self.config = None
        self.set_util(util)        
        self.update_period = self.util.weather_config[UPDATE_PERIOD]
        self.name = "peppyweather"
        
        if self.util.weather_config[USE_LOGGING]:
            logging.basicConfig(level=logging.NOTSET)            
        else:
            logging.disable(logging.CRITICAL)
            
        if self.config != None:
            self.rect = util.screen_rect
            self.util.weather_config["screen.rect"] = util.screen_rect
        else:
            self.init_display()
            self.rect = self.util.weather_config["screen.rect"]
        
        plugin_folder = type(self).__name__.lower() 
        images_folder = os.path.join(PACKAGE_SCREENSAVER, plugin_folder, DEFAULT_IMAGES_FOLDER)
        self.images = util.image_util.load_background_images(images_folder)
        self.indexes = cycle(range(len(self.images)))        
        
        Container.__init__(self, self.util, self.rect, BLACK)                
    
    def set_util(self, util):
        """ Set utility object
        
        :param util: external utility object
        """
        self.config = util.config
        self.util = WeatherUtil(util.k3, util.k4, util.k5)
        self.util.weather_config = util.weather_config
        path = os.path.join(os.getcwd(), SCREENSAVER, WEATHER)
        self.util.weather_config[BASE_PATH] = path
        self.util.pygame_screen = util.pygame_screen
        self.rect = util.screen_rect
        self.util.weather_config["screen.rect"] = self.rect
        self.util.get_font = util.get_font
            
    def init_display(self):
        """ Initialize display. Called if running stand-alone """
        
        screen_w = self.util.weather_config[SCREEN_INFO][WIDTH]
        screen_h = self.util.weather_config[SCREEN_INFO][HEIGHT]
        
        os.environ["SDL_FBDEV"] = "/dev/fb1"
        os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
        os.environ["SDL_MOUSEDRV"] = "TSLIB"
        
        if "win" not in sys.platform:
            pygame.display.init()
            pygame.mouse.set_visible(False)
        else:            
            pygame.init()
            pygame.display.set_caption("PeppyWeather")
            
        self.util.pygame_screen = pygame.display.set_mode((screen_w, screen_h))
        self.util.weather_config["screen.rect"] = pygame.Rect(0, 0, screen_w, screen_h)
    
    def set_weather(self):
        """ Reads weather data and sets it in UI classes """
        
        self.util.set_url()
        weather = self.util.load_json()
        self.components.clear()
        
        dark_light = self.util.weather_config[COLOR_DARK_LIGHT]
        semi_transparent_color = (dark_light[0], dark_light[1], dark_light[2], 210)
        
        self.today = Today(self.util, self.images[0], semi_transparent_color)
        self.today.set_weather(weather)
        self.today.draw_weather()
        self.today.set_visible(False)
        
        self.forecast = Forecast(self.util, self.images[1], semi_transparent_color)
        self.forecast.set_weather(weather)
        self.forecast.draw_weather()
        self.forecast.set_visible(True)
        
        self.add_component(self.today)
        self.add_component(self.forecast)
        
    def start(self):
        """ Start PeppyWeather screensaver """
        
        self.set_weather()
        self.clean_draw_update()        
        pygame.event.clear()        
    
    def start_standalone(self):
        """ Start PeppyWeather as a stand-alone app """
        
        self.start()
        count = 0
        delay = 0.2
        cycles = int(self.update_period / 0.2)       
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    keys = pygame.key.get_pressed() 
                    if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and event.key == pygame.K_c:
                        self.exit()
            
            count += 1
            
            if count >= cycles:
                self.refresh()
                count = 0
                                                                 
            time.sleep(0.2)
    
    def refresh(self):
        """ Refresh PeppyWeather. Used to switch between Today and Forecast screens. """
        
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
            
        self.clean_draw_update()
    
    def exit(self):
        """ Exit program """
        
        pygame.quit()            
        os._exit(0) 
       
if __name__ == "__main__":
    """ Used by stand-alone PeppyWeather """
    
    pw = Peppyweather()
    pw.start_standalone()
