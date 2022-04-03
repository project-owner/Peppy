# Copyright 2022 Peppy Player peppy.player@gmail.com
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

from ui.player.airplayplayer import AirplayPlayerScreen

class BluetoothSinkScreen(AirplayPlayerScreen):
    """ Bluetooth Sink Screen """
    
    def __init__(self, listeners, util, voice_assistant, volume_control):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object
        :param voice_assistant: voice assistant
        :param volume_control: volume control
        """
        AirplayPlayerScreen.__init__(self, listeners, util, None, voice_assistant, volume_control)
        self.volume.components[1] = None
        self.volume.components[2] = None
        self.screen_title.set_text("Bluetooth Sink")
        s = self.left_button.state
        s.show_img = False
        self.left_button.set_state(s)
        s = self.right_button.state
        s.show_img = False
        self.right_button.set_state(s)

        bb = self.play_button.states[0].bounding_box
        b = self.factory.create_disabled_button(bb, "play", 0.4)
        self.play_button.states[1] = b.state
        self.play_button.draw_state(1)
        self.play_button.clean_draw_update()        

    def go_right(self, state):
        """ Switch to the next track
        
        :param state: not used state object
        """
        pass

    def go_left(self, state):
        """ Switch to the previous track
        
        :param state: not used state object
        """
        pass
