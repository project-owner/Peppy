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

from datetime import datetime
from component import Component
from container import Container
from weatherconfigparser import SCREEN_RECT, CITY, REGION, COUNTRY, COLOR_DARK_LIGHT, COLOR_DARK, \
    COLOR_CONTRAST, COLOR_MEDIUM, COLOR_BRIGHT, COLOR_DARK_LIGHT, DEGREE, UNIT, UNKNOWN, HUMIDITY, WIND, \
    SUNRISE, SUNSET, CITY_LABEL, MPH
from weatherutil import CHILL, DIRECTION, SPEED, TEMPERATURE, VISIBILITY, HUMIDITY, PRESSURE, \
    SUNRISE, SUNSET, TEMP, TEXT, CODE, DATE, HIGH, LOW, CODE_UNKNOWN, ICONS_FOLDER, BLACK

TOP_HEIGHT = 15
BOTTOM_HEIGHT = 25
CITY_FONT_HEIGHT = 50
TIME_FONT_HEIGHT = 50
CODE_WIDTH = 35
CODE_IMAGE_WIDTH = 80
CODE_TEXT_HEIGHT = 10
TEMP_WIDTH = 40
TEMP_HEIGHT = 60
HIGH_LOW_TEXT_SIZE = 34
DEGREE_HEIGHT = 20

