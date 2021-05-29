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

from ui.component import Component
from ui.container import Container
from weatherutil import SPEED, TEMPERATURE, HUMIDITY, STATUS, SUNRISE, SUNSET, CODE_UNKNOWN, ICONS_FOLDER, \
    BLACK, GENERATED_IMAGE, IMAGE_CODE, DEGREE_SYMBOL, WIND_LABEL, UNKNOWN, MPH
from util.config import COLOR_CONTRAST, COLOR_BRIGHT

TOP_HEIGHT = 15
BOTTOM_HEIGHT = 25
CITY_FONT_HEIGHT = 50
TIME_FONT_HEIGHT = 50
CODE_WIDTH = 35
CODE_IMAGE_HEIGHT = 65
CODE_TEXT_HEIGHT = 10
TEMP_WIDTH = 55
TEMP_HEIGHT = 60
DEGREE_HEIGHT = 20

class Today(Container):
    """ This class draws screen for Today's weather """
    
    def __init__(self, util, image, semi_transparent_color, colors, labels, city_label):
        """ Initializer
        
        :param util: utility object
        :param image: initial image
        :param semi_transparent_color: semi-transparent background color
        :param colors: colors
        :param labels: labels
        :param city_label: city label
        """
        self.util = util
        self.colors = colors
        self.weather_config = util.weather_config
        self.initial_image = image
        self.degree = DEGREE_SYMBOL
        self.labels = labels
        self.city_label = city_label
        
        if getattr(util, "config", None):
            self.config = util.config
            self.rect = util.screen_rect
        else:
            self.rect = self.util.weather_config["screen.rect"]
        
        self.semi_transparent_color = semi_transparent_color
        
    def set_weather(self, weather):
        """ Fetch all required weather parameters from supplied object
        
        :param weather: object with weather parameters
        """
        if weather == None:
            self.set_unknown_weather()
            return

        self.speed = self.util.get_wind()[SPEED]
        self.humidity = self.util.get_atmosphere()[HUMIDITY]
        
        self.sunrise = self.util.get_time(self.util.get_astronomy()[SUNRISE])
        self.sunset = self.util.get_time(self.util.get_astronomy()[SUNSET])
        
        self.temp = self.util.get_condition()[TEMPERATURE]
        
        self.mph = self.labels[MPH]
        self.temp_unit = self.util.get_units()
        
        self.txt = self.util.get_condition()[STATUS]
        self.code_image = self.util.get_condition()[IMAGE_CODE]
        
        self.time = self.util.get_time(self.util.current_observation.ref_time)

    def set_unknown_weather(self):
        """ Set parameters in case of unavailable weather """
        
        self.city = UNKNOWN        
        self.speed = UNKNOWN        
        self.pressure = UNKNOWN        
        self.sunrise = self.sunset = UNKNOWN        
        self.temp = self.txt = UNKNOWN        
        self.mph = self.temp_unit = UNKNOWN        
        self.code = CODE_UNKNOWN
        self.code_image = None   
        self.time = UNKNOWN

    def draw_weather(self):
        """ Draw Today's weather """
        
        Container.__init__(self, self.util, self.rect, BLACK)
        
        c = Component(self.util)
        c.name = "today"
        c.content = self.initial_image
        c.content_x = 0
        c.content_y = 0
        c.bounding_box = self.rect
        self.add_component(c)       
        
        top_height = self.draw_top_background()
        self.draw_bottom_background()
        self.draw_city(top_height)
        self.draw_time(top_height)        
        self.draw_code()
        self.draw_temp()        
        self.draw_details()

    def draw_city(self, top_height):
        """ Draw city name
        
        :param top_height: the height of the top area
        """
        text_color = self.colors[COLOR_BRIGHT]
        font_size = int((top_height / 100) * CITY_FONT_HEIGHT)
        c = self.util.get_text_component(self.city_label, text_color, font_size)
        c.name = "city"
        y = int((top_height - c.content.get_size()[1]) / 2) + 1
        c.content_x = int(font_size / 2)
        c.content_y = y
        self.add_component(c)
        
    def draw_time(self, top_height):
        """ Draw time
        
        :param top_height: the height of the top area
        """
        text_color = self.colors[COLOR_BRIGHT]
        font_size = int((top_height / 100) * TIME_FONT_HEIGHT)
        c = self.util.get_text_component(self.time, text_color, font_size)
        c.name = "time"
        y = int((top_height - c.content.get_size()[1]) / 2) + 1
        c.content_x = int(self.rect.w - c.content.get_size()[0] - int(font_size / 2))
        c.content_y = y
        self.add_component(c)

    def draw_top_background(self):
        """ Draw header background """
        
        w = self.rect.w
        h = int((self.rect.h / 100) * TOP_HEIGHT)
        self.draw_background(self.rect.x, self.rect.y, w, h)
        return h
    
    def draw_bottom_background(self):
        """ Draw footer background """
        
        h = int((self.rect.h / 100) * BOTTOM_HEIGHT)
        w = self.rect.w
        y = self.rect.h - h        
        self.draw_background(self.rect.x, y, w, h)
        return h
    
    def draw_background(self, x, y, w, h):
        """ Draw background defined by input parameters
        
        :param x: x coordinate
        :param y: y coordinate
        :param w: width
        :param h: height
        """
        c = Component(self.util)
        c.name = "today.bgr"
        c.content = pygame.Rect(x, y, w, h)
        c.content_x = x
        c.content_y = y
        c.bounding_box = c.content
        c.bgr = self.semi_transparent_color
        self.add_component(c)

    def draw_temp(self):
        """ Draw temperature with shadow """
        
        bb_x = int((self.rect.w / 100) * CODE_WIDTH)
        bb_y = int((self.rect.h / 100) * TOP_HEIGHT)
        bb_w = int((self.rect.w / 100) * TEMP_WIDTH)
        bb_h = self.rect.h - bb_y - int((self.rect.h / 100) * BOTTOM_HEIGHT)  
        
        font_size = int((bb_h / 100) * TEMP_HEIGHT)
        front_color = self.colors[COLOR_CONTRAST]
         
        c = self.util.get_text_component(self.temp, front_color, font_size)
        c.name = "temp"
        c.content_x = bb_x + int((bb_w - c.content.get_size()[0]) / 2)
        c.content_y = bb_y + int((bb_h - c.content.get_size()[1]) / 2) + 6
        self.add_component(c)
        
        right_edge = c.content_x + c.content.get_size()[0]
        top_edge = c.content_y
        height = c.content.get_size()[1]
        
        font_size = int((height / 100) * DEGREE_HEIGHT)
        d = self.degree + self.temp_unit
        
        c = self.util.get_text_component(d, front_color, font_size)
        c.name = "temp.unit"
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
        image_w = image_h = int((bb_h / 100) * CODE_IMAGE_HEIGHT)
        font_size = int((bb_h / 100) * CODE_TEXT_HEIGHT)
        
        bb = pygame.Rect(0, 0, image_w, image_h)        
        img = self.util.load_multi_color_svg_icon(ICONS_FOLDER, self.code_image, bb)
        bb = img[1].get_rect()
        image_w = bb.w
        image_h = bb.h
        
        self.origin_x = bb_x + int((bb_w - image_w))
        self.origin_y = bb_y + int((bb_h - image_h) / 2)
        
        if spaces > 0:
            self.origin_y = self.origin_y - font_size - font_size / 2
        else:
            self.origin_y = self.origin_y - font_size

        name = GENERATED_IMAGE + "code." + str(self.origin_x) + str(self.origin_y)
        self.util.draw_image(img[1], self.origin_x, self.origin_y, self, bb, name)
        
        text_color = self.colors[COLOR_CONTRAST]
        
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
            c.name = "code1"
            y = int((bb_y + bb_h - c.content.get_size()[1]))
            c.content_x = int(bb_w - (image_w / 2) - (c.content.get_size()[0] / 2))
            c.content_y = y - font_size - font_size
            self.add_component(c)
            c = self.util.get_text_component(line2, text_color, font_size)
            c.name = "code2"
            y = int((bb_y + bb_h - c.content.get_size()[1]))
            c.content_x = int(bb_w - (image_w / 2) - (c.content.get_size()[0] / 2))
            c.content_y = y - font_size
            self.add_component(c)
        else:
            c = self.util.get_text_component(self.txt, text_color, font_size)
            c.name = "code1"
            y = int((bb_y + bb_h - c.content.get_size()[1]))
            c.content_x = int(bb_w - (image_w / 2) - (c.content.get_size()[0] / 2))
            c.content_y = y - font_size - (font_size / 2)
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
        humidity_label = self.labels[HUMIDITY] + colon
        wind_label = self.labels[WIND_LABEL] + colon
        sunrise_label = self.labels[SUNRISE] + colon
        sunset_label = self.labels[SUNSET] + colon
        
        bottom_height = (self.rect.h / 100) * BOTTOM_HEIGHT
        font_size = int((bottom_height / 100) * 26)
        center_line = self.rect.w / 2
        
        base_line = self.rect.h - (bottom_height / 2) 
        text_color = self.colors[COLOR_BRIGHT]
        value_color = self.colors[COLOR_CONTRAST]
        
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
        c.name = "humidity.label"
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = left_center - w
        c.content_y = base_line - h / 1.1
        self.add_component(c)
        
        c = self.util.get_text_component(self.humidity + "%", value_color, font_size)
        c.name = "humidity"
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = left_center + font_size / 2
        c.content_y = base_line - h / 1.1
        self.add_component(c)
        
        c = self.util.get_text_component(wind_label, text_color, font_size)
        c.name = "wind.label"
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = left_center - w
        c.content_y = base_line
        self.add_component(c)
        
        c = self.util.get_text_component(self.speed + " " + self.mph, value_color, font_size)
        c.name = "wind.speed"
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = left_center + font_size / 2
        c.content_y = base_line
        self.add_component(c)
        
        c = self.util.get_text_component(sunrise_label, text_color, font_size)
        c.name = "sunrise.label"
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = right_center - w
        c.content_y = base_line - h / 1.1
        self.add_component(c)
        
        c = self.util.get_text_component(self.sunrise, value_color, font_size)
        c.name = "sunrise.time"
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = right_center + font_size / 2
        c.content_y = base_line - h / 1.1
        self.add_component(c)
        
        c = self.util.get_text_component(sunset_label, text_color, font_size)
        c.name = "sunset.label"
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = right_center - w
        c.content_y = base_line
        self.add_component(c)
        
        c = self.util.get_text_component(self.sunset, value_color, font_size)
        c.name = "sunset.time"
        w = c.content.get_size()[0]
        h = c.content.get_size()[1]
        c.content_x = right_center + font_size / 2
        c.content_y = base_line
        self.add_component(c)
        