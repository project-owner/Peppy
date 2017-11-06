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

import urllib.parse
import math

from ui.screen.menuscreen import MenuScreen
from util.keys import KEY_AUTHORS, LABELS
from ui.menu.menu import ALIGN_LEFT
from ui.factory import Factory
from ui.menu.multipagemenu import MultiPageMenu
from websiteparser.siteparser import AUTHOR_NAME

MENU_ROWS = 5
MENU_COLUMNS = 2
PAGE_SIZE = MENU_ROWS * MENU_COLUMNS

class BookAuthor(MenuScreen):
    """ Authors screen """
    
    def __init__(self, util, listeners, ch, f, go_author, parser, base_url, d):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen listeners
        :param ch: selected character
        :param f: selected filter
        :param go_authors: callback
        :param parser: authors parser
        :param base_url: url
        :param d: dictionary with menu button flags 
        """ 
        self.util = util
        self.factory = Factory(util)
        self.base_url = base_url
        self.config = util.config
        
        self.parser = parser
        self.current_author_char = ch
        self.current_author_filter = f
        self.go_author = go_author
        self.author_cache = {}
        self.title = self.config[LABELS][KEY_AUTHORS]
        
        MenuScreen.__init__(self, util, listeners, MENU_ROWS, MENU_COLUMNS, d, self.turn_page)
        m = self.factory.create_book_author_menu_button  
        
        self.authors_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, go_author, m, MENU_ROWS, MENU_COLUMNS, None, (0, 0, 0), self.menu_layout)
        self.set_menu(self.authors_menu)        
        
    def set_current(self, ch=None, f=None):
        """ Apply selected character and filter
        
        :param ch: selected character
        :param f: selected filter
        """
        if not ch and not f:
            return
        
        self.set_loading(self.config[LABELS][KEY_AUTHORS])
        
        self.total_pages = 0
        self.current_page = 1        
        self.current_author_char = ch
        self.current_author_filter = f
        
        try:
            self.author_cache[ch]
        except:
            self.get_authors()
            
        self.turn_page()
        self.reset_loading()        
    
    def get_authors(self):
        """ Get authors from parser """
        
        c = urllib.parse.quote(self.current_author_char.encode('utf-8'))
        self.parser.author_parser.url = self.base_url.replace("AAA", c)
        authors = self.parser.get_authors()
        if authors:
            self.author_cache[self.current_author_char] = authors
        
    def turn_page(self):
        """ Turn authors page """
        
        self.authors_menu.set_items({}, 0, self.go_author)
        
        filtered_authors = []
        for a in self.author_cache[self.current_author_char]:
            if self.current_author_filter:
                if a[AUTHOR_NAME].startswith(self.current_author_filter):                    
                    filtered_authors.append(a)
            else:
                filtered_authors.append(a)

        start = (self.current_page - 1) * PAGE_SIZE
        end = self.current_page * PAGE_SIZE
        page = filtered_authors[start : end]  
        self.author_dict = self.factory.create_book_author_items(page)
        self.authors_menu.set_items(self.author_dict, 0, self.go_author, False)
        self.authors_menu.align_labels(ALIGN_LEFT)        
        self.authors_menu.select_by_index(0)        
        self.authors_menu.clean_draw_update()
        
        self.total_pages = math.ceil(len(filtered_authors) / PAGE_SIZE)
        
        left = str(self.current_page - 1)
        if self.total_pages == 0:
            right = "0"
        else:
            right = str(self.total_pages - self.current_page)
        self.navigator.left_button.change_label(left)
        self.navigator.right_button.change_label(right)
        self.set_title(self.current_page)
        
        
