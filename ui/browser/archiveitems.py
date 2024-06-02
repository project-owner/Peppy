# Copyright 2023 Peppy Player peppy.player@gmail.com
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
from ui.factory import Factory
from util.keys import KEY_ARCHIVE_ITEMS_BROWSER, KEY_PAGE_DOWN, KEY_PAGE_UP, KEY_PLAYER, KEY_ARCHIVE_ITEMS, \
    KEY_SEARCH, KEY_SOURCE, KEY_CALLBACK_VAR, KEY_ARCHIVE_FILES_BROWSER
from util.config import PADDING, IMAGE_AREA, ALIGN_BUTTON_CONTENT_X, H_ALIGN_LEFT, H_ALIGN_RIGHT, \
    H_ALIGN_CENTER, WRAP_LABELS, HORIZONTAL_LAYOUT, BACKGROUND, MENU_BGR_COLOR, FONT_HEIGHT_PERCENT, \
    LABELS, ARCHIVE, FILE, SEARCH
from ui.layout.buttonlayout import CENTER, LEFT, RIGHT, TOP, BOTTOM
from ui.menu.menu import Menu, ALIGN_LEFT
from ui.navigator.archiveitems import ArchiveItemsNavigator
from copy import copy
from util.archiveutil import ITEM_MENU_ROWS, ITEM_MENU_COLUMNS

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

ICON_LOCATION = LEFT
BUTTON_PADDING = 5
ICON_AREA = 0
ICON_SIZE = 0
FONT_HEIGHT = 16
QUERY_RESULTS = "query.results"

