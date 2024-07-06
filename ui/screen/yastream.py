# Copyright 2024 Peppy Player peppy.player@gmail.com
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

from ui.screen.screen import Screen, PERCENT_TOP_HEIGHT
from ui.menu.yastream import YaStreamMenu
from ui.navigator.yastream import YaStreamNavigator
from util.config import YA_STREAM
from util.keys import *

class YaStreamScreen(Screen):
    """ YA Stream Screen """

    def __init__(self, util, listeners):
        """ Initializer

        :param util: utility object
        :param listener: screen menu event listener
        """
        Screen.__init__(self, util, YA_STREAM, PERCENT_TOP_HEIGHT)

        self.menu = YaStreamMenu(util, (0, 0, 0, 0), self.layout.CENTER, font_size=self.font_size)
        self.menu.buttons[KEY_SEARCH_BY_NAME].add_release_listener(listeners[KEY_SEARCH_BY_NAME])
        self.menu.buttons[KEY_PLAYLISTS].add_release_listener(listeners[KEY_PLAYLISTS])
        self.add_menu(self.menu)

        self.layout.BOTTOM.y -= 1
        self.layout.BOTTOM.h += 1
        self.navigator = YaStreamNavigator(util, self.layout.BOTTOM, listeners)
        self.add_navigator(self.navigator)

        self.link_borders()       

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers

        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)

        self.menu.add_menu_observers(update_observer, redraw_observer)
        self.navigator.add_observers(update_observer, redraw_observer)
