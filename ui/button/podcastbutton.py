# Copyright 2019 Peppy Player peppy.player@gmail.com
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

import textwrap

from ui.component import Component
from ui.button.button import Button
from util.keys import MAXIMUM_FONT_SIZE, V_ALIGN, V_ALIGN_TOP, V_OFFSET, H_ALIGN, H_ALIGN_LEFT
from util.config import SCREEN_INFO, WIDTH

class PodcastButton(Button):
    """ Podcast button """
    
    def __init__(self, util, state):
        """ Initializer
        
        :param util: utility object
        :param state: button state
        """        
        Button.__init__(self, util, state)
    
    def add_label(self, state, bb):
        """ Add button label
        
        :param state: button state
        :param bb: bounding box
        """
        if not self.show_label:
            self.add_component(None)
            return
        
        fixed_height = getattr(state, "fixed_height", None)
        if fixed_height:
            font_size = fixed_height
        else:
            font_size = int((bb.h * state.label_text_height)/100.0)
            
        if font_size > self.config[MAXIMUM_FONT_SIZE]:
            font_size = self.config[MAXIMUM_FONT_SIZE]
        
        font = self.util.get_font(font_size)
        text = self.truncate_long_labels(state.l_name, bb, font)
        state.l_name = text
        size = font.size(text)
        label = font.render(text, 1, state.text_color_normal)
        c = Component(self.util, label)
        c.name = state.name + ".label"
        c.text = text
        c.text_size = font_size
        c.text_color_normal = state.text_color_normal
        c.text_color_selected = state.text_color_selected
        c.text_color_disabled = state.text_color_disabled
        c.text_color_current = c.text_color_normal
        
        h_align = getattr(state, H_ALIGN, None)
        if h_align != None:
            if h_align == H_ALIGN_LEFT:
                c.content_x = bb.x
        else:
            c.content_x = bb.x + (bb.width - size[0])/2
        
        v_align = getattr(state, V_ALIGN, None)
        if v_align and v_align == V_ALIGN_TOP:
            v_offset = getattr(state, V_OFFSET, 0)
            if v_offset != 0:
                v_offset = int((bb.height / 100) * v_offset)
                c.content_y = bb.y + v_offset
            else:
                c.content_y = bb.y
        else:
            c.content_y = bb.y + (bb.height - size[1])/2 + 1        
                
        if len(self.components) == 2:
            self.components.append(c)
        else:
            self.components[2] = c
            
        desc = getattr(state, "description", None)
        if desc != None:
            self.add_description(state, desc, c.content_y, size[1], bb, font_size)
            
    def add_description(self, state, desc, title_y, title_h, bb, font_size):
        """ Add podcast description
        
        :param state: button state
        :param desc: description text
        :param title_y: y coordinate
        :param title_h: text height
        :param bb: bounding box
        :param font_size:
        """
        desc_font_size = int(font_size * 0.7)
        font = self.util.get_font(desc_font_size)
        if self.config[SCREEN_INFO][WIDTH] <= 320:
            line_length = 56
        elif self.config[SCREEN_INFO][WIDTH] > 320 and self.config[SCREEN_INFO][WIDTH] <= 480:
            line_length = 58
        else:
            line_length = 64
        lines = textwrap.wrap(desc, line_length)
        
        for n, line in enumerate(lines[0:5]):
            label = font.render(line, 1, state.text_color_normal)
            c = Component(self.util, label)
            c.name = "desc." + str(title_y) + str(n)
            c.text = line
            c.text_size = desc_font_size
            c.text_color_normal = state.text_color_normal
            c.text_color_selected = state.text_color_selected
            c.text_color_disabled = state.text_color_disabled
            c.text_color_current = c.text_color_normal
            c.content_x = bb.x
            c.content_y = title_y + title_h + (n * desc_font_size)
            self.components.append(c)
    