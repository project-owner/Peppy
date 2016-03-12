# Copyright 2016 Peppy Player peppy.player@gmail.com
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
from util.keys import CURRENT, LANGUAGE, ORDER_LANGUAGE_MENU, NAME
from util.util import LANGUAGE_ITEMS

class LanguageMenu(Menu):
    """ Language Menu class. Extends base Menu class """
    
    def __init__(self, util, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param bgr: menu background
        :param bb: bounding box
        """    
        self.factory = Factory(util)
        m = self.factory.create_language_menu_button
        Menu.__init__(self, util, bgr, bounding_box, 2, 2, create_item_method=m)
        config = util.config
        language = config[CURRENT][LANGUAGE]
        self.languages = util.load_menu(LANGUAGE_ITEMS, NAME)
        self.set_items(self.languages, 0, self.change_language, False, config[ORDER_LANGUAGE_MENU])
        self.current_language = self.languages[language]
        self.item_selected(self.current_language) 
    
    def change_language(self, state):
        """ Change language event listener
        
        :param state: button state
        """
        if not self.visible:
            return
        self.current_language = state        
        self.notify_listeners(state)
