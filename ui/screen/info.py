# Copyright 2020-2023 Peppy Player peppy.player@gmail.com
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
from ui.container import Container
from util.keys import KEY_BACK, USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, H_ALIGN_RIGHT, V_ALIGN_BOTTOM, H_ALIGN_LEFT, \
    H_ALIGN_CENTER, kbd_keys, KEY_SELECT
from util.config import SCREEN_INFO, WIDTH, HEIGHT, COLORS, COLOR_CONTRAST, COLOR_BRIGHT, \
    GENERATED_IMAGE

MAX_CHARS = 30
MAX_CHARS_TITLE = 40

class InfoScreen(Container):
    """ Info screen. Shows file/station specific info and metadata """

    def __init__(self, name, util, listener, labels, meta_keys, units, lines, gap_after, get_metadata_function):
        """ Initializer
        
        :param name: screen name
        :param util: utility object
        :param listener: screen listener
        :param labels: list of screen lables
        :param meta_keys: list of metadata keys
        :param lines: screen lines
        :param gap_after: gap between lines after this number of lines
        :param get_metadata_function: metadata getter function
        """
        self.name = name
        self.util = util
        self.config = util.config
        self.factory = Factory(util)
        self.listener = listener
        self.labels = labels
        self.meta_keys = meta_keys
        self.units = units
        self.get_metadata_function = get_metadata_function

        self.bg = self.util.get_background(self.name)
        self.bgr_type = self.bg[0]
        self.bgr = self.bg[1]
        self.bgr_key = self.bg[5]

        self.screen_w = self.config[SCREEN_INFO][WIDTH]
        self.screen_h = self.config[SCREEN_INFO][HEIGHT]
        self.lines = lines
        font_vertical_percent = 6
        self.gap_after = gap_after
        self.bounding_box = util.screen_rect
        Container.__init__(self, util, self.bounding_box, background=self.bg[1], content=self.bg[2], image_filename=self.bg[3])
                
        font_size = int((font_vertical_percent * self.bounding_box.h)/100)    
        self.f = util.get_font(font_size)
        
        center_layout = BorderLayout(self.bounding_box)
        center_layout.set_percent_constraints(0, 0, 50, 0)

        left_layout = center_layout.LEFT
        right_layout = center_layout.CENTER

        self.label_layout = GridLayout(left_layout)
        self.label_layout.set_pixel_constraints(self.lines, 1)
        self.label_layout.get_next_constraints()
        bb1 = self.label_layout.get_next_constraints()

        self.value_layout = GridLayout(right_layout)
        self.value_layout.set_pixel_constraints(self.lines, 1)
        self.value_layout.get_next_constraints()
        bb2 = self.value_layout.get_next_constraints()

        title_bb = pygame.Rect(bb1.x, bb1.y, bb1.w + bb2.w, bb1.h)
        self.title = self.add_title(title_bb)

        self.max_label_length = 0
        self.max_value_length = 0

        self.label_comps = self.add_labels()
        self.values = self.add_values()

    def add_labels(self):
        """ Add all labels components """

        labels = []

        self.label_layout.get_next_constraints()
        for i, n in enumerate(self.labels):
            if i == self.gap_after:
                self.label_layout.get_next_constraints()
            labels.append(self.add_label(self.label_layout, i + 1, n + ":"))

        return labels

    def add_values(self):
        """ Add all values components """

        values = []

        self.value_layout.get_next_constraints()
        for i, _ in enumerate(self.labels):
            if i == self.gap_after:
                self.value_layout.get_next_constraints()
            values.append(self.add_value(self.value_layout, i + 1))

        return values

    def add_title(self, bb):
        """ Add title component

        :param bb: bounding box

        :return: title component
        """
        fgr = self.util.config[COLORS][COLOR_CONTRAST]
        h = H_ALIGN_CENTER
        v = V_ALIGN_BOTTOM
        f = int((bb.height * 80) / 100)
        name = GENERATED_IMAGE + "title"
        shift = int(bb.h/2)
        title = self.factory.create_output_text(name, bb, (0, 0, 0, 0), fgr, f, h, v, shift_y=-shift)
        self.add_component(title)

        return title    

    def add_label(self, layout, n, label_name):
        """ Add label component

        :param layout: label layout
        :param n: label number
        :param label_name: label name

        :return: label component
        """
        c = layout.get_next_constraints()
        fgr = self.util.config[COLORS][COLOR_BRIGHT]
        h = H_ALIGN_RIGHT
        v = V_ALIGN_BOTTOM
        f = int((c.height * 70) / 100)
        name = GENERATED_IMAGE + "label." + str(n)
        label = self.factory.create_output_text(name, c, (0, 0, 0, 0), fgr, f, h, v)
        label.set_text(label_name, False)
        self.add_component(label)

        label_size = label.components[1].content.get_size()
        if label_size[0] > self.max_label_length:
            self.max_label_length = label_size[0]

        return label

    def add_value(self, layout, n):
        """ Add value component

        :param layout: layout
        :param parent: parent container
        :param n: component number

        :return: value component
        """
        c = layout.get_next_constraints()
        fgr = self.util.config[COLORS][COLOR_CONTRAST]
        h = H_ALIGN_LEFT
        v = V_ALIGN_BOTTOM
        f = int((c.height * 70) / 100)
        name = GENERATED_IMAGE + "value." + str(n)
        gap = int((c.height * 20) / 100)
        value = self.factory.create_output_text(name, c, (0, 0, 0, 0), fgr, f, halign=h, valign=v, shift_x=gap)
        self.add_component(value)

        return value

    def set_current(self, _):
        """ Set info in current screen

        :param state: button state
        """
        meta = self.get_metadata_function()
        self.max_value_length = 0

        if not meta:
            self.title.set_text("")
            for v in self.values:
                v.set_text("")
            return

        self.set_value(self.title, meta, self.meta_keys[0], max_chars=MAX_CHARS_TITLE)

        for i, n in enumerate(self.values):
            unit = ""
            key = self.meta_keys[i + 1]
            try:
                unit = self.units[key]
            except:
                pass
            self.set_value(n, meta, key, unit=unit)

            label_size = n.components[1].content.get_size()
            if label_size[0] > self.max_value_length:
                self.max_value_length = label_size[0]

        self.align()

    def align(self):
        max_width = self.max_label_length + self.max_value_length
        screen_width = self.config[SCREEN_INFO][WIDTH]
        margin = (screen_width - max_width)/2
        middle_x = margin + self.max_label_length

        for n in self.label_comps:
            n.components[1].content_x = middle_x - n.components[1].content.get_size()[0] - 8

        for n in self.values:
            n.components[1].content_x = middle_x

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
            (event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.keyboard_key == kbd_keys[KEY_SELECT] and event.action == pygame.KEYUP):
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
