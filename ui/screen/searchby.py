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
from ui.menu.searchbymenu import SearchByMenu
from ui.navigator.searchby import SearchByNavigator
from util.keys import KEY_HOME

class SearchByScreen(Screen):
    """ Radio Browser Search By Screen """
    
    def __init__(self, util, listeners):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        Screen.__init__(self, util, "radio-browser", PERCENT_TOP_HEIGHT)
        self.listeners = listeners
        
        self.menu = SearchByMenu(util, None, self.layout.CENTER)
        self.menu.add_listener(self.change_item) 
        self.add_menu(self.menu)
        
        self.navigator = SearchByNavigator(util, self.layout.BOTTOM, listeners)
        self.add_navigator(self.navigator)

        self.link_borders()
        home = self.navigator.get_button_by_name(KEY_HOME)
        home.set_selected(True)

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.menu.add_menu_observers(update_observer, redraw_observer)
        self.navigator.add_observers(update_observer, redraw_observer)

    def change_item(self, state):
        """ Change menu item
        
        :param state: button state
        """
        self.listeners[state.name](state)
