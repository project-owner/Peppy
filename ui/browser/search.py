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

from ui.screen.menuscreen import MenuScreen
from ui.factory import Factory
from util.keys import *
from util.config import *
from ui.layout.buttonlayout import CENTER, LEFT, RIGHT, TOP, BOTTOM
from ui.menu.menu import Menu, ALIGN_LEFT
from ui.navigator.radiosearch import RadioSearchNavigator
from copy import copy

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
PAGE_SIZE = MENU_ROWS * MENU_COLUMNS

RADIO_BROWSER_STATION_ID = "radio.browser.station.id"

class RadioSearchScreen(MenuScreen):
    """ Radio Browser Screen """
    
    def __init__(self, util, listeners, state):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        :param state: initial state
        """
        self.util = util
        self.config = util.config
        self.radio_browser_util = util.radio_browser
        self.factory = Factory(util)
        rows = MENU_ROWS
        columns = MENU_COLUMNS
        d = [MENU_ROWS, MENU_COLUMNS]
        self.page_size = rows * columns
        self.go_player = listeners[KEY_PLAYER]
        self.search_by = getattr(state, "search_by", None)
        self.listeners = listeners
        self.bgr_color = self.util.config[COLORS][COLOR_DARK]
        self.TITLE_PREFIX = {
            KEY_SEARCH_BY_COUNTRY: self.config[LABELS]["country"],
            KEY_SEARCH_BY_LANGUAGE: self.config[LABELS]["language"],
            KEY_SEARCH_BY_GENRE: self.config[LABELS]["genre"],
            KEY_SEARCH_BY_NAME: self.config[LABELS]["name"]
        }

        MenuScreen.__init__(self, util, listeners, rows, columns, d, self.turn_page, page_in_title=False)
        self.total_pages = 0
        m = self.create_menu_button
        button_height = (self.menu_layout.h / rows) - (self.config[PADDING] * 2)
        bgr = self.config[BACKGROUND][MENU_BGR_COLOR]

        if self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            font_size = int(((100 - self.config[IMAGE_AREA]) / 100) * self.config[FONT_HEIGHT_PERCENT])
        else:
            font_size = int((button_height / 100) * self.config[FONT_HEIGHT_PERCENT])

        self.navigator = RadioSearchNavigator(self.util, self.layout.BOTTOM, listeners, "radio.search.navigator")
        self.add_navigator(self.navigator)
        self.left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        self.right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)
        self.back_button = self.navigator.get_button_by_name(KEY_BACK)
        self.player_button = self.navigator.get_button_by_name(KEY_PLAYER)
        self.change_back_button_listener(state)

        h = self.config[HORIZONTAL_LAYOUT]
        self.browser_menu = Menu(util, bgr, self.menu_layout, rows, columns, create_item_method=m, align=ALIGN_LEFT, horizontal_layout=h, font_size=font_size)
        self.set_menu(self.browser_menu)
        self.current_page = None
        self.animated_title = True
        self.sort_abc_ascending = False
        self.sort_num_ascending = False

    def load_page(self, state):
        """ Load current page
        
        :param state: button state
        """
        self.title = ""
        self.screen_title.set_text(self.title)
        self.search_by = getattr(state, "search_by", None)

        self.set_loading(self.title)
        
        self.menu_items = self.get_items(state)
        self.turn_page()
        self.reset_loading()
        self.clean_draw_update()

    def get_items(self, state):
        """ Get menu items
        
        :param state: button state
        """
        if getattr(state, "comparator_item", None):
            t = state.comparator_item
        else:
            t = state.callback_var

        try:
            self.title = self.TITLE_PREFIX[self.search_by] + ": " + t
        except:
            self.title = self.config[LABELS]["browse"] + ": " + t

        self.search_item = state.callback_var
        items = self.radio_browser_util.get_stations_page(self.search_by, self.search_item)
        self.total_pages = self.radio_browser_util.get_pages_num(self.search_by, self.search_item, self.page_size)

        return self.radio_browser_util.get_states_from_items(items, self.bgr_color, self.search_by, self.search_item)
    
    def set_title(self):
        """ Set screen title """

        self.screen_title.set_text(self.title)

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
        
        if self.current_page == None:
            self.current_page = 1

        self.set_title()

        start = (self.current_page - 1) * self.page_size
        end = self.current_page * self.page_size
        buffer = self.radio_browser_util.buffers[self.search_by]

        if len(buffer) > start: # in buffer
            items = buffer[start : end]
            self.menu_items = self.radio_browser_util.get_states_from_items(items, self.bgr_color, self.search_by, self.search_item)
        else: # load next buffer page
            self.set_loading(self.title)
            items = self.radio_browser_util.get_stations_page(self.search_by, self.search_item, offset=start, limit=PAGE_SIZE)
            self.total_pages =  self.radio_browser_util.get_pages_num(self.search_by, self.search_item, self.page_size)
            self.reset_loading()
            self.clean_draw_update()
            self.menu_items = self.radio_browser_util.get_states_from_items(items, self.bgr_color, self.search_by, self.search_item)

        return self.menu_items

    def turn_page(self):
        """ Turn page """
        
        page = self.get_page()
        d = self.browser_menu.make_dict(page)
        if d:
            self.browser_menu.set_items(d, 0, self.change_item, False)
        else:
            self.browser_menu.buttons = {}
            self.browser_menu.components = []

        if self.navigator and self.total_pages > 1:
            self.left_button.change_label(str(self.current_page - 1))
            self.right_button.change_label(str(self.total_pages - self.current_page))
        else:
            self.left_button.change_label("0")
            self.right_button.change_label("0")

        self.select_current_menu_item()
        self.browser_menu.clean_draw_update()
        self.link_borders()

    def change_item(self, state):
        """ Change item

        :param state: state object
        """
        state.source = KEY_SEARCH_BROWSER
        self.config[RADIO_BROWSER_SEARCH_BY] = state.search_by
        self.config[RADIO_BROWSER_SEARCH_ITEM] = state.search_item
        self.go_player(state)

    def change_back_button_listener(self, state):
        """ Change the Back button listener

        :param state: button state
        """
        search_by = getattr(state, "search_by", None)

        if search_by == None:
            return

        back_function = self.listeners[search_by]
        self.back_button.release_listeners.clear()
        self.back_button.add_release_listener(back_function)

    def select_current_menu_item(self):
        """ Select the current menu item """

        self.browser_menu.unselect()
        id = self.config.get(RADIO_BROWSER_SEARCH_STATION_ID, None)
        for b in self.browser_menu.buttons.values():
            if b.state.id == id:
                b.set_selected(True)
                self.navigator.unselect()
                break
        
        if not self.navigator.is_selected() and not self.browser_menu.is_selected():
            self.back_button.set_selected(True)

    def set_current(self, state):
        """ Set as a current screen
        
        :param state: button state
        """
        self.change_back_button_listener(state)

        source = getattr(state, "source", None)
        if source == None or source == KEY_BACK:
            return
        elif source == KEY_RADIO_BROWSER_PLAYER:
            self.select_current_menu_item()
            return

        self.current_page = 1
        self.load_page(state)

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
