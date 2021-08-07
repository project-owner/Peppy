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

from ui.navigator.switch import SwitchNavigator
from ui.screen.screen import Screen, PERCENT_TOP_HEIGHT
from ui.menu.switchmenu import SwitchMenu
from util.config import LABELS
from util.keys import KEY_SWITCH

class SwitchScreen(Screen):
    """ Disk Power Switch Screen """
    
    def __init__(self, util, listeners):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT)
        self.switch_menu = SwitchMenu(util, None, self.layout.CENTER)
        self.add_menu(self.switch_menu)

        config = util.config
        self.label = config[LABELS][KEY_SWITCH]
        self.screen_title.set_text(self.label)

        self.navigator = SwitchNavigator(util, self.layout.BOTTOM, listeners)
        self.add_navigator(self.navigator)

        self.link_borders()

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.switch_menu.add_menu_observers(update_observer, redraw_observer, release=False)
        self.navigator.add_observers(update_observer, redraw_observer)
