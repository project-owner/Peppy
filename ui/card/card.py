# Copyright 2022-2024 Peppy Player peppy.player@gmail.com
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
import logging
import textwrap

from ui.component import Component
from ui.container import Container
from ui.layout.borderlayout import BorderLayout
from util.config import SCREEN_INFO, WIDTH

BLACK = (0, 0, 0)
SEPARATOR = ":"
GENERATED_IMAGE = "generated.img."

TOP_HEIGHT = 15
BOTTOM_HEIGHT_DEFAULT = 25
TITLE_FONT_HEIGHT = 50
ICON_WIDTH = 20
ICON_HEIGHT = 40
ICON_MARGIN = 20
ICON_LABEL_HEIGHT = 10
VALUE_WIDTH = 80
VALUE_HEIGHT = 50
DEGREE_HEIGHT = 20

ONE_ROW_TEXT_HEIGHT = 32
TWO_ROW_TEXT_HEIGHT = 24
THREE_ROW_TEXT_HEIGHT = 20

COLOR_THEME = "color.theme"
LABEL = "label"
DATE = "date"
ICON = "icon"
ICON_2 = "icon.2"
ICON_LABEL = "icon.label"
VALUE = "value"
UNIT = "unit"
DETAILS = "details"
HEADER_FOOTER_BGR = "bgr"
SCREEN_BGR = "screen.bgr"
SHADOW = "shadow"
DETAIL_LABEL = "detail.label"
DETAIL_VALUE = "detail.value"
TREND = "trend"
TREND_UP = "up"
TREND_DOWN = "down"
TREND_UP_COLOR = "trend.up.color"
TREND_DOWN_COLOR = "trend.down.color"
TOP = "top"
LEFT = "left"
CENTER = "center"
RIGHT = "right"
LOGO_URL = "logo_url"
CHANGE_VALUE = "change.value"
CHANGE_PERCENT = "change.percent"

