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

import math

from ui.screen.menuscreen import MenuScreen 
from ui.menu.multipagemenu import MultiPageMenu
from ui.navigator.book import BookNavigator
from util.keys import KEY_CHOOSE_GENRE, LABELS, KEY_PAGE_DOWN, KEY_PAGE_UP, KEY_BACK
from ui.menu.menu import ALIGN_LEFT
from ui.factory import Factory
from util.config import FONT_HEIGHT_PERCENT, COLORS, COLOR_MEDIUM, COLOR_CONTRAST, COLOR_BRIGHT, \
    BACKGROUND, MENU_BGR_COLOR
from ui.button.button import Button

MENU_ROWS = 5
MENU_COLUMNS = 2
PAGE_SIZE = MENU_ROWS * MENU_COLUMNS

class BookGenre(MenuScreen):
    """ Book genre screen """
    
    def __init__(self, util, listeners, go_book_by_genre, genres, base_url, d):
        self.util = util
        self.go_book_by_genre = go_book_by_genre
        self.config = util.config
        self.genres_list = genres
        self.base_url = base_url
        self.factory = Factory(util)
        MenuScreen.__init__(self, util, listeners, d, self.turn_page)
        self.total_pages = math.ceil(len(genres) / PAGE_SIZE)
        self.title = self.config[LABELS][KEY_CHOOSE_GENRE]
        
        self.navigator = BookNavigator(util, self.layout.BOTTOM, listeners, d[4])
        self.back_button = self.navigator.get_button_by_name(KEY_BACK)
        self.left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        self.right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)
        self.add_navigator(self.navigator)

        m = self.create_book_genre_menu_button
        font_size = int(((self.menu_layout.h / MENU_ROWS) / 100) * self.config[FONT_HEIGHT_PERCENT])
        self.genre_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, m, MENU_ROWS, MENU_COLUMNS, None, (0, 0, 0, 0), self.menu_layout, font_size=font_size)
        self.set_menu(self.genre_menu)
        
        self.turn_page()        

    def create_book_genre_menu_button(self, s, constr, action, show_img=True, show_label=True):
        """ Create Genre Menu button

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
        s.show_img = show_img
        s.show_label = show_label
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        s.label_text_height = 35
        s.bgr = self.config[BACKGROUND][MENU_BGR_COLOR]

        button = Button(self.util, s)
        button.add_release_listener(action)
        return button

    def turn_page(self):
        """ Turn book genre page """
        
        start = (self.current_page - 1) * PAGE_SIZE
        end = self.current_page * PAGE_SIZE
        page = self.genres_list[start : end]  
        self.genres_dict = self.factory.create_book_genre_items(page, self.base_url)
        self.genre_menu.set_items(self.genres_dict, 0, self.go_book_by_genre, False)
        self.genre_menu.align_content(ALIGN_LEFT)

        for i, b in enumerate(self.genre_menu.buttons.values()):
            b.parent_screen = self
            b.state.index = start + i

        self.genre_menu.clean_draw_update()
        
        self.left_button.change_label(str(self.current_page - 1))
        self.right_button.change_label(str(self.total_pages - self.current_page))
        self.set_title(self.current_page)

        if self.genre_menu.get_selected_item() != None:
            self.navigator.unselect()
        else:
            if not self.navigator.is_selected():
                self.back_button.set_selected(True)
                self.back_button.clean_draw_update()

        self.link_borders()
        self.genre_menu.current_page = self.current_page
    
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
        self.genre_menu.add_menu_observers(update_observer, redraw_observer, release=False)
