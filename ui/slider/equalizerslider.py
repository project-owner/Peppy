# Copyright 2016-2020 Peppy Player peppy.player@gmail.com
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

import time

from timeit import default_timer as timer
from ui.component import Component
from ui.container import Container
from ui.slider.slider import Slider
from ui.layout.borderlayout import BorderLayout
from util.config import USAGE, USE_WEB, COLORS, COLOR_BRIGHT
from ui.state import State

class EqualizerSlider(Container):
    """ Time slider component """

    def __init__(self, f, id, util, name, bgr, slider_color, img_knob, img_knob_on, key_incr, key_decr, key_knob, bb, listener, label):
        """ Initializer
        
        :param id: band ID
        :param util: utility object
        :param name: slider name
        :param bgr: slider background color
        :param slider_color: slider center line color
        :param img_knob: knob image
        :param img_knob_on: knob image in on state
        :param key_incr: keyboard key associated with slider increment action
        :param key_decr: keyboard key associated with slider decrement action
        :param key_knob: keyboard key associated with single click on knob
        :param bb: slider bounding box
        """
        Container.__init__(self, util, background=bgr, bounding_box=bb, content=None)
        self.util = util
        self.config = util.config
        self.bgr = bgr
        
        self.VALUE_LAYER = 2
        self.LABEL_LAYER = 1
        
        layout = BorderLayout(bb)
        layout.set_percent_constraints(10.0, 10.0, 0.0, 0.0)
        
        self.value_name = name + ".value." + str(id)
        self.label_name = name + ".label." + str(id)
        self.value_layout = layout.TOP
        self.label_layout = layout.BOTTOM
        self.label_layout.y -= 1
        self.label_layout.h += 2
        
        self.slider = Slider(util, "slider." + str(id), bgr, slider_color, img_knob, img_knob_on, None, key_incr, key_decr, key_knob, layout.CENTER)
        self.slider.add_slide_listener(listener)
        self.add_component(self.slider)
        
        height = 60
        font_size = int((self.value_layout.h * height)/100.0)
        c = self.config[COLORS][COLOR_BRIGHT]
        self.top = f.create_output_text("top.label." + str(id), self.value_layout, bgr, c, font_size)
        self.bottom = f.create_output_text("bottom.label." + str(id), self.label_layout, bgr, c, font_size)        
        self.bottom.set_text(label)

        self.add_component(self.top)
        self.add_component(self.bottom)
        
        self.seek_listeners = []
        self.update_seek_listeners = True
        self.use_web = self.config[USAGE][USE_WEB]
        
    def set_value(self, v):
        self.top.set_text(v)

        if self.use_web and getattr(self, "web_seek_listener", None):
            s = State()
            s.event_origin = self
            s.seek_time_label = v
            self.web_seek_listener(s)
