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
import pygame
import math

from component import Component
from container import Container
from weatherconfigparser import SCREEN_RECT, COLOR_DARK, COLOR_MEDIUM, COLOR_CONTRAST, \
    COLOR_BRIGHT, COLOR_DARK_LIGHT, CODE, DAY, DEGREE, UNKNOWN
from weatherutil import HIGH, CODE_UNKNOWN, ICONS_FOLDER, BLACK

TILE_HEADER_HEIGHT = 25
DAY_HEIGHT = 60
ICON_HEIGHT = 46

class Forecast(Container):
    """ This class draws 6 days weather forecast  """
    
    def __init__(self, util, image, semi_transparent_color):
        """ Initializer
        
        :param util: utility object
        :param image: initial image
        :param semi_transparent_color: semi-transparent background color
        """
        self.util = util
        self.weather_config = util.weather_config
        self.initial_image = image
        
        if getattr(util, "config", None):
            self.config = util.config
            self.rect = self.config[SCREEN_RECT]
        else:
            self.rect = self.util.weather_config[SCREEN_RECT]
        
        self.degree = self.weather_config[DEGREE]
        self.semi_transparent_color = semi_transparent_color

    def set_weather(self, weather):
        """ Set weather object which has all forecast data
        
        :param weather: forecast object
        """
        if weather == None:
            self.forecast = []
            day = {DAY: UNKNOWN, CODE: CODE_UNKNOWN, HIGH: UNKNOWN}
            for d in range(6):                
                self.forecast.append(day) 
        else:
            self.forecast = self.util.get_forecast()[1: -3]

    def draw_weather(self):
        """ Draw weather forecast  """
        
        c = self.util.weather_config[COLOR_DARK]
        Container.__init__(self, self.util, self.rect, BLACK)
        
        c = Component(self.util)
        c.content = self.initial_image
        c.content_x = 0
        c.content_y = 0
        c.bounding_box = self.rect
        self.add_component(c)  
        
        widths = self.get_widths()
        heights = self.get_heights()
        
        self.draw_tiles(widths, heights)
        
    def draw_tiles(self, widths, heights):
        """ Draw six tiles for the forecast
        
        :param widths: array of 6 tiles widths
        :param heights: array of 6 tiles heights
        """        
        for r in range(len(heights)):
            for c in range(len(widths)):
                comp = Component(self.util)
                x = 1 + c + (c * widths[c - 1])
                y = 1 + r + (r * heights[r - 1])
                w = widths[c]
                h = heights[r]
                fcast = self.forecast[r * len(widths) + c]
                self.draw_tile(x, y, w, h, fcast)
                
                if c == 0 or c == 1:
                    self.draw_separator(x, y, w, h)
    
    def draw_separator(self, x, y, w, h):
        """ Draw tile separator
        
        :param x: tile x coordinate
        :param y: tile y coordinate
        :param w: tile width
        :param h: tile height
        """
        height = (h / 100) * TILE_HEADER_HEIGHT
        comp = Component(self.util)
        rect = pygame.Rect(x + w, y + height, 1, h - height + 2)
        comp.content = rect
        comp.fgr = self.util.weather_config[COLOR_DARK_LIGHT]
        comp.bgr = self.util.weather_config[COLOR_DARK_LIGHT]
        comp.bounding_box = rect
        self.add_component(comp)               
    
    def draw_tile(self, x, y, w, h, fcast):
        """ Draw single tile for one day forecast   
        
        :param x: tile x coordinate
        :param y: tile y coordinate
        :param w: tile width
        :param h: tile height
        :param fcast: one day forecast
        """
        self.draw_tile_header(x, y, w, h, fcast)
        self.draw_tile_icon(x, y, w, h, fcast)
        self.draw_temp(x, y, w, h, fcast)
        
    def draw_tile_icon(self, x, y, w, h, fcast):
        """ Draw weather icon
        
        :param x: tile x coordinate
        :param y: tile y coordinate
        :param w: tile width
        :param h: tile height
        :param fcast: one day forecast
        """
        code_image = self.util.code_image_map[int(fcast[CODE])]
        image_w = image_h = int((w / 100) * ICON_HEIGHT) 
        top_height = (h / 100) * TILE_HEADER_HEIGHT
        
        bb = pygame.Rect(0, 0, image_w, image_h)
        img = self.util.load_svg_icon(ICONS_FOLDER, code_image, bb)
        bb = img[1].get_rect()
        
        origin_x = x + (image_w - bb.w) / 2
        origin_y = y + top_height + (image_w - bb.h) / 2
        
        bb.x = origin_x
        bb.y = origin_y
        self.util.draw_image(img[1], origin_x, origin_y, self, bb)
    
    def draw_temp(self, x, y, w, h, fcast):
        """ Draw temperature
        
        :param x: tile x coordinate
        :param y: tile y coordinate
        :param w: tile width
        :param h: tile height
        :param fcast: one day forecast
        """
        top_height = (h / 100) * TILE_HEADER_HEIGHT
        bb_y = y + top_height + top_height / 1.5
        bb_w = w
        bb_h = h - top_height  
        
        font_size = int((bb_h / 100) * 50)
        front_color = self.util.weather_config[COLOR_CONTRAST]
        
        c = self.util.get_text_component(str(fcast[HIGH]) + self.degree, front_color, font_size)
        
        c.content_x = x + w - c.content.get_size()[0]
        c.content_y = bb_y + int((bb_h - c.content.get_size()[1]) / 2) + 6
        self.add_component(c)
                
    def draw_tile_header(self, x, y, w, h, fcast):
        """ Draw tile header
        
        :param x: tile x coordinate
        :param y: tile y coordinate
        :param w: tile width
        :param h: tile height
        :param fcast: one day forecast
        """
        height = (h / 100) * TILE_HEADER_HEIGHT
        comp = Component(self.util)
        comp.content_x = x
        comp.content_y = y
        rect = pygame.Rect(x, y, w, height)
        comp.content = rect
        comp.fgr = self.semi_transparent_color
        comp.bgr = self.semi_transparent_color
        comp.bounding_box = rect
        self.add_component(comp)
        
        text_color = self.util.weather_config[COLOR_BRIGHT]
        font_size = int((height / 100) * DAY_HEIGHT)
        
        if fcast[DAY] == UNKNOWN:
            d = UNKNOWN
        else:
            d = self.weather_config[fcast[DAY].lower()]
            
        c = self.util.get_text_component(d, text_color, font_size)
        c.content_x = x + (w - c.content.get_size()[0]) / 2
        c.content_y = y + font_size / 8
        self.add_component(c)
        
    def draw_tile_body(self, x, y, w, h, fcast):
        """ Draw center part of the tile
        
        :param x: tile x coordinate
        :param y: tile y coordinate
        :param w: tile width
        :param h: tile height
        :param fcast: one day forecast
        """
        top_height = (h / 100) * TILE_HEADER_HEIGHT
        y += top_height
        h = h - top_height + 1
        comp = Component(self.util)
        comp.content_x = x
        comp.content_y = y
        rect = pygame.Rect(x, y, w, h)
        comp.content = rect
        comp.fgr = self.util.weather_config[COLOR_BRIGHT]
        comp.bgr = self.util.weather_config[COLOR_BRIGHT]
        comp.bounding_box = rect
        self.add_component(comp)
    
    def get_widths(self):
        """ Calculate tiles widths """
        
        cols = 3
        widths = []
        rw = self.rect.w
        w = rw - (cols + 1)        
        r = w % cols
        width = math.floor(w / cols)
        
        for n in range(cols):
            if r:
                if n == cols - 1:
                    widths.append(rw - (width * n) - (cols + 1))
                else:
                    widths.append(width)
            else:
                widths.append(width)
        
        return widths
    
    def get_heights(self):
        """ Calculate tiles heights """
        
        rows = 2
        heights = []
        rh = self.rect.h
        h = rh - (rows + 1)        
        rr = h % rows
        height = math.floor(h / rows)
        
        for n in range(rows):
            if rr:
                if n == rows - 1:
                    heights.append(rh - (height * n) - (rows + 1))
                else:
                    heights.append(height)
            else:
                heights.append(height)
        
        return heights
