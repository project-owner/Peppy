# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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

import math

from ui.screen.menuscreen import MenuScreen
from util.keys import KEY_AUTHORS, LABELS, KEY_BACK, KEY_PAGE_DOWN, KEY_PAGE_UP
from ui.menu.menu import ALIGN_LEFT
from ui.factory import Factory
from ui.menu.multipagemenu import MultiPageMenu
from ui.navigator.book import BookNavigator
from websiteparser.siteparser import AUTHOR_NAME, AUTHOR_URL, AUTHOR_BOOKS
from util.config import FONT_HEIGHT_PERCENT, COLORS, COLOR_MEDIUM, COLOR_CONTRAST, COLOR_BRIGHT, COLOR_DARK
from ui.button.button import Button
from ui.state import State

MENU_ROWS = 5
MENU_COLUMNS = 2
PAGE_SIZE = MENU_ROWS * MENU_COLUMNS

class BookAuthor(MenuScreen):
    """ Authors screen """
    
    def __init__(self, util, listeners, ch, f, go_author, parser, base_url, voice_assistant, d):
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
        
        MenuScreen.__init__(self, util, listeners, MENU_ROWS, MENU_COLUMNS, voice_assistant, d, self.turn_page)
        m = self.create_book_author_menu_button
        
        self.navigator = BookNavigator(util, self.layout.BOTTOM, listeners, d[4])
        self.back_button = self.navigator.get_button_by_name(KEY_BACK)
        self.left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        self.right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)
        self.add_navigator(self.navigator)

        font_size = int(((self.menu_layout.h / MENU_ROWS) / 100) * self.config[FONT_HEIGHT_PERCENT])
        self.authors_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, m, MENU_ROWS, MENU_COLUMNS, None, (0, 0, 0), self.menu_layout, font_size=font_size)
        self.set_menu(self.authors_menu)
        
    def create_book_author_menu_button(self, s, constr, action, scale, font_size):
        """ Create Author Menu button

        :param s: button state
        :param constr: bounding box
        :param action: button event listener
        :param show_img: True - show image, False - don't show image
        :param show_label: True - show label, False - don't show label
        
        :return: genre menu button
        """
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = False
        s.show_label = True
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        s.fixed_height = font_size

        button = Button(self.util, s)
        button.add_release_listener(action)
        return button

    def create_book_author_items(self, authors):
        """ Create dictionary with author books

        :param authors: list of author books

        :return: dictionary with author books
        """
        items = {}
        for i, g in enumerate(authors):
            state = State()
            state.name = g[AUTHOR_NAME]
            state.url = g[AUTHOR_URL] + "/"
            state.author_books = int(g[AUTHOR_BOOKS] )
            try:
                state.l_name = state.name + " (" + g[AUTHOR_BOOKS] + ")"
            except:
                state.l_name = state.name
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = False
            state.show_label = True
            state.comparator_item = state.name
            state.index = i
            items[state.name] = state
        return items

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
        
        self.parser.author_parser.current_author_char = self.current_author_char
        self.parser.author_parser.url = self.base_url
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
        self.author_dict = self.create_book_author_items(page)
        self.authors_menu.set_items(self.author_dict, 0, self.go_author, False)
        self.authors_menu.align_content(ALIGN_LEFT)
        self.total_pages = math.ceil(len(filtered_authors) / PAGE_SIZE)
        
        left = str(self.current_page - 1)
        if self.total_pages == 0:
            right = "0"
        else:
            right = str(self.total_pages - self.current_page)

        self.left_button.change_label(left)
        self.right_button.change_label(right)
        self.set_title(self.current_page)

        if self.authors_menu.get_selected_item() != None:
            self.navigator.unselect()
        else:
            if not self.navigator.is_selected():
                self.back_button.set_selected(True)
                self.back_button.clean_draw_update()

        self.authors_menu.clean_draw_update()

        self.link_borders()

    def handle_event(self, event):
        """ Handle screen event

        :param event: the event to handle
        """
        self.handle_event_common(event)

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.navigator.add_observers(update_observer, redraw_observer)
        self.authors_menu.add_menu_loaded_listener(redraw_observer)
        self.authors_menu.add_menu_observers(update_observer, redraw_observer, release=False)   
