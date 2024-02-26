# Copyright 2024 Peppy Player peppy.player@gmail.com
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
from util.keys import *
from util.config import *
from ui.state import State
from ui.layout.buttonlayout import CENTER, LEFT, RIGHT, TOP, BOTTOM
from ui.menu.menu import Menu, ALIGN_LEFT
from ui.navigator.browser import BrowserNavigator, SORT_ALPHABETIC, SORT_NUMERIC
from copy import copy
from util.radiobrowser import NAME, STATIONCOUNT, COUNTRY_CODE

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

ICON_LOCATION = LEFT
BUTTON_PADDING = 5
ICON_AREA = 25
ICON_SIZE = 80
FONT_HEIGHT = 16

MENU_ROWS = 5
MENU_COLUMNS = 2

class BrowserScreen(MenuScreen):
    """ Radio Browser Screen """
    
    def __init__(self, util, listeners, browser_type, title):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        :param browser_type: browser type - Country, Language
        :param title: screen title
        """
        self.util = util
        self.config = util.config
        self.source = browser_type
        self.factory = Factory(util)
        rows = MENU_ROWS
        columns = MENU_COLUMNS
        d = [MENU_ROWS, MENU_COLUMNS]
        self.page_size = rows * columns
        self.go_radio_search = listeners[KEY_SEARCH_BROWSER]

        MenuScreen.__init__(self, util, listeners, rows, columns, d, self.turn_page, page_in_title=False)
        self.total_pages = 0
        self.title = title
        m = self.create_menu_button
        button_height = (self.menu_layout.h / rows) - (self.config[PADDING] * 2)
        bgr = self.config[BACKGROUND][MENU_BGR_COLOR]

        if self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            font_size = int(((100 - self.config[IMAGE_AREA]) / 100) * self.config[FONT_HEIGHT_PERCENT])
        else:
            font_size = int((button_height / 100) * self.config[FONT_HEIGHT_PERCENT])

        listeners[SORT_ALPHABETIC] = self.sort_alphabetic
        listeners[SORT_NUMERIC] = self.sort_numeric
        self.navigator = BrowserNavigator(self.util, self.layout.BOTTOM, listeners, "browser.navigator")
        self.add_navigator(self.navigator)
        self.left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        self.right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)
        self.back_button = self.navigator.get_button_by_name(KEY_BACK)

        h = self.config[HORIZONTAL_LAYOUT]
        self.browser_menu = Menu(util, bgr, self.menu_layout, rows, columns, create_item_method=m, align=ALIGN_LEFT, horizontal_layout=h, font_size=font_size)
        self.set_menu(self.browser_menu)
        self.current_page = 1
        self.animated_title = True
        self.sort_abc_ascending = False
        self.sort_num_ascending = False
        self.items = None

    def set_current(self, state=None):
        """ Set as a current screen

        :param state: button state
        """
        if self.items != None:
            return

        self.set_loading(self.title)
        
        self.bgr_color = self.util.config[COLORS][COLOR_DARK]
        self.radio_browser_util = self.util.radio_browser

        if self.source == KEY_COUNTRY_SCREEN:
            self.search_by = KEY_SEARCH_BY_COUNTRY
            self.items = self.radio_browser_util.get_countries()
            self.menu_items = self.get_menu_items(self.items, self.bgr_color)
        elif self.source == KEY_LANGUAGE_SCREEN:
            self.search_by = KEY_SEARCH_BY_LANGUAGE
            self.items = self.radio_browser_util.get_languages()
            self.menu_items = self.get_menu_items(self.items, self.bgr_color)

        self.total_pages = math.ceil(len(self.menu_items) / self.page_size)
        self.turn_page()
        self.reset_loading()
        self.clean_draw_update()

    def set_title(self):
        """ Set screen title """

        self.screen_title.set_text(self.title)

    def sort_alphabetic(self, state):
        """ Sort items in alphabetic order

        :param state: button state
        """
        if self.sort_abc_ascending:
            self.sort_abc_ascending = False
        else:
            self.sort_abc_ascending = True

        self.sort(NAME, self.sort_abc_ascending)

    def sort_numeric(self, state):
        """ Sort items in numeric order

        :param state: button state
        """
        if self.sort_num_ascending:
            self.sort_num_ascending = False
        else:
            self.sort_num_ascending = True
            
        self.sort(STATIONCOUNT, self.sort_num_ascending)

    def sort(self, key, sort_order):
        """ Sort items
        
        :param key: sort key
        :param sort_order: sort order
        """
        self.radio_browser_util.sort_list(self.items, key, reversed=sort_order)
        self.menu_items = self.get_menu_items(self.items, self.bgr_color)
        self.turn_page()
        self.clean_draw_update()

    def create_menu_button(self, state, constr, action, scale, font_size):
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
        s.wrap_labels = True
        s.fixed_height = font_size
        s.scaled = False

        b = self.factory.create_menu_button(s, constr, action, scale, label_area_percent=label_area_percent, show_label=s.show_label, font_size=font_size)

        return b

    def get_scale_factor(self, s):
        """ Calculate scale factor

        :param s: button state object

        :return: scale width and height tuple
        """
        bb = s.bounding_box
        if self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            location = TOP
        else:
            location = self.config[ALIGN_BUTTON_CONTENT_X]
        icon_box = self.factory.get_icon_bounding_box(bb, location, self.config[IMAGE_AREA], self.config[IMAGE_SIZE], self.config[PADDING])
        icon_box_without_label = self.factory.get_icon_bounding_box(bb, location, 100, 100, self.config[PADDING], False)
        if self.config[HIDE_FOLDER_NAME]:
            s.show_label = False
            w = icon_box_without_label.w
            h = icon_box_without_label.h
        else:
            s.show_label = True
            w = icon_box.w
            h = icon_box.h

        return (w, h)

    def get_page(self):
        """ Get the current page from the playlist

        :return: the page
        """
        if self.total_pages == 0:
            self.left_button.change_label("0")
            self.right_button.change_label("0")
            self.set_title()
            return []
        
        self.set_title()
        start = (self.current_page - 1) * self.page_size
        end = self.current_page * self.page_size
        return self.menu_items[start : end]

    def turn_page(self):
        """ Turn page """
        
        page = self.get_page()
        d = self.browser_menu.make_dict(page)
        self.browser_menu.set_items(d, 0, self.change_item, False)
        menu_selected = self.browser_menu.is_selected()

        if self.navigator and self.total_pages > 1:
            self.left_button.change_label(str(self.current_page - 1))
            self.right_button.change_label(str(self.total_pages - self.current_page))
        else:
            self.left_button.change_label("0")
            self.right_button.change_label("0")

        self.browser_menu.clean_draw_update()
        if menu_selected:
            self.navigator.unselect()

        self.link_borders()
        navigator_selected = self.navigator.is_selected()

        if (len(page) == 0 or (not menu_selected and not navigator_selected)) and self.navigator and not self.navigator.is_selected():
                self.back_button.set_selected(True)

    def change_item(self, state):
        """ Change item

        :param state: state object
        """
        state.source = self.source
        state.name = state.l_name
        state.search_by = self.search_by

        if self.search_by == KEY_SEARCH_BY_COUNTRY:
            state.callback_var = state.country_code 
        elif self.search_by == KEY_SEARCH_BY_LANGUAGE:
            state.callback_var = state.comparator_item.lower()
        else:
            state.callback_var = state.comparator_item

        self.go_radio_search(state)

    def get_menu_items(self, items, bgr):
        """ Get menu items

        :param items: browser items
        :param bgr: menu items

        :return: menu items
        """
        if not items:
            return []

        menu_items = []
        index = 0
        
        for item in items:
            name = item[NAME]
            count = item.get(STATIONCOUNT, None)
            state = State()
            state.index = index
            state.name = str(index)

            if self.search_by == KEY_SEARCH_BY_LANGUAGE:
                state.l_name = f"{name.title()} ({count})"
                state.comparator_item = name.title()
            else:
                state.l_name = f"{name} ({count})"
                state.comparator_item = name

            state.image_path = state.default_icon_path = None
            state.bgr = bgr
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = False
            state.show_label = True
            state.h_align = H_ALIGN_LEFT
            state.v_align = V_ALIGN_TOP
            state.v_offset = 35
            state.country_code = item.get(COUNTRY_CODE, None)
            state.search_by = self.search_by
            menu_items.append(state)
            index += 1

        return menu_items

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        MenuScreen.add_screen_observers(self, update_observer, redraw_observer)
        self.update_observer = update_observer
        self.redraw_observer = redraw_observer
        self.add_loading_listener(redraw_observer)      
        self.navigator.add_observers(update_observer, redraw_observer)
