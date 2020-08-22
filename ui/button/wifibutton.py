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
from util.keys import MAXIMUM_FONT_SIZE, V_ALIGN, V_ALIGN_TOP, V_OFFSET, H_ALIGN, H_ALIGN_LEFT, H_OFFSET
from util.config import SCREEN_INFO, WIDTH

class WiFiButton(Button):
    """ Wi-Fi button """

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

        font_size = state.fixed_height
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
                c.content_x = bb.x + getattr(state, H_OFFSET, 0)
        else:
            c.content_x = bb.x + (bb.width - size[0]) / 2

        v_align = getattr(state, V_ALIGN, None)
        if v_align and v_align == V_ALIGN_TOP:
            v_offset = getattr(state, V_OFFSET, 0)
            if v_offset != 0:
                v_offset = int((bb.height / 100) * v_offset)
                c.content_y = bb.y + v_offset
            else:
                c.content_y = bb.y
        else:
            c.content_y = bb.y + (bb.height - size[1]) / 2 + 1

        if len(self.components) == 2:
            self.components.append(c)
        else:
            self.components[2] = c
