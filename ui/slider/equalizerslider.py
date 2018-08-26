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

    def __init__(self, id, util, name, bgr, slider_color, img_knob, img_knob_on, key_incr, key_decr, key_knob, bb, listener, label):
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
        Container.__init__(self, util, background=bgr, bounding_box=bb)
        self.util = util
        self.config = util.config
        
        self.VALUE_LAYER = 3
        self.LABEL_LAYER = 2
        
        comp = Component(self.util, bb)
        comp.name = name + ".bgr." + str(id)
        comp.bgr = bgr
        self.add_component(comp)
        
        layout = BorderLayout(bb)
        layout.set_percent_constraints(10.0, 10.0, 0.0, 0.0)
        
        self.value_name = name + ".value." + str(id)
        self.label_name = name + ".label." + str(id)
        self.value_layout = layout.TOP
        self.label_layout = layout.BOTTOM
        
        k = 1.75
        w = self.label_layout.w
        h = self.label_layout.h
        self.label_layout.w *= k
        self.label_layout.h *= k
        self.label_layout.x -= (self.label_layout.w - w) / 2
        self.label_layout.y -= (self.label_layout.h - h) / 2
        
        k = 1.6
        w = self.value_layout.w
        h = self.value_layout.h
        self.value_layout.w *= k
        self.value_layout.h *= k
        self.value_layout.x -= (self.value_layout.w - w) / 2
        self.value_layout.y -= (self.value_layout.h - h) / 2 - 2
        
        self.slider = Slider(util, "slider." + str(id), bgr, slider_color, img_knob, img_knob_on, None, key_incr, key_decr, key_knob, layout.CENTER)
        self.slider.add_slide_listener(listener)
        self.value = "0"        
        self.add_component(self.slider)
        
        c = Component(self.util, None) # init total time layer
        self.add_component(c)
        c = Component(self.util, None) # init current time layer
        self.add_component(c)
             
        self.seek_listeners = []
        self.update_seek_listeners = True
        self.use_web = self.config[USAGE][USE_WEB]
        
        self.set_labels(self.label_name, label, self.label_layout, self.LABEL_LAYER)
        self.set_labels(self.value_name, self.value, self.value_layout, self.VALUE_LAYER)
        
        self.use_web = self.config[USAGE][USE_WEB]
    
    def set_value(self, v):
        self.set_labels(self.value_name, v, self.value_layout, self.VALUE_LAYER)
    
    def set_labels(self, name, v, bb, layer_num):
        font_size = int((bb.h * 45)/100.0)
        font = self.util.get_font(font_size)
        size = font.size(v)
        label = font.render(v, 1, self.config[COLORS][COLOR_BRIGHT])
        c = Component(self.util, label)
        c.bgr = (255, 0, 0)
        c.name = name
        c.text = v
        c.text_size = font_size
        c.text_color_current = self.config[COLORS][COLOR_BRIGHT]
        c.content_x = bb.x + (bb.width - size[0])/2
        c.content_y = bb.y + (bb.height - size[1])/2 
        self.components[layer_num] = c
        
        if self.visible:   
            self.draw()
            self.update()
            
            if self.use_web and getattr(self, "web_seek_listener", None):
                s = State()
                s.event_origin = self
                s.seek_time_label = v
                self.web_seek_listener(s)
            