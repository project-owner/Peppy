# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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
from ui.menu.languagemenu import LanguageMenu
from util.config import LANGUAGE
from ui.factory import Factory

class LanguageScreen(Screen):
    """ Genre Screen. Extends base Screen class """
    
    def __init__(self, util, change_language, listeners, voice_assistant):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        Screen.__init__(self, util, LANGUAGE, PERCENT_TOP_HEIGHT, voice_assistant)
        self.language_menu = LanguageMenu(util, (0, 0, 0), self.layout.CENTER)
        self.language_menu.add_listener(change_language)   
        self.add_menu(self.language_menu)
        
        factory = Factory(util)
        self.menu_buttons = factory.create_home_player_buttons(self, self.layout.BOTTOM, listeners)
        self.home_button = self.menu_buttons[0]
        self.player_button = self.menu_buttons[1]
    
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.language_menu.add_menu_observers(update_observer, redraw_observer, release=False)
        for b in self.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)
