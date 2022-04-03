# Copyright 2021 Peppy Player peppy.player@gmail.com
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

from pygame import Rect
from ui.state import State
from ui.button.button import Button
from ui.player.radioplayer import RadioPlayerScreen
from util.config import CURRENT, STREAM
from util.keys import kbd_keys, KEY_SELECT, KEY_STREAM_BROWSER, KEY_HOME
from util.util import V_ALIGN_BOTTOM

class StreamPlayerScreen(RadioPlayerScreen):
    """ The Stream Player Screen """
    
    def __init__(self, util, listeners, voice_assistant=None, volume_control=None):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        :param voice_assistant: the voice assistant
        :param volume_control: the volume control
        """
        self.util = util
        self.config = util.config
        self.bounding_box = util.screen_rect
        self.image_util = util.image_util
        self.listeners = listeners

        RadioPlayerScreen.__init__(self, util, listeners, voice_assistant, volume_control)
    
    def set_custom_button(self):
        """ Set the custom buttom """

        self.custom_button = self.factory.create_stream_button(self.custom_button_layout)
        self.right_panel.add_component(self.custom_button)

    def set_current_item(self, index):
        """ Specific for each player. Sets config item """

        self.config[CURRENT][STREAM] = index

    def set_center_button(self):
        """ Set the center button """

        self.playlist = self.util.get_stream_playlist()

        if self.playlist == None or len(self.playlist) == 0:
            self.clean_center_button()
            self.update_arrow_button_labels()
            self.set_title("")
            self.stop()
            return

        self.current_index = self.config[CURRENT][STREAM]

        if self.current_index >= len(self.playlist):
            self.current_index = len(self.playlist) - 1    
        
        self.current_state = self.playlist[self.current_index]
        self.current_state.bounding_box = self.layout.CENTER

        if not hasattr(self.current_state, "icon_base"):
            self.util.add_icon(self.current_state)
        
        if self.center_button == None:
            self.center_button = self.get_center_button(self.current_state)
            self.current_button = self.center_button
            self.add_component(self.center_button)
        else:
            button = self.get_center_button(self.current_state)
            self.center_button.state = button.state
            self.center_button.components = button.components
        
        self.center_button.selected = True
        self.center_button.add_release_listener(self.listeners[KEY_STREAM_BROWSER])
        
        self.center_button.clean_draw_update()
        img = self.center_button.components[1]
        self.logo_button_content = (img.image_filename, img.content, img.content_x, img.content_y)

        self.update_arrow_button_labels()
        self.set_title(self.current_state)

    def get_center_button(self, s):
        """ Create stream button

        :param s: button state

        :return: center stream button
        """
        bb = Rect(self.layout.CENTER.x + 1, self.layout.CENTER.y + 1, self.layout.CENTER.w - 1, self.layout.CENTER.h - 1)
        if not hasattr(s, "icon_base"):
            self.util.add_icon(s)

        state = State()
        state.icon_base = s.icon_base
        self.factory.set_state_scaled_icons(s, bb)
        state.index = s.index
        state.scaled = getattr(s, "scaled", False)
        state.icon_base_scaled = s.icon_base_scaled
        state.name = "stream." + s.name
        state.l_name = s.l_name
        state.url = s.url
        state.keyboard_key = kbd_keys[KEY_SELECT]
        state.bounding_box = bb
        state.img_x = bb.x
        state.img_y = bb.y
        state.auto_update = False
        state.show_bgr = True
        state.show_img = True
        state.logo_image_path = s.image_path
        state.image_align_v = V_ALIGN_BOTTOM
        state.comparator_item = self.current_state.comparator_item
        button = Button(self.util, state)

        img = button.components[1]
        self.logo_button_content = (img.image_filename, img.content, img.content_x, img.content_y)

        return button

    def set_current(self, state=None):
        """ Set the current screen state

        :param state: the state object
        """
        if state == None:
            self.clean_center_button()
            self.update_arrow_button_labels()
            self.set_title("")
            self.stop_player()
            self.current_button = self.home_button
            self.home_button.clean_draw_update()
            return

        if not hasattr(state, "source"):
            return

        src = getattr(state, "source", None)

        if src == KEY_HOME:
            if not hasattr(self, "current_button"): # after changing language
                self.home_button.set_selected(True)
                self.home_button.clean_draw_update()
                self.current_button = self.home_button
            if state.change_mode:
                self.start_playback()
        elif src == KEY_STREAM_BROWSER:
            if self.center_button and self.center_button.state.url != state.url:
                self.start_playback()
