# Copyright 2020-2021 Peppy Player peppy.player@gmail.com
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
from ui.menu.collectionmenu import CollectionMenu
from ui.navigator.collection import CollectionNavigator
from util.config import LABELS, LOADING, COLLECTION

class CollectionScreen(Screen):
    """ Collection Screen """
    
    def __init__(self, util, listeners, voice_assistant):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        :param voice_assistant: voice assistant
        """
        Screen.__init__(self, util, COLLECTION, PERCENT_TOP_HEIGHT, voice_assistant)
        
        self.set_loading(text=util.config[LABELS][LOADING])
        self.menu = CollectionMenu(util, (0, 0, 0, 0), self.layout.CENTER, font_size=self.font_size)
        self.reset_loading()
        self.menu.add_listener(listeners[COLLECTION])
        self.add_menu(self.menu)
        
        self.navigator = CollectionNavigator(util, self.layout.BOTTOM, listeners)
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
        