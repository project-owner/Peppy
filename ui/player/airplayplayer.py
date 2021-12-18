# Copyright 2019-2021 Peppy Player peppy.player@gmail.com
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

from ui.player.fileplayer import FilePlayerScreen
from ui.state import State

class AirplayPlayerScreen(FilePlayerScreen):
    """ AirPlay Player Screen """
    
    def __init__(self, listeners, util, get_current_playlist, voice_assistant, volume_control, change_screensaver_image=None, next=None, previous=None):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object
        :param get_current_playlist: current playlist getter
        :param voice_assistant:   voice assistant
        :param volume control: volume control
        :param player_stop: stop player function
        :param next: next track function
        :param previous: previous track function
        """
        FilePlayerScreen.__init__(self, listeners, util, get_current_playlist, voice_assistant, volume_control, False, False, False, False)
        self.change_screensaver_image = change_screensaver_image
        self.next = next
        self.previous = previous
        self.center_button.state.name = "file.button"
        self.volume.check_pause = False
        self.volume.handle_knob_events = False
        self.screen_title.set_text("AirPlay")
        self.volume_visible = True

        self.toggle_time_volume()
        bb = self.custom_button.states[0].bounding_box
        b = self.factory.create_disabled_button(bb, "time", 0.4)
        self.custom_button.states[1] = b.state
        self.custom_button.draw_state(1)
        self.custom_button.clean_draw_update()
        self.custom_button.start_listeners = []
        self.link_borders()
        
    def set_current(self, new_track=False, state=None):
        """ Set current file or playlist
        
        :param new_track: True - new audio file
        :param state: button state
        """
        pass        

    def handle_metadata(self, state=None):
        """ Handle metadata UI callback

        :param state: metadata object
        """
        if not state:
            return

        if "picture" in state.keys():
            img = ("current_shairport_image", state["picture"])
            self.set_center_button(img)
            self.center_button.clean_draw_update()
            state = State()
            state.icon_base = img
            state.full_screen_image = img
            self.change_screensaver_image(state)
        elif "current_title" in state.keys():
            title = state["current_title"]
            self.screen_title.set_text(title)
        elif "volume" in state.keys():
            volume = state["volume"]
            self.volume.set_position(volume)
            self.volume.update_position()
            self.volume.notify_slide_listeners()
        elif "stream" in state.keys():
            type = state["stream"]            
            if type == "end":
                self.play_button.draw_state(1)
            elif type == "begin":
                self.play_button.draw_state(0)
        elif "Time" in state.keys() and "seek_time" in state.keys():
            state["state"] = "running"

        if self.visible:
            if self.update_web_observer:
                self.update_web_observer()

    def go_right(self, state):
        """ Switch to the next track
        
        :param state: not used state object
        """
        self.next()

    def go_left(self, state):
        """ Switch to the previous track
        
        :param state: not used state object
        """
        self.previous()

    def is_valid_mode(self):
        """ Check that current mode is valid mode
        
        :return: True - airplay mode is valid
        """
        return True
    