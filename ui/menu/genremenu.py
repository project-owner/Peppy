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

from ui.menu.menu import Menu
from ui.factory import Factory
from util.keys import CURRENT, PLAYLIST, ORDER_GENRE_MENU, GENRE
from util.util import GENRE_ITEMS

class GenreMenu(Menu):
    """ Genre Menu class. Extends base Menu class """
    
    def __init__(self, util, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param bgr: menu background
        :param bb: bounding box
        """        
        self.factory = Factory(util)
        m = self.factory.create_genre_menu_button
        Menu.__init__(self, util, bgr, bounding_box, 3, 3, create_item_method=m)
        self.config = util.config
        current_genre_name = self.config[CURRENT][PLAYLIST]
        self.genres = util.load_menu(GENRE_ITEMS, GENRE)       
        self.set_items(self.genres, 0, self.change_genre, False, self.config[ORDER_GENRE_MENU])
        self.current_genre = self.genres[current_genre_name]
        self.item_selected(self.current_genre)
    
    def change_genre(self, state):
        """ Change genre event listener
        
        :param state: button state
        """
        if not self.visible:
            return
        self.current_genre = state
        self.config[CURRENT][PLAYLIST] = state.genre
        self.notify_listeners(state)        
