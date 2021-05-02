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

from ui.layout.gridlayout import GridLayout
from ui.factory import Factory
from ui.screen.screen import Screen, PERCENT_TOP_HEIGHT
from ui.menu.latinabcmenu import LatinAbcMenu
from util.keys import KEY_CALLBACK
from ui.navigator.latinkeyboard import LatinKeyboardNavigator

IMAGE_SIZE_PERCENT = 60

class LatinAbcScreen(Screen):
    """ Ltin Alphabet Screen """
    
    def __init__(self, title, util, listeners, voice_assistant):
        """ Initializer
        
        :param title: screen title
        :param util: utility object
        :param listener: screen menu event listener
        :param voice_assistant: voice assistant
        """
        Screen.__init__(self, util, None, PERCENT_TOP_HEIGHT, voice_assistant)
        self.screen_title.set_text(title)
        self.factory = Factory(util)
        self.abc_menu = LatinAbcMenu(util, listeners[KEY_CALLBACK], (0, 0, 0, 0), self.layout.CENTER)
        self.abc_menu.add_listener(listeners[KEY_CALLBACK]) 
        self.add_menu(self.abc_menu)
        
        layout = GridLayout(self.layout.BOTTOM)
        layout.set_pixel_constraints(1, 4, 1, 0)
        layout.current_constraints = 0

        self.navigator = LatinKeyboardNavigator(util, layout, listeners)
        self.add_navigator(self.navigator)

        self.link_borders()
        self.link_borders_custom()

    def link_borders_custom(self):
        margin = 10
        self.navigator.components[0].exit_left_x = self.abc_menu.buttons['Z'].bounding_box.x + margin
        self.navigator.components[0].exit_left_y = self.abc_menu.buttons['Z'].bounding_box.y + margin
        self.navigator.components[0].exit_top_x = self.abc_menu.buttons['V'].bounding_box.x + margin
        self.navigator.components[0].exit_top_y = self.abc_menu.buttons['V'].bounding_box.y + margin
        # self.abc_menu.buttons['U'].exit_right_x = self.abc_menu.buttons['V'].bounding_box.x + margin
        # self.abc_menu.buttons['U'].exit_right_y = self.abc_menu.buttons['V'].bounding_box.y + margin

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.abc_menu.add_menu_observers(update_observer, redraw_observer)
        self.navigator.add_observers(update_observer, redraw_observer)
        