# Copyright 2018 Peppy Player peppy.player@gmail.com
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

from ui.container import Container
from ui.layout.gridlayout import GridLayout
from ui.factory import Factory
from util.keys import KEY_HOME, KEY_PLAYER, KEY_MUTE, KEY_PLAY_PAUSE
from util.config import SLEEP_NOW

class TimerNavigator(Container):
    """ Timer navigator menu """
    
    def __init__(self, util, bounding_box, listeners, bgr):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        :param bgr: menu background        
        """ 
        Container.__init__(self, util)
        self.factory = Factory(util)
        self.name = "timer.navigator"
        self.content = bounding_box
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.menu_buttons = []
        self.bgr = bgr

        self.layout = GridLayout(bounding_box)            
        self.layout.set_pixel_constraints(1, 3, 1, 0)        
        self.layout.current_constraints = 0
        self.image_size = 64
        
        self.home_button = self.add_button(KEY_HOME, KEY_HOME, listeners[KEY_HOME])
        self.sleep_now_button = self.add_button(SLEEP_NOW, KEY_MUTE, listeners[SLEEP_NOW])
        self.player_button = self.add_button(KEY_PLAYER, KEY_PLAY_PAUSE, listeners[KEY_PLAYER])
        
    def add_button(self, img_name, kbd_key, listener):
        """ Add button to the menu
        
        :param img_name: button image name
        :param kbd_key: keyboard key assigned to the button
        :param listener: button listener
        """
        constr = self.layout.get_next_constraints()
        button = self.factory.create_button(img_name, kbd_key, constr, listener, self.bgr, image_size_percent=self.image_size)
        self.add_component(button)
        self.menu_buttons.append(button)
        return button
        
    def add_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        for b in self.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)       
