# Copyright 2016-2020 Peppy Player peppy.player@gmail.com
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

from ui.screen.menuscreen import MenuScreen 
from ui.menu.multipagemenu import MultiPageMenu
from ui.menu.booknavigator import BookNavigator
from util.keys import KEY_CHOOSE_GENRE, LABELS
from ui.menu.menu import ALIGN_LEFT
from ui.factory import Factory
import math

MENU_ROWS = 5
MENU_COLUMNS = 2
PAGE_SIZE = MENU_ROWS * MENU_COLUMNS

class BookGenre(MenuScreen):
    """ Bokk genre screen """
    
    def __init__(self, util, listeners, go_book_by_genre, genres, base_url, voice_assistant, d):
        self.util = util
        self.go_book_by_genre = go_book_by_genre
        self.config = util.config
        self.genres_list = genres
        self.base_url = base_url
        self.factory = Factory(util)
        MenuScreen.__init__(self, util, listeners, MENU_ROWS, MENU_COLUMNS, voice_assistant, d, self.turn_page)
        self.total_pages = math.ceil(len(genres) / PAGE_SIZE)
        self.title = self.config[LABELS][KEY_CHOOSE_GENRE]
        m = self.factory.create_book_genre_menu_button        
        self.genre_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, m, MENU_ROWS, MENU_COLUMNS, None, (0, 0, 0, 0), self.menu_layout)        
        self.set_menu(self.genre_menu)
        self.navigator = BookNavigator(util, self.layout.BOTTOM, listeners, d[4])
        self.add_component(self.navigator)
        self.turn_page()        
        
    def turn_page(self):
        """ Turn book genre page """
        
        start = (self.current_page - 1) * PAGE_SIZE
        end = self.current_page * PAGE_SIZE
        page = self.genres_list[start : end]  
        self.genres_dict = self.factory.create_book_genre_items(page, self.base_url)
        self.genre_menu.set_items(self.genres_dict, 0, self.go_book_by_genre, False)
        self.genre_menu.align_content(ALIGN_LEFT)

        for b in self.genre_menu.buttons.values():
            b.parent_screen = self

        self.genre_menu.select_by_index(0)
        self.genre_menu.clean_draw_update()
        
        self.navigator.left_button.change_label(str(self.current_page - 1))
        self.navigator.right_button.change_label(str(self.total_pages - self.current_page))
        self.set_title(self.current_page)
        
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.navigator.add_observers(update_observer, redraw_observer)
        self.genre_menu.add_menu_observers(update_observer, redraw_observer, release=False)