class ArchiveItemsBrowserScreen(MenuScreen):
    """ Archive Items Browser Screen """
    
    def __init__(self, util, listeners):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        """
        self.util = util
        self.config = util.config
        self.factory = Factory(util)
        self.archive_util = util.archive_util

        rows = ITEM_MENU_ROWS
        columns = ITEM_MENU_COLUMNS
        d = [ITEM_MENU_ROWS, ITEM_MENU_COLUMNS]
        self.page_size = rows * columns

        MenuScreen.__init__(self, util, listeners, d, self.turn_page, page_in_title=False)
        self.animated_title = True
        self.total_pages = 0
        self.title = self.config[LABELS][QUERY_RESULTS]
        self.screen_title.set_text(self.title)
        m = self.create_archive_browser_menu_button
        button_height = (self.menu_layout.h / rows) - (self.config[PADDING] * 2)
        bgr = self.config[BACKGROUND][MENU_BGR_COLOR]

        if self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            font_size = int(((100 - self.config[IMAGE_AREA]) / 100) * self.config[FONT_HEIGHT_PERCENT])
        else:
            font_size = int((button_height / 100) * self.config[FONT_HEIGHT_PERCENT])

        self.navigator = ArchiveItemsNavigator(self.util, self.layout.BOTTOM, listeners, "archive.navigator")
        self.add_navigator(self.navigator)
        self.left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        self.right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)
        self.player_button = self.navigator.get_button_by_name(KEY_PLAYER)

        h = self.config[HORIZONTAL_LAYOUT]
        self.archive_menu = Menu(util, bgr, self.menu_layout, rows, columns, create_item_method=m, align=ALIGN_LEFT, horizontal_layout=h, font_size=font_size)
        self.set_menu(self.archive_menu)
        
        self.total_items = 0
        self.current_page = None
        self.ARCHIVE_LABEL = util.config[LABELS][ARCHIVE]
        self.turn_page()

        self.animated_title = True
        self.reset_page_counter = listeners[KEY_ARCHIVE_FILES_BROWSER]

    def create_archive_browser_menu_button(self, state, constr, action, scale, font_size):
        """ Factory function for menu button

        :param state: button state
        :param constr: bounding box
        :param action: action listener
        :param scale: True - scale, False - don't scale
        :param font_size: the label font size

        :return: menu button
        """
        s = copy(state)
        s.bounding_box = constr
        s.padding = self.config[PADDING]
        s.image_area_percent = self.config[IMAGE_AREA]
        label_area_percent = 100 - s.image_area_percent
        if self.config[ALIGN_BUTTON_CONTENT_X] == 'left':
            s.image_location = LEFT
            s.label_location = LEFT
            s.h_align = H_ALIGN_LEFT
        elif self.config[ALIGN_BUTTON_CONTENT_X] == 'right':
            s.image_location = RIGHT
            s.label_location = RIGHT
            s.h_align = H_ALIGN_RIGHT
        elif self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            s.image_location = TOP
            s.label_location = BOTTOM
            s.h_align = H_ALIGN_CENTER
        s.v_align = CENTER
        s.wrap_labels = self.config[WRAP_LABELS]
        s.fixed_height = font_size
        s.scaled = False
        s.show_label = True
        s.show_img = False

        b = self.factory.create_menu_button(s, constr, action, scale, label_area_percent=label_area_percent, 
                                            show_img=s.show_img, show_label=s.show_label, font_size=font_size)

        return b

    def set_current(self, state):
        """ Set current state
        
        :param state: button state
        """
        source = getattr(state, KEY_SOURCE, None)
        search_query = None
        items = None

        if not source:
            return

        self.set_loading(None)

        if source == KEY_SEARCH:
            search_query = getattr(state, KEY_CALLBACK_VAR, None)
            self.config[SEARCH] = search_query

        if search_query:
            if self.current_page == None:
                self.current_page = 1
            items = self.archive_util.get_menu_page(search_query, self.current_page)

        if items:
            self.total_items = items[0]
            self.config[KEY_ARCHIVE_ITEMS] = items
            self.current_page = 1

        self.turn_page()
        self.reset_loading()

    def get_page(self):
        """ Get the current page from the playlist

        :return: the page
        """
        self.total_pages = math.ceil(self.total_items / self.page_size)

        if self.total_pages == 0:
            self.left_button.change_label("0")
            self.right_button.change_label("0")
            return []
        
        if self.current_page == None:
            self.current_page = self.get_page_by_id()

        items = self.archive_util.get_menu_page(self.config[SEARCH], self.current_page)

        if items:
            self.config[KEY_ARCHIVE_ITEMS] = items
            return items[1]
        else:
            return []

    def get_page_by_id(self):
        """ Get the page by index

        :return: the page
        """
        id = None
        page = 1
        try:
            id = self.config[ARCHIVE][FILE]
        except:
            pass

        if not id:
            return page
        
        index = int(id)
        if index < self.page_size:
            page = 1
        else:
            page = math.ceil(index / self.page_size)
            if page == 1:
                page = 2

        return page

    def turn_page(self):
        """ Turn page """

        page = self.get_page()

        if not page:
            return

        d = self.archive_menu.make_dict(page)
        self.archive_menu.set_items(d, 0, self.change_item, False)
        self.title = self.config[LABELS][QUERY_RESULTS] + ": " + self.config[SEARCH]
        self.screen_title.set_text(self.title)
        index = 0
        menu_selected = self.archive_menu.select_by_index(index)

        if self.navigator and self.total_pages > 1:
            self.left_button.change_label(str(self.current_page - 1))
            self.right_button.change_label(str(self.total_pages - self.current_page))
        else:
            self.left_button.change_label("0")
            self.right_button.change_label("0")

        for b in self.archive_menu.buttons.values():
            b.parent_screen = self

        self.archive_menu.clean_draw_update()
        if menu_selected:
            self.navigator.unselect()

        self.link_borders()
        navigator_selected = self.navigator.is_selected()

        if (len(page) == 0 or (not menu_selected and not navigator_selected)) and self.navigator:
            self.navigator.unselect()
            self.player_button.set_selected(True)
            self.player_button.clean_draw_update()

    def change_item(self, state):
        """ Change item

        :param state: state object
        """
        state.source = KEY_ARCHIVE_ITEMS_BROWSER
        state.name = state.l_name
        state.time = "0.0"
        self.reset_page_counter()
        self.go_player(state)
