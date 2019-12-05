# Copyright 2019 Peppy Player peppy.player@gmail.com
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
import pygame

from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.screen.menuscreen import MenuScreen
from ui.menu.menu import ALIGN_CENTER
from util.config import LABELS
from ui.menu.multipagemenu import MultiPageMenu
from util.wifiutil import WiFiUtil, MENU_ROWS_WIFI, MENU_COLUMNS_WIFI, PAGE_SIZE_WIFI
from ui.menu.wifinavigator import WiFiNavigator
from util.keys import KEY_HOME, KEY_KEYBOARD_KEY, KEY_CALLBACK, KEY_REFRESH, KEY_SORT

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

SORT_ALPHABETICALLY = 1
SORT_BY_SIGNAL_STRENGTH = 2

class WiFiScreen(MenuScreen):
    """ Wi-Fi Screen """

    def __init__(self, util, listeners, voice_assistant):
        """ Initializer

        :param util: utility object
        :param listeners: listeners
        :param voice_assistant: voice assistant
        """
        self.util = util
        self.config = util.config
        self.listeners = listeners
        self.factory = Factory(util)
        self.go_home = listeners[KEY_HOME]
        self.go_keyboard = listeners[KEY_KEYBOARD_KEY]
        self.keyboard_callback = listeners[KEY_CALLBACK]

        self.wifi_selection_listeners = []

        self.wifi_util = WiFiUtil(util)
        self.bounding_box = util.screen_rect
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)

        d = [MENU_ROWS_WIFI, MENU_COLUMNS_WIFI]
        MenuScreen.__init__(self, util, listeners, MENU_ROWS_WIFI, MENU_COLUMNS_WIFI, voice_assistant, d,
                            self.turn_page, page_in_title=False, show_loading=False)
        self.title = self.config[LABELS]["select.wifi"]
        self.set_title(1)

        m = self.factory.create_wifi_menu_button
        self.wifi_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title,
                                       self.go_to_page, m, MENU_ROWS_WIFI, MENU_COLUMNS_WIFI, None,
                                       (0, 0, 0), self.menu_layout, align=ALIGN_CENTER)
        self.set_menu(self.wifi_menu)

        listeners[KEY_REFRESH] = self.set_current
        listeners[KEY_SORT] = self.sort_abc
        self.navigator = WiFiNavigator(self.util, self.layout.BOTTOM, listeners, PAGE_SIZE_WIFI + 1)
        self.components.append(self.navigator)
        self.original_networks = None
        self.networks = None
        self.sort_direction = False
        self.current_network = None

    def set_current(self, state):
        """ Set current state

        :param state: button state
        """
        self.set_loading(self.title)
        info = self.wifi_util.get_wifi_networks()

        self.original_networks = info["networks"]

        if not self.original_networks:
            self.reset_loading()
            return

        self.networks = self.sort_networks(SORT_ALPHABETICALLY)
        self.current_network = info["profile"]
        self.total_pages = math.ceil(len(self.networks) / PAGE_SIZE_WIFI)
        self.reset_loading()

        self.current_page = self.wifi_util.get_page_num(self.current_network, self.networks)
        self.turn_page()

    def sort_networks(self, order):
        """ Sort networks

        :param order: sort order
        :return: sorted networks
        """
        sorted_networks = []

        if order == SORT_ALPHABETICALLY:
            sorted_networks = sorted(self.original_networks, key=lambda i: i["name"], reverse=self.sort_direction)
        else:
            sorted_networks = sorted(self.original_networks, key=lambda i: i["strength"], reverse=self.sort_direction)

        states = {}
        h = self.layout.CENTER.h / MENU_ROWS_WIFI
        bb = pygame.Rect(0, 0, h, h)
        for i, n in enumerate(sorted_networks):
            s = self.wifi_util.get_network_info(i, n["name"], n["strength"], bb)
            states[s.name] = s

        return states

    def sort_abc(self, state):
        """ Sort in alphabetical order

        :param state: button state
        """
        self.sort(SORT_ALPHABETICALLY)

    def select_network(self, state=None):
        """ Select network from menu

        :param state: button state
        """
        self.current_network = state.name
        self.notify_wifi_selection_listeners(self.current_network)
        state.title = self.config[LABELS]["enter.password"]
        state.callback = self.keyboard_callback
        self.go_keyboard(state)

    def sort(self, order):
        """ Sort by order

        :param order: sort order
        :return:
        """
        self.sort_direction = not self.sort_direction
        self.current_page = 1
        self.networks = self.sort_networks(order)
        self.turn_page()

    def turn_page(self):
        """ Turn page """

        p = self.wifi_util.get_network_page(self.current_page, self.networks)
        self.wifi_menu.set_items(p, 0, self.select_network, False)

        keys = list(p.keys())

        if len(keys) != 0 and self.navigator and self.total_pages > 1:
            self.navigator.left_button.change_label(str(self.current_page - 1))
            self.navigator.right_button.change_label(str(self.total_pages - self.current_page))

        self.set_title(self.current_page)
        self.wifi_menu.clean_draw_update()

        if hasattr(self, "update_observer"):
            self.wifi_menu.add_menu_observers(self.update_observer, self.redraw_observer)

        self.wifi_menu.unselect()
        for i, b in enumerate(self.wifi_menu.buttons.values()):
            if self.current_network == b.state.name:
                self.wifi_menu.select_by_index(b.state.index)
                return
        index = (self.current_page - 1) * PAGE_SIZE_WIFI
        self.wifi_menu.select_by_index(index)

    def add_wifi_selection_listener(self, listener):
        """ Add listener

        :param listener: event listener
        """
        if listener not in self.wifi_selection_listeners:
            self.wifi_selection_listeners.append(listener)

    def notify_wifi_selection_listeners(self, selected_wifi):
        """ Notify all listeners

        :param selected_wifi:
        """
        for listener in self.wifi_selection_listeners:
            listener(selected_wifi)

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers

        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        MenuScreen.add_screen_observers(self, update_observer, redraw_observer)
        self.update_observer = update_observer
        self.redraw_observer = redraw_observer
        self.add_loading_listener(redraw_observer)
        for b in self.navigator.menu_buttons:
            self.add_button_observers(b, update_observer, redraw_observer)