class Today(Container):
    """ This class draws screen for Today's weather """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """
        self.util = util
        self.weather_config = util.weather_config
        self.degree = self.weather_config[DEGREE]
        
        if getattr(util, "config", None):
            self.config = util.config
            self.rect = self.config[SCREEN_RECT]
        else:
            self.rect = self.util.weather_config[SCREEN_RECT]
        
    def set_weather(self, weather):
        """ Fetch all required weather parameters from supplied object
        
        :param weather: object with weather parameters
        """
        if weather == None:
            self.set_unknown_weather()
            return

        self.chill = self.util.get_wind()[CHILL]
        self.direction = self.util.get_wind()[DIRECTION]
        self.speed = self.util.get_wind()[SPEED]
        
        self.visibility = self.util.get_atmosphere()[VISIBILITY]
        self.humidity = self.util.get_atmosphere()[HUMIDITY]
        self.pressure = self.util.get_atmosphere()[PRESSURE]
        
        a = self.util.get_astronomy()
        t = self.util.get_astronomy()[SUNRISE]
        self.sunrise = self.util.get_time(t)
        t = self.util.get_astronomy()[SUNSET]
        self.sunset = self.util.get_time(t)
        
        self.temp = self.util.get_condition()[TEMP]
        
        self.mph = self.weather_config[MPH]
        self.temp_unit = self.util.get_units()[TEMPERATURE]
        
        self.code = self.util.get_condition()[CODE]
        self.txt = self.weather_config[self.code]
        self.code_image = self.util.code_image_map[int(self.code)]
        
        d = self.util.get_condition()[DATE]
        self.time = self.util.get_time_from_date(d)

        today_weather = self.util.get_forecast()[0]
        self.high = today_weather[HIGH]
        self.low = today_weather[LOW]        

    def set_unknown_weather(self):
        """ Set parameters in case of unavailable weather """
        
        self.city = UNKNOWN        
        self.chill = self.direction = self.speed = UNKNOWN        
        self.visibility = self.humidity = self.pressure = UNKNOWN        
        self.sunrise = self.sunset = UNKNOWN        
        self.temp = self.txt = UNKNOWN        
        self.mph = self.temp_unit = UNKNOWN        
        self.code = CODE_UNKNOWN
        self.code_image = self.util.code_image_map[int(self.code)]        
        self.time = UNKNOWN
        self.high = self.low = UNKNOWN

    def draw_weather(self):
        """ Draw Today's weather """
        
        Container.__init__(self, self.util, self.rect, BLACK)        
        
        top_height = self.draw_top_background(self.util.weather_config[COLOR_DARK_LIGHT])
        self.draw_city(top_height)
        self.draw_time(top_height)
        
        bottom_height = self.draw_bottom_background(self.util.weather_config[COLOR_DARK_LIGHT])
        
        c = self.util.weather_config[COLOR_BRIGHT]
        self.draw_center_background(top_height, bottom_height, c)        
        
        self.draw_code()
        self.draw_temp()
        
        self.draw_high_low()
         
        self.draw_details()

    def draw_city(self, top_height):
        """ Draw city name
        
        :param top_height: the height of the top area
        """
        text_color = self.util.weather_config[COLOR_CONTRAST]
        font_size = int((top_height / 100) * CITY_FONT_HEIGHT)
        c = self.util.get_text_component(self.weather_config[CITY_LABEL], text_color, font_size)
        y = int((top_height - c.content.get_size()[1]) / 2) + 1
        c.content_x = int(font_size / 2)
        c.content_y = y
        self.add_component(c)
        
    def draw_time(self, top_height):
        """ Draw time
        
        :param top_height: the height of the top area
        """
        text_color = self.util.weather_config[COLOR_CONTRAST]
        font_size = int((top_height / 100) * TIME_FONT_HEIGHT)
        c = self.util.get_text_component(self.time, text_color, font_size)
        y = int((top_height - c.content.get_size()[1]) / 2) + 1
        c.content_x = int(self.rect.w - c.content.get_size()[0] - int(font_size / 2))
        c.content_y = y
        self.add_component(c)

    def draw_top_background(self, color):
        """ Draw header background
        
        :param color: background color
        """
        w = self.rect.w
        h = int((self.rect.h / 100) * TOP_HEIGHT)
        self.draw_background(self.rect.x, self.rect.y, w, h, color)
        return h
    
    def draw_center_background(self, top_height, bottom_height, color):
        """ Draw center background
        
        :param top_height: the height of the header
        :param bottom_height: the height of the footer
        :param color: background color
        """
        w = self.rect.w
        h = int(self.rect.h - top_height - bottom_height)
        self.draw_background(self.rect.x, top_height, w, h, color)
        return h
        
    def draw_bottom_background(self, color):
        """ Draw footer background
        
        :param color: background color
        """
        h = int((self.rect.h / 100) * BOTTOM_HEIGHT)
        w = self.rect.w
        y = self.rect.h - h        
        self.draw_background(self.rect.x, y, w, h, color)
        return h
    
    def draw_background(self, x, y, w, h, color):
        """ Draw background defined by input parameters
        
        :param x: x coordinate
        :param y: y coordinate
        :param w: width
        :param h: height
        :param color: background color
        """
        c = Component(self.util)
        c.content = pygame.Rect(x, y, w, h)
        c.content_x = x
        c.content_y = y
        c.bounding_box = c.content
        c.bgr = color
        self.add_component(c)

    def draw_temp(self):
        """ Draw temperature with shadow """
        
        bb_x = int((self.rect.w / 100) * CODE_WIDTH)
        bb_y = int((self.rect.h / 100) * TOP_HEIGHT)
        bb_w = int((self.rect.w / 100) * TEMP_WIDTH)
        bb_h = self.rect.h - bb_y - int((self.rect.h / 100) * BOTTOM_HEIGHT)  
        
        font_size = int((bb_h / 100) * TEMP_HEIGHT)
        front_color = self.util.weather_config[COLOR_DARK_LIGHT]
        shadow_color = self.util.weather_config[COLOR_MEDIUM]
         
        c = self.util.get_text_component(self.temp, shadow_color, font_size)
        offset = 2
        c.content_x = bb_x + int((bb_w - c.content.get_size()[0]) / 2) + offset
        c.content_y = bb_y + int((bb_h - c.content.get_size()[1]) / 2) + 6 + offset
        self.add_component(c)
        
        c = self.util.get_text_component(self.temp, front_color, font_size)
        c.content_x = bb_x + int((bb_w - c.content.get_size()[0]) / 2)
        c.content_y = bb_y + int((bb_h - c.content.get_size()[1]) / 2) + 6
        self.add_component(c)
        
        right_edge = c.content_x + c.content.get_size()[0]
        top_edge = c.content_y
        height = c.content.get_size()[1]
        
        font_size = int((height / 100) * DEGREE_HEIGHT)
        d = self.degree + self.temp_unit
        
        c = self.util.get_text_component(d, shadow_color, font_size)
        c.content_x = right_edge + offset
        c.content_y = top_edge + font_size + offset
        self.add_component(c)
        
        c = self.util.get_text_component(d, front_color, font_size)
        c.content_x = right_edge
        c.content_y = top_edge + font_size
        self.add_component(c)
        
        self.temp_right_edge = right_edge + c.content.get_size()[0]
        
    def draw_code(self):
        """ Draw image and text for the today's weather """
        
        spaces = self.txt.count(" ")
        bb_x = 0
        bb_y = int((self.rect.h / 100) * TOP_HEIGHT)
        bb_w = int((self.rect.w / 100) * CODE_WIDTH)
        bb_h = self.rect.h - bb_y - int((self.rect.h / 100) * BOTTOM_HEIGHT)
        image_w = image_h = int((bb_w / 100) * CODE_IMAGE_WIDTH) 
        font_size = int((bb_h / 100) * CODE_TEXT_HEIGHT)
        
        bb = pygame.Rect(0, 0, image_w, image_h)        
        img = self.util.load_svg_icon(ICONS_FOLDER, self.code_image, bb)
        bb = img[1].get_rect()
        image_w = bb.w
        image_h = bb.h
        
        self.origin_x = bb_x + int((bb_w - image_w))
        self.origin_y = bb_y + int((bb_h - image_h) / 2)
        
        bb.x = self.origin_x
        if spaces > 0:
            bb.y = self.origin_y - font_size - font_size / 2
        else:
            bb.y = self.origin_y - font_size
        self.util.draw_image(img[1], self.origin_x, self.origin_y, self, bb)
        
        text_color = self.util.weather_config[COLOR_DARK]
        
        line1 = line2 = None
        if spaces > 0:
            if spaces > 2:
                tokens = self.txt.split()
                line1 = tokens[0] + " " + tokens[1]
                line2 = self.txt[len(line1) :].strip()
            else:
                line1 = self.txt[0 : self.txt.rfind(" ")].strip()
                line2 = self.txt[self.txt.rfind(" ") :].strip()
        
        if line1:
            c = self.util.get_text_component(line1, text_color, font_size)
            y = int((bb_y + bb_h - c.content.get_size()[1]))
            c.content_x = int(bb_w - (image_w / 2) - (c.content.get_size()[0] / 2))
            c.content_y = y - font_size - font_size
            self.add_component(c)
            c = self.util.get_text_component(line2, text_color, font_size)
            y = int((bb_y + bb_h - c.content.get_size()[1]))
            c.content_x = int(bb_w - (image_w / 2) - (c.content.get_size()[0] / 2))
            c.content_y = y - font_size
            self.add_component(c)
        else:
            c = self.util.get_text_component(self.txt, text_color, font_size)
            y = int((bb_y + bb_h - c.content.get_size()[1]))
            c.content_x = int(bb_w - (image_w / 2) - (c.content.get_size()[0] / 2))
            c.content_y = y - font_size - (font_size / 2)
            self.add_component(c)
        
    def draw_high_low(self):
        """ Draw high/low today's temperatures """
        
        bb_x = self.temp_right_edge
        bb_y = int((self.rect.h / 100) * TOP_HEIGHT)
        bb_w = self.rect.w - bb_x
        bb_h = self.rect.h - bb_y - int((self.rect.h / 100) * BOTTOM_HEIGHT)
        text_color = self.util.weather_config[COLOR_DARK_LIGHT]
        font_size = int((bb_w / 100) * HIGH_LOW_TEXT_SIZE)
        
        c = self.util.get_text_component(self.high, text_color, font_size)
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = bb_x + int((bb_w - w) / 2)
        c.content_y = bb_y + int((bb_h - h) / 2) - (font_size / 2)
        self.add_component(c)
        
        c = self.util.get_text_component(self.low, text_color, font_size)
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = bb_x + int((bb_w - w) / 2)
        c.content_y = bb_y + int((bb_h - h) / 2) + (font_size / 1.4)
        self.add_component(c)
        
        x = c.content_x
        y = bb_y + int(bb_h / 2)
        w = c.content.get_size()[0]
        h = 2
        r = pygame.Rect(x, y, w, h)
        c = Component(self.util, r)
        c.name = "sep" + ".text"
        c.content_x = 0
        c.content_y = 0
        c.fgr = text_color
        c.bgr = text_color
        self.add_component(c)
    
    def get_font_size(self, t1, t2, text_color, font_size):
        """ Return font size
        
        :param t1: text 1
        :param t2: text 2
        :param text_color: text color
        :param font_size: initial font size
        
        :return: either initial font size or initial font size - 2
        """
        w_1 = self.util.get_text_width(t1, text_color, font_size)
        w_2 = self.util.get_text_width(t2, text_color, font_size)
        w = max(w_1, w_2)
        if w > self.rect.w / 2:
            return font_size - 2
        else:
            return font_size
    
    def draw_details(self):
        """ Draw such weather details as humidity, wind, sunrise and sunset """
        
        colon = ":"
        humidity_label = self.weather_config[HUMIDITY] + colon
        wind_label = self.weather_config[WIND] + colon
        sunrise_label = self.weather_config[SUNRISE] + colon
        sunset_label = self.weather_config[SUNSET] + colon
        
        bottom_height = (self.rect.h / 100) * BOTTOM_HEIGHT
        font_size = int((bottom_height / 100) * 26)
        center_line = self.rect.w / 2
        
        base_line = self.rect.h - (bottom_height / 2) 
        text_color = self.util.weather_config[COLOR_CONTRAST]
        value_color = self.util.weather_config[COLOR_BRIGHT]
        
        tail = 3
        t1 = humidity_label + " " + self.humidity + "%" + " " * tail
        t2 = wind_label + " " + self.speed + " " + self.mph + " " * tail
        fs_1 = self.get_font_size(t1, t2, text_color, font_size)
        
        t1 = sunrise_label + " " + self.sunrise + " " * tail 
        t2 = sunset_label + " " + self.sunset + " " * tail
        fs_2 = self.get_font_size(t1, t2, text_color, font_size)
        
        font_size = min(fs_1, fs_2)
        
        v_1 = self.util.get_text_width(humidity_label + " " * (tail - 1), text_color, font_size)
        v_2 = self.util.get_text_width(wind_label + " " * (tail - 1), text_color, font_size)               
        value_width = max(v_1, v_2)        
        left_center = value_width
        
        v_1 = self.util.get_text_width(self.sunrise + " " * (tail + 1), text_color, font_size)        
        v_2 = self.util.get_text_width(self.sunset + " " * (tail + 1), text_color, font_size)        
        value_width = max(v_1, v_2)        
        right_center = self.rect.w - value_width
                
        c = self.util.get_text_component(humidity_label, text_color, font_size)
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = left_center - w
        c.content_y = base_line - h / 1.1
        self.add_component(c)
        
        c = self.util.get_text_component(self.humidity + "%", value_color, font_size)
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = left_center + font_size / 2
        c.content_y = base_line - h / 1.1
        self.add_component(c)
        
        c = self.util.get_text_component(wind_label, text_color, font_size)
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = left_center - w
        c.content_y = base_line
        self.add_component(c)
        
        c = self.util.get_text_component(self.speed + " " + self.mph, value_color, font_size)
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = left_center + font_size / 2
        c.content_y = base_line
        self.add_component(c)
        
        c = self.util.get_text_component(sunrise_label, text_color, font_size)
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = right_center - w
        c.content_y = base_line - h / 1.1
        self.add_component(c)
        
        c = self.util.get_text_component(self.sunrise, value_color, font_size)
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = right_center + font_size / 2
        c.content_y = base_line - h / 1.1
        self.add_component(c)
        
        c = self.util.get_text_component(sunset_label, text_color, font_size)
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = right_center - w
        c.content_y = base_line
        self.add_component(c)
        
        c = self.util.get_text_component(self.sunset, value_color, font_size)
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = right_center + font_size / 2
        c.content_y = base_line
        self.add_component(c)
        