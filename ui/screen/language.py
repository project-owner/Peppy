# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
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
from util.util import KEY_LANGUAGE
from ui.factory import Factory

class LanguageScreen(Screen):
    """ Genre Screen. Extends base Screen class """
    
    def __init__(self, util, change_language, listeners):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        Screen.__init__(self, util, KEY_LANGUAGE, PERCENT_TOP_HEIGHT)
        self.language_menu = LanguageMenu(util, (0, 0, 0), self.layout.CENTER)
        self.language_menu.add_listener(change_language)   
        self.add_menu(self.language_menu)
        
        factory = Factory(util)
        buttons = factory.create_home_player_buttons(self, self.layout.BOTTOM, listeners)
        self.home_button = buttons[0]
        self.player_button = buttons[1]
    
