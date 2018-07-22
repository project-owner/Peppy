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
from weatherconfigparser import WeatherConfigParser, SCREEN_INFO, WIDTH, HEIGHT, DEPTH, USE_LOGGING, \
    PYGAME_SCREEN, SCREEN_RECT, UPDATE_PERIOD, BASE_PATH

SCREENSAVER = "screensaver"
WEATHER = "peppyweather"
FONT_SIZE = 18

class Peppyweather(Container, ScreensaverWeather):
    """ Main PeppyWeather class """
    
    def __init__(self, util=None):
        """ Initializer
        
        :param util: utility object
        """
        ScreensaverWeather.__init__(self)
        self.config = None
        if util:            
            self.set_util(util)
        else:
            self.util = WeatherUtil()
            base_path = "."
            parser = WeatherConfigParser(base_path)
            self.util.weather_config = parser.weather_config
        
        self.update_period = self.util.weather_config[UPDATE_PERIOD]
        
        if self.util.weather_config[USE_LOGGING]:
            logging.basicConfig(level=logging.NOTSET)            
        else:
            logging.disable(logging.CRITICAL)
            
        if self.config != None:
            self.rect = self.config[SCREEN_RECT]
            self.util.weather_config[SCREEN_RECT] = self.rect
        else:
            self.init_display()
            self.rect = self.util.weather_config[SCREEN_RECT]
        
        Container.__init__(self, self.util, self.rect, BLACK)                
    
    def set_util(self, util):
        """ Set utility object
        
        :param util: external utility object
        """
        self.config = util.config
        self.util = WeatherUtil()
        self.util.weather_config = util.weather_config
        path = os.path.join(os.getcwd(), SCREENSAVER, WEATHER)
        self.util.weather_config[BASE_PATH] = path
        self.util.PYGAME_SCREEN = util.PYGAME_SCREEN
        self.rect = self.config[SCREEN_RECT]
        self.util.weather_config[SCREEN_RECT] = self.rect
        self.util.get_font = util.get_font
            
    def init_display(self):
        """ Initialize display. Called if running stand-alone """
        
        screen_w = self.util.weather_config[SCREEN_INFO][WIDTH]
        screen_h = self.util.weather_config[SCREEN_INFO][HEIGHT]
        depth = self.util.weather_config[SCREEN_INFO][DEPTH]
        
        os.environ["SDL_FBDEV"] = "/dev/fb1"
        os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
        os.environ["SDL_MOUSEDRV"] = "TSLIB"
        
        if "win" not in sys.platform:
            pygame.display.init()
            pygame.mouse.set_visible(False)
        else:            
            pygame.init()
            pygame.display.set_caption("PeppyWeather")
            
        self.util.PYGAME_SCREEN = pygame.display.set_mode((screen_w, screen_h), pygame.DOUBLEBUF, depth)        
        self.util.weather_config[SCREEN_RECT] = pygame.Rect(0, 0, screen_w, screen_h)
    
    def set_weather(self):
        """ Reads weather data and sets it in UI classes """
        
        self.util.set_url()
        weather = self.util.load_json()

        self.today = Today(self.util)
        self.today.set_weather(weather)
        self.today.draw_weather()
        self.today.set_visible(False)
        
        self.forecast = Forecast(self.util)
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
        
        if self.today.visible == True:
            self.today.set_visible(False)
            self.forecast.set_visible(True)                        
        else:
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
