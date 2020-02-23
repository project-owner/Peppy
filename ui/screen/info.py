# Copyright 2020 Peppy Player peppy.player@gmail.com
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
import numbers

from ui.state import State
from ui.layout.borderlayout import BorderLayout
from ui.layout.gridlayout import GridLayout
from ui.factory import Factory
from ui.component import Component
from ui.container import Container
from util.keys import LABELS, KEY_INFO, KEY_BACK, USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, \
    H_ALIGN_RIGHT, V_ALIGN_BOTTOM, H_ALIGN_LEFT, V_ALIGN_TOP, H_ALIGN_CENTER
from util.config import SCREEN_INFO, WIDTH, HEIGHT, COLORS, COLOR_CONTRAST, COLOR_BRIGHT, \
    GENERATED_IMAGE
from util.collector import GENRE, ALBUM, ARTIST, DATE

MAX_CHARS = 30
MAX_CHARS_TITLE = 50

class InfoScreen(Container):
    """ Info screen. Shows file specific info and metadata """

    def __init__(self, util, listener):
        """ Initializer
        
        :param util: utility object
        :Param listener: screen listener
        """        
        self.util = util
        self.config = util.config
        self.factory = Factory(util)
        self.listener = listener
        self.screen_w = self.config[SCREEN_INFO][WIDTH]
        self.screen_h = self.config[SCREEN_INFO][HEIGHT]
        self.lines = 14
        font_vertical_percent = 6
        self.name = KEY_INFO
        self.bounding_box = util.screen_rect
        Container.__init__(self, util, self.bounding_box, (0, 0, 0))
                
        font_size = int((font_vertical_percent * self.bounding_box.h)/100)    
        self.f = util.get_font(font_size)
        
        center_layout = BorderLayout(self.bounding_box)
        center_layout.set_percent_constraints(0, 0, 44, 0)

        left_layout = center_layout.LEFT
        right_layout = center_layout.CENTER

        label_layout = GridLayout(left_layout)
        label_layout.set_pixel_constraints(self.lines, 1)
        label_layout.get_next_constraints()
        bb1 = label_layout.get_next_constraints()

        value_layout = GridLayout(right_layout)
        value_layout.set_pixel_constraints(self.lines, 1)
        value_layout.get_next_constraints()
        bb2 = value_layout.get_next_constraints()

        title_bb = pygame.Rect(bb1.x, bb1.y, bb1.w + bb2.w, bb1.h)
        self.title = self.add_title(title_bb)

        label_layout.get_next_constraints()
        self.add_label(label_layout, 1, self.config[LABELS]["file.size"] + ":")
        self.add_label(label_layout, 2, self.config[LABELS]["sample.rate"] + ":")
        self.add_label(label_layout, 3, self.config[LABELS]["channels"] + ":")
        self.add_label(label_layout, 4, self.config[LABELS]["bits.per.sample"] + ":")
        self.add_label(label_layout, 5, self.config[LABELS]["bit.rate"] + ":")

        label_layout.get_next_constraints()
        self.add_label(label_layout, 6, self.config[LABELS][GENRE] + ":")
        self.add_label(label_layout, 7, self.config[LABELS][ARTIST] + ":")
        self.add_label(label_layout, 8, self.config[LABELS][ALBUM] + ":")
        self.add_label(label_layout, 9, self.config[LABELS][DATE] + ":")

        value_layout.get_next_constraints()
        self.filesize = self.add_value(value_layout, 1)
        self.sample_rate = self.add_value(value_layout, 2)
        self.channels = self.add_value(value_layout, 3)
        self.bits = self.add_value(value_layout, 4)
        self.bit_rate = self.add_value(value_layout, 5)

        value_layout.get_next_constraints()
        self.genre = self.add_value(value_layout, 6)
        self.artist = self.add_value(value_layout, 7)
        self.album = self.add_value(value_layout, 8)
        self.date = self.add_value(value_layout, 9)

        self.values = [self.filesize, self.sample_rate, self.channels, self.bits, self.bit_rate, self.genre, self.artist, self.album, self.date]

    def add_title(self, bb):
        """ Add title component

        :param bb: bounding box

        :return: title component
        """
        fgr = self.util.config[COLORS][COLOR_CONTRAST]
        bgr = (0, 0, 0)
        h = H_ALIGN_CENTER
        v = V_ALIGN_BOTTOM
        f = int((bb.height * 80) / 100)
        name = GENERATED_IMAGE + "title"
        shift = int(bb.h/2)
        title = self.factory.create_output_text(name, bb, bgr, fgr, f, h, v, shift_y=-shift)
        self.add_component(title)

        return title    

    def add_label(self, layout, n, label_name):
        """ Add label component

        :param layout: label layout
        :param n: label number
        :param label_name: label name
        """
        c = layout.get_next_constraints()
        fgr = self.util.config[COLORS][COLOR_BRIGHT]
        bgr = (0, 0, 0)
        h = H_ALIGN_RIGHT
        v = V_ALIGN_BOTTOM
        f = int((c.height * 70) / 100)
        name = GENERATED_IMAGE + "label." + str(n)
        label = self.factory.create_output_text(name, c, bgr, fgr, f, h, v)
        label.set_text(label_name)
        self.add_component(label)

    def add_value(self, layout, n):
        """ Add value component

        :param layout: layout
        :param parent: parent container
        :param n: component number

        :return: value component
        """
        c = layout.get_next_constraints()
        fgr = self.util.config[COLORS][COLOR_CONTRAST]
        bgr = (0, 0, 0)
        h = H_ALIGN_LEFT
        v = V_ALIGN_BOTTOM
        f = int((c.height * 70) / 100)
        name = GENERATED_IMAGE + "value." + str(n)
        gap = int((c.height * 20) / 100)
        value = self.factory.create_output_text(name, c, bgr, fgr, f, halign=h, valign=v, shift_x=gap)
        self.add_component(value)

        return value
    
    def set_current(self, state):
        """ Set info in current screen

        :param state: button state
        """
        meta = self.util.get_file_metadata()

        if not meta:
            self.title.set_text("")
            for v in self.values:
                v.set_text("")
            return

        self.set_value(self.title, meta, "filename", max_chars=MAX_CHARS_TITLE)
        self.set_value(self.filesize, meta, "filesize", unit=self.config[LABELS]["bytes"])
        self.set_value(self.sample_rate, meta, "sample_rate", unit=self.config[LABELS]["hz"])
        self.set_value(self.channels, meta, "channels")
        self.set_value(self.bits, meta, "bits_per_sample")
        self.set_value(self.bit_rate, meta, "bitrate", unit=self.config[LABELS]["kbps"])
        self.set_value(self.genre, meta, GENRE)
        self.set_value(self.artist, meta, ARTIST)
        self.set_value(self.album, meta, ALBUM)
        self.set_value(self.date, meta, DATE)

    def set_value(self, field, meta, key, max_chars=MAX_CHARS, unit=None):
        """ Set text in provided field

        :param field: text field
        :param meta: meta dictionary
        :param key: dictionary key
        :param max_chars: maximum characters in the field
        :param unit: value unit
        """
        try:
            v = meta[key]
            if isinstance(v, numbers.Number):
                if key == "bitrate":
                    v = round(v / 1000)

                n = "{:,}".format(v).replace(",", " ")
                if unit:
                    n += " " + unit
                field.set_text(n)
            else:
                field.set_text(self.truncate(v, max_chars))
        except:
            field.set_text("")

    def truncate(self, s, max_chars):
        """ Truncate string

        :param s: input string
        :param max_chars: maximum string length

        :return: truncated string
        """
        if len(s) > max_chars:
            s = s[0 : max_chars] + "..."
        return s
    
    def handle_event(self, event):
        """ Handle screen events

        :param event: event object
        """
        if (event.type == pygame.MOUSEBUTTONUP and event.button == 1) or \
            (event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.keyboard_key == pygame.K_ESCAPE):
            s = State()
            s.source = KEY_BACK
            self.listener(s)
            self.redraw_observer()

    def exit_screen(self):
        """ Exit screen """       
        pass

    def add_screen_observer(self, redraw_observer):
        """ Add screen observer
        
        :param redraw_observer: observer to redraw the whole screen
        """
        self.redraw_observer = redraw_observer
