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

from ui.factory import Factory
from ui.menu.menu import Menu
from util.keys import CURRENT, KEY_LANGUAGE, ORDER_LANGUAGE_MENU, NAME
from util.util import LANGUAGE_ITEMS, ENGLISH, GERMAN, FRENCH, RUSSIAN
from util.config import USAGE, USE_VOICE_ASSISTANT

class LanguageMenu(Menu):
    """ Language Menu class. Extends base Menu class """
    
    def __init__(self, util, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """    
        self.factory = Factory(util)
        m = self.factory.create_language_menu_button
        self.util = util
        Menu.__init__(self, self.util, bgr, bounding_box, 2, 2, create_item_method=m)
        self.config = self.util.config
        language = self.config[CURRENT][KEY_LANGUAGE]
        self.languages = self.util.load_menu(LANGUAGE_ITEMS, NAME)
        self.set_voice_commands(language)
        self.set_items(self.languages, 0, self.change_language, False, self.config[ORDER_LANGUAGE_MENU])
        self.current_language = self.languages[language]
        self.item_selected(self.current_language) 
    
    def set_voice_commands(self, language):
        """ Set menu voice commands
        
        :param language: new language
        """
        if not self.config[USAGE][USE_VOICE_ASSISTANT]:
            return
        
        self.util.voice_commands = self.util.all_voice_commands[language]
        commands = self.util.voice_commands
        self.languages[ENGLISH].voice_commands = [commands["VA_ENGLISH"].strip()]
        self.languages[GERMAN].voice_commands = [commands["VA_GERMAN"].strip()]
        self.languages[FRENCH].voice_commands = [commands["VA_FRENCH"].strip()]
        self.languages[RUSSIAN].voice_commands = [commands["VA_RUSSIAN"].strip()]
    
    def change_language(self, state):
        """ Change language event listener
        
        :param state: button state
        """
        if not self.visible:
            return
        self.current_language = state
        self.set_voice_commands(state.name)      
        self.notify_listeners(state)