class Card(Container):
    """ Template for card screen """
    
    def __init__(self, cache_name, bb, name, util, icon_name, icon_folder=None, lcd=True, show_details=True, label_alignment=LEFT, 
        icon_alignment=CENTER, show_bgr=True, padding=(0, 0, 0, 0), show_border=False, value_height=VALUE_HEIGHT, icon_width=ICON_WIDTH):
        """ Initializer
        
        :param cache_name: icon cache name
        :param bb: bounding box
        :param name: screen name
        :param util: utility object
        :param label: title label
        :param icon_name: icon name
        :param icon_label: icon label
        :param lcd: True - LCD font, False - regular font
        :param show_details: True - show details, False - no details
        :param label_alignment: label alignment
        :param icon_alignment: icon alignment
        :param show_bgr: show background
        :param padding: padding for top/bottom components
        :param show_border: True - show separator on the left side
        :param value_height: height of the value
        :param icon_width: icon width
        """
        self.cache_name = cache_name
        self.name = name
        self.util = util
        self.image_util = util.image_util
        self.config = util.config
        self.icon_name = icon_name
        self.icon_folder = icon_folder
        self.lcd = lcd
        self.rect = bb
        Container.__init__(self, self.util, self.rect, BLACK)
        self.value = None
        self.unit = None
        self.details = None
        self.trend = None
        self.show_details = show_details
        self.label_alignment = label_alignment
        self.icon_alignment = icon_alignment
        self.show_bgr = show_bgr
        self.padding = padding
        self.show_border = show_border
        self.value_height = value_height
        self.font_size = None
        self.icon_width = icon_width
        self.layout = self.get_layout()

    def get_layout(self):
        """ Get the layout for title, details, icon area and value area

        :return: layout rectangle
        """
        layout = BorderLayout(self.rect)
        top = int(self.rect.h * TOP_HEIGHT / 100)

        if self.show_details:
            bottom = int(self.rect.h * BOTTOM_HEIGHT_DEFAULT / 100)
        else:
            bottom = 0

        center = self.rect.h - top - bottom
        if center % 2 != 0:
            top -= 1
            center += 1

        if self.icon_name == None:
            left = 0
        else:
            left = self.rect.w * self.icon_width / 100

        right = 0
        layout.set_pixel_constraints(top, bottom, left, right)

        if self.icon_name != None:
            layout.LEFT.y += self.rect.y
        
        return layout
        
    def set_value(self, label=None, icon_label=None, colors=None, value=None, unit=None, details=None, trend=None, 
        timestamp=None, bgr_img=None, change_value=None, change_percent=None):
        """ Set card label, value, unit and details
        
        :param label: card label
        :param icon_label: icon label
        :param colors: color theme
        :param value: value
        :param unit: unit
        :param details: details
        :param trend: trend type
        :param timestamp: timestamp
        :param bgr_img: background image
        :param change_value: change value
        :param change_percent: change percent
        """
        self.label = label
        self.icon_label = icon_label
        self.colors = colors
        self.value = value
        self.unit = unit
        self.details = details
        self.trend = trend
        self.timestamp = timestamp
        self.bgr_img = bgr_img
        self.change_value = change_value 
        self.change_percent = change_percent

        self.draw_card()

    def draw_card(self):
        """ Draw all card components """
        
        self.components.clear()
        c = Component(self.util)
        c.name = self.name + ".card.bgr"

        if self.show_bgr:
            if self.bgr_img:
                c.content = self.bgr_img
            else:
                c.content = self.rect.copy()
            c.bgr = self.colors[SCREEN_BGR]
        else:
            c.content = self.rect.copy()
            c.bgr = self.bgr = (0, 0, 0, 0)
        
        c.content_x = 0
        c.content_y = 0
        c.bounding_box = self.rect
        self.add_component(c)

        self.draw_top_background()
        self.draw_label()
        self.draw_time()
        self.draw_icon()       
        self.draw_value()
        self.draw_bottom_background()
        self.draw_details()

    def draw_top_background(self):
        """ Draw header background """
        
        bb = self.layout.TOP
        x = bb.x + self.padding[0]
        y = bb.y + self.padding[1]
        w = bb.w - self.padding[0] - self.padding[2]
        h = bb.h
        self.draw_background(x, y, w, h)

        if self.show_border:
            c = Component(self.util)
            c.name = "card.border"
            c.content = pygame.Rect(bb.x, bb.y + h, 1, self.layout.CENTER.h)
            c.bgr = self.colors[HEADER_FOOTER_BGR]
            c.bounding_box = c.content
            self.add_component(c)

    def draw_bottom_background(self):
        """ Draw footer background """

        if not self.show_details:
            return
        
        bb = self.layout.BOTTOM
        x = bb.x + self.padding[0]
        y = self.rect.h - bb.h - self.padding[3]
        w = bb.w - self.padding[0] - self.padding[2]
        h = bb.h
        self.draw_background(x, y, w, h)

    def get_label_component(self, label, color=None):
        """ Get label component
        
        :param: label text
        :param: label color

        :return: label component
        """
        bb = self.layout.TOP
        font_size = int((bb.h / 100) * TITLE_FONT_HEIGHT)

        if color == None:
            color = self.colors[LABEL]

        c = self.get_text_component(label, color, font_size)
        c.name = GENERATED_IMAGE + "label." + self.cache_name
        u = c.content.get_size()[1]/10
        
        if self.label_alignment == LEFT:
            c.content_x = bb.x + self.padding[0] + u * 3.4
        elif self.label_alignment == CENTER:
            c.content_x = bb.x + (bb.w - c.content.get_size()[0]) / 2

        c.content_y = bb.y + self.padding[1] + u/1.5 + (bb.h - font_size) / 2

        return c

    def draw_label(self):
        """ Draw label """

        label_component = self.get_label_component(self.label)
        self.add_component(label_component)

    def set_label(self, label, color=None):
        """ Set new label component
        
        :param label: label text
        :param color: label color
        """
        self.label = label

        for i, c in enumerate(self.components):
            if c != None and c.name == GENERATED_IMAGE + "label." + self.cache_name:
                self.components[i] = self.get_label_component(label, color)
                return

    def draw_time(self):
        """ Draw time """

        if self.timestamp == None:
            return

        bb = self.layout.TOP
        font_size = int((bb.h / 100) * TITLE_FONT_HEIGHT)
        c = self.get_text_component(self.timestamp, self.colors[LABEL], font_size)
        c.name = "time"
        y = (bb.h - font_size) / 2
        u = font_size/10
        c.content_x = self.rect.x + bb.w - c.content.get_size()[0] - self.padding[0] - u * 3.4
        c.content_y = bb.y + y + self.padding[1] + u/1.5
        self.add_component(c)

    def get_text_component(self, text, fgr, font_height):
        """ Create text component using supplied parameters
        
        :param text: text
        :param fgr: text color
        :param font_height: font height
        
        :return: text component
        """
        self.font = self.util.get_font(font_height)        
        label = self.font.render(text, 1, fgr)
        comp = Component(self.util, label)
        comp.text = text
        comp.text_size = font_height
        comp.fgr = fgr

        return comp

    def draw_background(self, x, y, w, h):
        """ Draw background defined by input parameters
        
        :param x: X coordinate
        :param y: Y coordinate
        :param w: width
        :param h: height
        """
        c = Component(self.util)
        c.name = "card.bgr"
        c.content = pygame.Rect(x, y, w, h)
        c.content_x = x
        c.content_y = y
        c.bounding_box = c.content
        c.bgr = self.colors[HEADER_FOOTER_BGR]
        self.add_component(c)

    def draw_value(self):
        """ Draw value """
        
        if self.value == None:
            return

        b = self.layout.CENTER
        bb = b.copy()
        bb.h = (bb.h * self.value_height) / 100
        
        if self.trend == TREND_UP:
            trend_color = self.colors[TREND_UP_COLOR]
            arrow_name = "up-arrow"
        elif self.trend == TREND_DOWN:
            trend_color = self.colors[TREND_DOWN_COLOR]
            arrow_name = "down-arrow"
        else:
            trend_color = None
            arrow_name = None

        if isinstance(self.value, str):
            bb.x = b.x
            bb.h = b.h
            bb.w = b.w

            self.render_string_value(bb, self.value)
            return

        img = self.render_card_value((bb.w, bb.h), self.value, self.unit, self.colors[VALUE], self.colors[SHADOW], trend_color, arrow_name, self.lcd)
        img_w = img.get_size()[0]
        img_h = bb.h

        c = Component(self.util, img)
        c.name = GENERATED_IMAGE + "value." + self.cache_name

        if self.lcd:
            c.content_x = bb.x + (b.w - img_w) / 2
            c.content_y = bb.y + (b.h - img_h) / 2
        else:
            c.content_x = bb.x + (b.w - img_w * 0.9) / 2
            c.content_y = bb.y + (b.h - img_h * 1.5) / 2

        c.image_filename = c.name
        self.add_component(c)
        
    def draw_icon(self):
        """ Draw image and image label """
        
        if self.icon_name == None:
            return

        if self.icon_label == None:
            spaces = 0
        else:
            spaces = self.icon_label.count(" ")

        bb = self.layout.LEFT
        font_size = int((bb.h / 100) * ICON_LABEL_HEIGHT)
        margin = (bb.w / 100) * ICON_MARGIN
        icon_bb = bb.copy()
        icon_bb.h = icon_bb.w

        if self.config[SCREEN_INFO][WIDTH] >= 1280:
            icon_bb.w = int(bb.w / 2)
        else:
            icon_bb.w = bb.w - margin

        try:
            icon_2 = self.colors[ICON_2]
        except:
            icon_2 = self.colors[ICON]

        icon_color_hex = self.image_util.color_to_hex(self.colors[ICON])
        icon_color_hex_2 = self.image_util.color_to_hex(icon_2)

        img = self.image_util.load_svg_icon(self.icon_name, icon_color_hex, icon_bb, color_2=icon_color_hex_2, cache_suffix=self.cache_name, folder=self.icon_folder)

        if img == None: 
            return

        image_w = img[1].get_size()[0]
        image_h = img[1].get_size()[1]
        self.origin_x = bb.x + abs(bb.w - image_w)/2
        self.origin_y = bb.y + abs(bb.h - image_h)/2
        
        if self.icon_label != None:
            if spaces > 0:
                self.origin_y = self.origin_y - font_size - font_size / 2
            else:
                self.origin_y = self.origin_y - font_size
        else:
            if self.icon_alignment == TOP:
                self.origin_y = bb.y + self.padding[1] * 3

        name = GENERATED_IMAGE + "card." + self.cache_name + "." + str(self.origin_x) + str(self.origin_y)
        c = Component(self.util)
        c.name = name
        c.content = img[1]

        if self.config[SCREEN_INFO][WIDTH] <= 480:
            c.content_x = self.origin_x + margin
        elif self.config[SCREEN_INFO][WIDTH] > 480 and self.config[SCREEN_INFO][WIDTH] <= 720:
            c.content_x = self.origin_x + int(margin/2)
        elif self.config[SCREEN_INFO][WIDTH] > 720 and self.config[SCREEN_INFO][WIDTH] <= 1280:
            c.content_x = self.origin_x + margin
        else:
            c.content_x = self.origin_x

        c.content_y = self.origin_y
        c.image_filename = name
        self.add_component(c)
        
        if self.icon_label == None:
            return

        line1 = line2 = None
        if spaces > 0:
            if spaces > 2:
                tokens = self.icon_label.split()
                line1 = tokens[0] + " " + tokens[1]
                line2 = self.icon_label[len(line1) :].strip()
            else:
                line1 = self.icon_label[0 : self.icon_label.rfind(" ")].strip()
                line2 = self.icon_label[self.icon_label.rfind(" ") :].strip()
        
        if line1:
            c = self.get_text_component(line1, self.colors[ICON_LABEL], font_size)
            c.name = "line1"
            txt_w = c.content.get_size()[0]
            txt_h = c.content.get_size()[1]
            y = bb.y + bb.h - txt_h
            c.content_x = bb.x + (bb.w - txt_w) / 2
            out_of_bb = False
            line_x = c.content_x

            if c.content_x <= bb.x:
                out_of_bb = True
                c.content_x = self.origin_x - margin / 2
                line_x = c.content_x

            c.content_y = y - font_size - font_size
            self.add_component(c)
            c = self.get_text_component(line2, self.colors[ICON_LABEL], font_size)
            c.name = "line2"
            txt_w = c.content.get_size()[0]
            txt_h = c.content.get_size()[1]
            y = bb.y + bb.h - txt_h
            c.content_x = bb.x + (bb.w - txt_w) / 2

            if out_of_bb or c.content_x <= (bb.x + 2):
                c.content_x = line_x

            c.content_y = y - font_size
            self.add_component(c)
        else:
            c = self.get_text_component(self.icon_label, self.colors[ICON_LABEL], font_size)
            c.name = "line1"
            txt_w = c.content.get_size()[0]
            txt_h = c.content.get_size()[1]
            y = bb.y + bb.h - txt_h
            c.content_x = bb.x + (bb.w - txt_w) / 2

            if c.content_x <= bb.x:
                c.content_x = self.origin_x - margin / 2

            c.content_y = y - font_size - (font_size / 2)
            self.add_component(c)

    def get_font_size(self, t1, t2, text_color, font_size):
        """ Return font size
        
        :param t1: text 1
        :param t2: text 2
        :param text_color: text color
        :param font_size: font size
        
        :return: either initial font size or initial font size - 2
        """
        w_1 = self.get_text_width(t1, text_color, font_size)
        w_2 = self.get_text_width(t2, text_color, font_size)
        w = max(w_1, w_2)
        if w > self.rect.w / 2:
            return font_size - 2
        else:
            return font_size
    
    def get_text_width(self, text, fgr, font_height):
        """ Calculate text width
        
        :param text: text
        :param fgr: text color
        :param font_height: font height
        
        :return: text width
        """
        self.font = self.util.get_font(font_height)        
        label = self.font.render(text, 1, fgr)
        return label.get_size()[0]

    def draw_details(self):
        """ Draw card details at the bottom """
        
        if not self.show_details or self.details == None:
            return
        
        bb = self.layout.BOTTOM
        details_len = len(self.details)
        w = bb.w - self.padding[0] - self.padding[2]

        if details_len == 1:
            row_height = int(bb.h / 3)
            text = self.get_label_value_unit(0)
            if text == None:
                return

            margin = (bb.h / 100) * (100 - ONE_ROW_TEXT_HEIGHT)/2
            text_width = self.get_max_text_width(self.details, row_height)
            x = self.padding[0] + (w - text_width) / 2
            y = self.rect.h - bb.h - self.padding[1] + margin
            self.add_column([text], x, y, row_height)
        elif details_len == 2:
            row_height = int(bb.h / 3)
            text = self.get_label_value_unit(0)
            margin = (bb.h / 100) * (100 - ONE_ROW_TEXT_HEIGHT)/2
            x = self.padding[0] + margin
            y = self.rect.h - bb.h + row_height
            self.add_column([text], x, y, row_height)

            text = self.get_label_value_unit(1)
            text_width = self.get_max_text_width(self.details[1:], row_height)
            x = bb.w - text_width - self.padding[0] - margin
            self.add_column([text], x, y, row_height)
        elif details_len == 3 or details_len == 4:
            margin_y = int(bb.h * 20) / 100
            area_h = bb.h - margin_y * 2
            line_gap = int(area_h * 10) / 100
            row_height = int((area_h - line_gap) / 2)
            text = self.get_label_value_unit(0)
            column = [text, self.get_label_value_unit(1)]
            margin_x = (bb.h - (row_height * 2.6)) / 2
            x = self.padding[0] + margin_x * 2
            y = self.rect.h - bb.h + margin_y
            self.add_column(column, x, y, row_height, line_gap)

            column = [self.get_label_value_unit(2)]
            if details_len == 4:
                column.append(self.get_label_value_unit(3))
            text = self.get_label_value_unit(1)
            text_width = self.get_max_text_width(self.details[2:], row_height)
            x = bb.w - text_width - self.padding[0] - margin_x * 2
            self.add_column(column, x, y, row_height, line_gap)
        elif details_len == 5 or details_len == 6:
            margin_y = int(bb.h * 10) / 100
            area_h = bb.h - margin_y * 2
            line_gap = int(area_h * 6) / 100
            row_height = int((area_h - line_gap * 2) / 3)
            text = self.get_label_value_unit(0)
            column = [text, self.get_label_value_unit(1), self.get_label_value_unit(2)]
            margin_x = (bb.h - (row_height * 3.8)) / 2
            x = self.padding[0] + margin_x * 2
            y = self.rect.h - bb.h + margin_y
            self.add_column(column, x, y, row_height, line_gap)

            column = [self.get_label_value_unit(3), self.get_label_value_unit(4)]
            if details_len == 6:
                column.append(self.get_label_value_unit(5))
            text = self.get_label_value_unit(1)
            text_width = self.get_max_text_width(self.details[3:], row_height)
            x = bb.w - text_width - self.padding[0] - margin_x * 2
            self.add_column(column, x, y, row_height, line_gap)
        elif details_len >= 7 and details_len <= 9:
            margin_y = int(bb.h * 10) / 100
            area_h = bb.h - margin_y * 2
            line_gap = int(area_h * 6) / 100
            row_height = int((area_h - line_gap * 2) / 3)
            text = self.get_label_value_unit(0)
            column = [text, self.get_label_value_unit(1), self.get_label_value_unit(2)]
            margin_x = (bb.h - (row_height * 3.8)) / 2
            x = self.padding[0] + margin_x * 2
            y = self.rect.h - bb.h + margin_y
            self.add_column(column, x, y, row_height, line_gap)

            column = [self.get_label_value_unit(3), self.get_label_value_unit(4), self.get_label_value_unit(5)]
            text = self.get_label_value_unit(1)
            text_width = self.get_max_text_width(self.details[3:5], row_height)
            x = bb.w/2 - text_width/2
            self.add_column(column, x, y, row_height, line_gap)

            column = [self.get_label_value_unit(6)]
            if details_len == 8 or details_len == 9:
                column.append(self.get_label_value_unit(7))
            if details_len == 9:
                column.append(self.get_label_value_unit(8))
            text = self.get_label_value_unit(1)
            text_width = self.get_max_text_width(self.details[6:], row_height)
            x = bb.w - text_width - self.padding[0]- margin_x * 2
            self.add_column(column, x, y, row_height, line_gap)
        else:
            logging.debug("Max supported details: 9")

    def get_label_value_unit(self, index):
        """ Get label, value and unit from the detail list by index
        
        :param index: list index

        :return: tuple with label, value and unit
        """
        try:
            label = self.details[index][0] + SEPARATOR
            value = self.details[index][1]
            unit = self.details[index][2]
            return (label, value, unit)
        except:
            return None

    def get_max_text_width(self, texts, font_size):
        """ Calculate the maximum string length from the provided list of strings
        
        :param texts: list of strings
        :param font_size: font size

        :return: maxumum string length
        """
        max_width = 0

        for text in texts:
            txt = text[0] + " " + str(text[1]) + text[2]
            text_width = self.get_text_width(txt, self.colors[DETAIL_LABEL], font_size)
            if text_width > max_width:
                max_width = text_width  

        return max_width

    def add_column(self, texts, x, y, row_height, line_gap=0):
        """ Add a column of details to the container
        
        :param texts: list of label, value and unit texts
        :param x: X coordinate of the top left column corner
        :param y: Y coordinate of the top left column corner
        :param row_height: row height
        """
        # label = self.get_text_component("TEXT", self.colors[DETAIL_LABEL], row_height)
        for i, text in enumerate(texts):
            if i == 0:
                height = 0
            else:
                height = (row_height + line_gap) * i
            self.add_label_value_unit(text, x, y + height, row_height)

    def add_label_value_unit(self, text, x, y, row_height):
        """ Add label, value and unit to the container
        
        :param text: text
        :param x: X coordinate of the text
        :param x: Y coordinate of the text
        :param row_height: row height
        """
        c_label = self.get_text_component(str(text[0]) + " ", self.colors[DETAIL_LABEL], row_height)
        c_label.name = "detail.label"
        w = c_label.content.get_size()[0]
        c_label.content_x = x
        c_label.content_y = y
        self.add_component(c_label)

        c_value = self.get_text_component(str(text[1]) + text[2], self.colors[DETAIL_VALUE], row_height)
        c_value.name = "value.unit"
        c_value.content_x = c_label.content_x + w
        c_value.content_y = c_label.content_y
        self.add_component(c_value)
   
    def render_card_value(self, bb, value, unit, color, color_shadow=None, trend_color=None, arrow_name=None, lcd=True):
        """ Render card value
        
        :param bb: boundnig box
        :param value: value
        :param unit: unit
        :param color: color
        :param color_shadow: shadow color
        :param trend_color: trend color
        :param arrow_name: trend arrow name
        :param lcd: True - LCD font, False - regular font
        """
        if lcd:
            return self.render_lcd_value(bb, value, unit, color, color_shadow, trend_color, arrow_name)
        else:
            return self.render_number_value(bb, value, unit, color, trend_color, arrow_name)

    def render_lcd_value(self, bb, value, unit, color, color_shadow=None, trend_color=None, arrow_name=None):
        """ Render LCD card value
        
        :param bb: boundnig box
        :param value: value
        :param unit: unit
        :param color: color
        :param color_shadow: shadow color
        :param trend_color: trend color
        :param arrow_name: trend arrow name
        """
        n = f"{value:0>5.1f}"

        bb = pygame.Rect(0, 0, bb[0], bb[1])
        icon_color_hex = self.image_util.color_to_hex(color)
        shadow_color_hex = self.image_util.color_to_hex(color_shadow)
        digits = None
        x = i = 0

        for d in n:
            if d == ".":
                dot = pygame.Surface((dot_size, dot_size))
                dot.fill(color)
                x += size[0] + gap
                digits.blit(dot, (x*0.992, h - dot_size))
                x -= size[0] + gap
                x += dot_width
                i += 1 
                continue

            if d == "0" and (i == 0 or i == 1):
                shadow_color = shadow_color_hex
            else:
                shadow_color = icon_color_hex

            digit = self.image_util.load_svg_icon("lcd." + d, shadow_color_hex, bb, color_2=shadow_color, cache_suffix=self.cache_name, category="")

            if digits == None:
                size = digit[1].get_size()
                gap = (size[0] / 100) * 12
                h = bb.h
                dot_size = size[1] / 8.7
                dot_width = dot_size * 1.4
                if unit:
                    unit_height = int(h * 0.3)
                    font = self.util.get_font(unit_height)
                    unit_image = font.render(unit, 1, color)
                    unit_width = unit_image.get_size()[0] * 1.2
                else:
                    unit_width = 0

                total_width = size[0] * 4 + dot_width + gap * 5 + unit_width
                digits = pygame.Surface((total_width, h), pygame.SRCALPHA)

            if i == 0:
                x = 0
            else:
                x += size[0] + gap

            digits.blit(digit[1], (x, 0))

            if i == 4 and unit:
                x += size[0] + gap * 2
                y = bb.h - unit_height * 1.1
                digits.blit(unit_image, (x, y))
                if trend_color:
                    trend_color_hex = self.image_util.color_to_hex(trend_color)
                    bb = pygame.Rect(0, 0, unit_width, y)
                    arrow = self.image_util.load_svg_icon(arrow_name, trend_color_hex, bb, color_2=trend_color_hex, cache_suffix=self.cache_name)
                    arrow_width = arrow[1].get_size()[0]
                    x = x + gap + (unit_width*0.8 - arrow_width)*0.6
                    digits.blit(arrow[1], (x, 0))

            i += 1

        return digits

    def render_number_value(self, bb, value, unit, color, trend_color=None, arrow_name=None):
        """ Render value
        
        :param bb: boundnig box
        :param value: value
        :param unit: unit
        :param color: color
        :param trend_color: trend color
        :param arrow_name: trend arrow name
        """
        if value == None:
            return

        n = f"{value:5.2f}"
        digits = arrow = None
        x = 0

        font = self.util.get_font(bb[1])
        dg = font.render(n, 1, color)
        size = dg.get_size()
        gap = (size[0] / 100) * 14
        w = size[0]
        h = bb[1]
        if unit:
            unit_height = int(h * 0.2)
            font = self.util.get_font(unit_height)
            unit_image = font.render(unit, 1, color)
            unit_width = unit_image.get_size()[0]
            unit_height = bb[1]
        else:
            unit_width = 0

        if trend_color and arrow_name:
            trend_color_hex = self.image_util.color_to_hex(trend_color)
            b = pygame.Rect(0, 0, h * 0.14, h * 0.36)
            arrow = self.image_util.load_svg_icon(arrow_name, trend_color_hex, b, color_2=trend_color_hex, cache_suffix=self.cache_name)
            arrow_width = arrow[1].get_size()[0]
            arrow_height = b.h
        else:
            arrow_width = 0
            arrow_height = 0

        total_width = w + gap / 3 + unit_width
        total_height = bb[1] + arrow_height

        digits = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        digits.blit(dg, (0, 0))

        if unit:
            x = size[0] + gap / 3
            y = h - unit_height * 1.7
            digits.blit(unit_image, (x, y))

        if arrow:
            change_height = int(h * 0.2)
            font = self.util.get_font(change_height)
            change_image = font.render(" " + self.change_value + "  " + self.change_percent + "%", 1, color)
            change_width = change_image.get_size()[0]
            width = arrow_width + change_width

            x = w - width
            y = total_height - change_height - 4
            digits.blit(arrow[1], (x, y))
            digits.blit(change_image, (x + arrow_width, y))

        return digits

    def render_string_value(self, bb, value):
        """ Render string value
        
        :param bb: bounding box
        :param value: value string
        """
        
        if self.config[SCREEN_INFO][WIDTH] <= 320:
            font_size = 10
            line_length = 46
            line_gap = 6
        elif self.config[SCREEN_INFO][WIDTH] > 320 and self.config[SCREEN_INFO][WIDTH] <= 480:
            font_size = 14
            line_length = 50
            line_gap = 8
        elif self.config[SCREEN_INFO][WIDTH] > 480 and self.config[SCREEN_INFO][WIDTH] <= 720:
            font_size = 20
            line_length = 52
            line_gap = 10
        elif self.config[SCREEN_INFO][WIDTH] > 720 and self.config[SCREEN_INFO][WIDTH] <= 800:
            font_size = 22
            line_length = 52
            line_gap = 10
        elif self.config[SCREEN_INFO][WIDTH] > 800 and self.config[SCREEN_INFO][WIDTH] <= 1024:
            font_size = 26
            line_length = 56
            line_gap = 12
        elif self.config[SCREEN_INFO][WIDTH] > 1024 and self.config[SCREEN_INFO][WIDTH] <= 1280:
            font_size = 22
            line_length = 86
            line_gap = 10
        else:
            font_size = 15
            line_length = 50
            line_gap = 8

        lines = textwrap.wrap(value, line_length)
        font = self.util.get_font(font_size)
        rendered_lines = []
        max_width = 0
        max_height = 0
        for n, line in enumerate(lines):
            r = font.render(line, 1, self.colors[VALUE])
            max_width = max(max_width, r.get_size()[0])
            max_height = max(max_height, font_size)
            rendered_lines.append(r)

        text_width = max_width
        text_height = (max_height * len(lines)) + (len(lines) - 1) * line_gap
        
        for n, line in enumerate(lines):
            c = Component(self.util, rendered_lines[n])
            c.name = "desc." + str(n)
            c.text = line
            c.text_size = font_size
            c.text_color_normal = self.colors[VALUE]
            c.text_color_current = c.text_color_normal
            c.content_x = bb.x + (bb.w - text_width) / 2
            c.content_y = bb.y + (bb.h - text_height) / 2 + (n * (max_height + line_gap))
            self.components.append(c)
