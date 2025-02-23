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
import math

from ui.component import Component
from ui.container import Container
from weatherutil import HIGH, CODE_UNKNOWN, ICONS_FOLDER, BLACK, GENERATED_IMAGE, DEGREE_SYMBOL, UNKNOWN, DAY, CODE
from util.config import COLOR_CONTRAST, COLOR_BRIGHT, COLOR_DARK_LIGHT

TILE_HEADER_HEIGHT = 25
DAY_HEIGHT = 60
ICON_HEIGHT = 44

class Forecast(Container):
    """ This class draws 6 days weather forecast  """
    
    def __init__(self, util, image, semi_transparent_color, colors):
        """ Initializer
        
        :param util: utility object
        :param image: initial image
        :param semi_transparent_color: semi-transparent background color
        :param colors: colors
        """
        self.util = util
        self.colors = colors
        self.weather_config = util.weather_config
        self.initial_image = image
        
        if getattr(util, "config", None):
            self.rect = util.screen_rect
        else:
            self.rect = self.util.weather_config["screen.rect"]
        
        self.degree = DEGREE_SYMBOL
        self.semi_transparent_color = semi_transparent_color

    def set_weather(self, weather):
        """ Set weather object which has all forecast data
        
        :param weather: forecast object
        """
        if weather == None:
            self.forecast = []
            day = {DAY: UNKNOWN, CODE: CODE_UNKNOWN, HIGH: UNKNOWN}
            for _ in range(6):                
                self.forecast.append(day) 
        else:
            self.forecast = self.util.get_forecast()["data"][1:]

    def draw_weather(self):
        """ Draw weather forecast  """
        
        Container.__init__(self, self.util, self.rect, BLACK)
        
        c = Component(self.util)
        c.name = "forecast.bgr"
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
        comp.name = "sep." + str(x) + "." + str(y)
        rect = pygame.Rect(x + w, y + height, 1, h - height + 2)
        comp.content = rect
        comp.fgr = self.colors[COLOR_DARK_LIGHT]
        comp.bgr = self.colors[COLOR_DARK_LIGHT]
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
        code_image = fcast["icon"]
        image_w = image_h = int((h / 100) * ICON_HEIGHT)
        top_height = (h / 100) * TILE_HEADER_HEIGHT
        
        bb = pygame.Rect(0, 0, image_w, image_h)
        scale = 0.75
        bb.w *= scale
        bb.h *= scale

        img = self.util.load_multi_color_svg_icon(ICONS_FOLDER, code_image, bb)
        bb = img[1].get_rect()
        
        origin_x = x + (image_w - bb.w) / 2
        origin_y = y + top_height + (image_w - bb.h) / 2
        
        name = GENERATED_IMAGE + "tile." + str(origin_x) + str(origin_y)
        self.util.draw_image(img[1], origin_x, origin_y, self, bb, name)
    
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
        bb_h = h - top_height  
        
        font_size = int((bb_h / 100) * 50)
        front_color = self.colors[COLOR_CONTRAST]
        
        c = self.util.get_text_component(self.util.get_temperature(fcast["temperatureHigh"]) + self.degree, front_color, font_size)
        c.text = None
        c.name = c.image_filename = GENERATED_IMAGE + "temp." + str(int(c.content_x)) + str(int(c.content_y))
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
        comp.name = "tile.header." + str(x) + "." + str(y)
        comp.content_x = x
        comp.content_y = y
        rect = pygame.Rect(x, y, w, height)
        comp.content = rect
        comp.fgr = self.semi_transparent_color
        comp.bgr = self.semi_transparent_color
        comp.bounding_box = rect
        self.add_component(comp)
        
        text_color = self.colors[COLOR_BRIGHT]
        font_size = int((height / 100) * DAY_HEIGHT)

        d = self.util.get_weekday(fcast["time"])
        c = self.util.get_text_component(d, text_color, font_size)
        c.name = "th." + str(x) + "." + str(y)
        c.content_x = x + (w - c.content.get_size()[0]) / 2
        c.content_y = y + ((height - font_size) / 2)
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
        comp.name = "tile.body" + str(x) + "." + str(y)
        comp.content_x = x
        comp.content_y = y
        rect = pygame.Rect(x, y, w, h)
        comp.content = rect
        comp.fgr = self.colors[COLOR_BRIGHT]
        comp.bgr = self.colors[COLOR_BRIGHT]
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
