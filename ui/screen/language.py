# Copyright 2016-2023 Peppy Player peppy.player@gmail.com
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

from ui.navigator.language import LanguageNavigator
from ui.screen.screen import Screen, PERCENT_TOP_HEIGHT
from ui.menu.languagemenu import LanguageMenu
from util.config import LABELS, LANGUAGE

class LanguageScreen(Screen):
    """ Genre Screen. Extends base Screen class """
    
    def __init__(self, util, change_language, listeners):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT)
        self.language_menu = LanguageMenu(util, None, self.layout.CENTER)
        self.language_menu.add_listener(change_language)   
        self.add_menu(self.language_menu)

        self.label = util.config[LABELS][LANGUAGE]
        l_name = util.get_current_language_translation()
        txt = self.label + ": " + l_name
        self.screen_title.set_text(txt)

        self.navigator = LanguageNavigator(util, self.layout.BOTTOM, listeners)
        self.add_navigator(self.navigator)

        self.link_borders()

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.language_menu.add_menu_observers(update_observer, redraw_observer, release=False)
        self.navigator.add_observers(update_observer, redraw_observer)
