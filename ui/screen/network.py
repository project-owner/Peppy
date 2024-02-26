# Copyright 2019-2024 Peppy Player peppy.player@gmail.com
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

import pygame
import time

from ui.component import Component
from ui.container import Container
from ui.screen.screen import Screen
from ui.layout.borderlayout import BorderLayout
from ui.layout.gridlayout import GridLayout
from ui.factory import Factory
from ui.screen.menuscreen import MenuScreen
from util.config import LABELS, BLUETOOTH
from util.wifiutil import WiFiUtil, CONNECTED, ETHERNET_IP, WIFI_NETWORK, WIFI_IP
from ui.navigator.network import NetworkNavigator
from util.keys import KEY_HOME, KEY_CHECK_INTERNET, KEY_SET_MODES, KEY_DISCONNECTING, KEY_CONNECTING, H_ALIGN_LEFT, \
    H_ALIGN_RIGHT, V_ALIGN_BOTTOM, V_ALIGN_TOP, KEY_CALLBACK_VAR, KEY_REFRESH, KEY_DISCONNECT, KEY_BLUETOOTH_REMOVE
from util.config import COLORS, COLOR_BRIGHT, COLOR_CONTRAST, LINUX_PLATFORM, USAGE, USE_BLUETOOTH, BACKGROUND, MENU_BGR_COLOR

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

class NetworkScreen(MenuScreen):
    """ Network Screen """

    def __init__(self, util, listeners):
        """ Initializer

        :param util: utility object
        :param listeners: listeners
        """
        self.util = util
        self.config = util.config
        self.factory = Factory(util)
        self.check_internet_connectivity = listeners[KEY_CHECK_INTERNET]
        self.go_home = listeners[KEY_HOME]
        self.set_modes = listeners[KEY_SET_MODES]
        self.linux = self.config[LINUX_PLATFORM]

        self.wifi_util = WiFiUtil(util)
        self.bluetooth_util = self.util.get_bluetooth_util()

        self.bounding_box = util.screen_rect
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)

        rows = 7
        if self.linux and self.config[USAGE][USE_BLUETOOTH]:
            rows = 7
        else:
            rows = 6

        columns = 1
        d = [rows, columns]
        MenuScreen.__init__(self, util, listeners, rows, columns, d, None, page_in_title=False, show_loading=False)
        self.title = self.config[LABELS]["network"]
        self.set_title(1)

        center_layout = BorderLayout(self.menu_layout)
        center_layout.set_percent_constraints(0, 0, 47, 0)

        left_layout = center_layout.LEFT
        right_layout = center_layout.CENTER

        label_layout = GridLayout(left_layout)
        row_height = label_layout.height / rows
        gap = (row_height * 20) / 100
        label_layout.y -= gap
        label_layout.set_pixel_constraints(rows, columns)
        label_layout.get_next_constraints()

        value_layout = GridLayout(right_layout)
        value_layout.y -= gap
        value_layout.set_pixel_constraints(rows, columns)
        value_layout.get_next_constraints()

        self.network_panel = Container(util, self.menu_layout)

        rect = pygame.Rect(self.menu_layout.x, self.menu_layout.y + 1, self.menu_layout.w, self.menu_layout.h - 1)
        b = util.config[BACKGROUND][MENU_BGR_COLOR]
        bgr = Component(util, rect, 0, 0, self.menu_layout, bgr=b)
        bgr.name = "network.panel.bgr"
        self.network_panel.add_component(bgr)

        self.internet_label = self.add_label(label_layout, self.network_panel, 1)
        self.ethernet_label = self.add_label(label_layout, self.network_panel, 2)
        self.wifi_network_label = self.add_label(label_layout, self.network_panel, 3)
        self.wifi_ip_label = self.add_label(label_layout, self.network_panel, 4)
        if self.linux and self.config[USAGE][USE_BLUETOOTH]:
            self.bluetooth_label = self.add_label(label_layout, self.network_panel, 5)

        self.internet = self.add_value(value_layout, self.network_panel, 1)
        self.ethernet_ip = self.add_value(value_layout, self.network_panel, 2)
        self.wifi_network = self.add_value(value_layout, self.network_panel, 3)
        self.wifi_ip = self.add_value(value_layout, self.network_panel, 4)
        if self.linux and self.config[USAGE][USE_BLUETOOTH]:
            self.bluetooth = self.add_value(value_layout, self.network_panel, 5)

        self.add_component(self.network_panel)

        listeners[KEY_REFRESH] = self.set_current
        listeners[KEY_DISCONNECT] = self.disconnect_wifi
        listeners[KEY_BLUETOOTH_REMOVE] = self.remove_bluetooth_devices

        self.navigator = NetworkNavigator(self.util, self.layout.BOTTOM, listeners)
        self.navigator.components[0].set_selected(True)
        self.add_navigator(self.navigator)
        self.original_networks = None
        self.networks = None
        self.current_network = None
        self.current_wifi_network = None
        self.clicked = False
        Screen.link_borders(self, False)

    def set_current(self, state):
        """ Set current state

        :param state: button state
        """
        if state and getattr(state, "source", None) == "bluetooth":
            self.set_loading(self.title)
            self.bluetooth_util.connect_device(state.name, state.mac_address, False)
            self.set_initial_state(state)
            if self.bluetooth.text:
                self.bluetooth_util.update_asoundrc(state.mac_address)
            self.reset_loading()
            self.clean_draw_update()
            return

        if not state or (state and not getattr(state, KEY_CALLBACK_VAR, None)):
            self.set_loading(self.title)
            self.set_initial_state(state)
            self.reset_loading()
        else:
            self.connect_wifi(state)

        self.clean_draw_update()

    def set_initial_state(self, state):
        """ Set initial screen

        :param state: button state
        """
        info = self.get_network_info()

        self.internet_label.set_text("Internet:")
        self.ethernet_label.set_text("Ethernet IP:")
        self.wifi_network_label.set_text("Wi-Fi Network:")
        self.wifi_ip_label.set_text("Wi-Fi IP:")
        if self.linux and self.config[USAGE][USE_BLUETOOTH]:
            self.bluetooth_label.set_text("Bluetooth:")

        self.set_value(self.internet, info, CONNECTED)
        self.set_value(self.ethernet_ip, info, ETHERNET_IP)
        self.set_value(self.wifi_network, info, WIFI_NETWORK)
        self.set_value(self.wifi_ip, info, WIFI_IP)
        if self.linux and self.config[USAGE][USE_BLUETOOTH]:
            self.set_value(self.bluetooth, info, BLUETOOTH)

    def set_value(self, field, info, key):
        """ Set text in provided field

        :param field: text field
        :param info: info dictionary
        :param key: dictionary key
        """
        try:
            field.set_text(self.truncate(info[key]))
        except:
            field.set_text("")

    def get_network_info(self):
        """ Get network information

        :return: dictionary with network info
        """
        info = self.wifi_util.get_network()
        connected = self.check_internet_connectivity()
        if connected:
            info[CONNECTED] = self.config[LABELS]["connected"]
        else:
            info[CONNECTED] = self.config[LABELS]["disconnected"]

        info[BLUETOOTH] = ""
        d = self.bluetooth_util.get_connected_device()
        if d:
            info[BLUETOOTH] = d["name"]

        return info

    def truncate(self, s):
        """ Truncate string

        :param s: input string

        :return: truncated string
        """
        CHARS = 18
        if len(s) > CHARS:
            s = s[0 : CHARS] + "..."
        return s

    def add_label(self, layout, parent, n):
        """ Add label component

        :param layout: label layout
        :param parent: parent container
        :param n: label number
        :return: label component
        """
        c = layout.get_next_constraints()
        fgr = self.util.config[COLORS][COLOR_BRIGHT]
        h = H_ALIGN_RIGHT
        v = V_ALIGN_BOTTOM
        f = int((c.height * 50) / 100)
        name = "label." + str(n)
        label = self.factory.create_output_text(name, c, (0, 0, 0, 0), fgr, f, h, v)
        parent.add_component(label)
        return label

    def add_value(self, layout, parent, n):
        """ Add value component

        :param layout: layout
        :param parent: parent container
        :param n: component number
        :return: value component
        """
        c = layout.get_next_constraints()
        fgr = self.util.config[COLORS][COLOR_CONTRAST]
        h = H_ALIGN_LEFT
        v = V_ALIGN_BOTTOM
        f = int((c.height * 68) / 100)
        name = "value." + str(n)
        gap = int((c.height * 20) / 100)
        c.y += 1
        value = self.factory.create_output_text(name, c, (0, 0, 0, 0), fgr, f, halign=h, valign=v, shift_x=gap)
        parent.add_component(value)
        return value

    def set_current_wifi_network(self, net):
        """ Set current Wi-Fi network

        :param net: new network name
        """
        self.current_wifi_network = net

    def connect_wifi(self, state):
        """ Connect to Wi-Fi network

        :param state: button state
        """
        self.set_loading(self.title, self.config[LABELS][KEY_CONNECTING])

        if self.linux:
            self.connect_wifi_linux(state)
        else:
            self.connect_wifi_windows()

        self.check_network()
        self.set_initial_state(None)
        self.reset_loading()

    def connect_wifi_windows(self):
        """ Connect to Wi-Fi on Windows """

        self.wifi_util.connect_wifi_windows(self.current_wifi_network, self.current_wifi_network)
        time.sleep(4)

    def connect_wifi_linux(self, state):
        """" Connect to Wi-Fi on Linux

        :param state: button state
        """
        pswd = getattr(state, KEY_CALLBACK_VAR, None)
        if not pswd:
            return

        self.wifi_util.connect_wifi_linux(self.current_wifi_network, pswd)
        time.sleep(5)

    def disconnect_wifi(self, state):
        """ Disconnect from Wi-Fi network

        :param state: button state
        """
        self.set_loading(self.title, self.config[LABELS][KEY_DISCONNECTING])
        self.wifi_util.disconnect_wifi()
        self.check_network()
        time.sleep(4)
        self.set_initial_state(None)
        self.reset_loading()
        self.clean_draw_update()

    def remove_bluetooth_devices(self, state):
        """ Remove bluetooth devices

        :param state: button state
        """
        self.set_loading(self.title)
        self.bluetooth_util.remove_devices()
        self.set_initial_state(state)
        if not self.bluetooth.text:
            self.bluetooth_util.restore_asoundrc()
        self.reset_loading()
        self.clean_draw_update()

    def check_network(self):
        """ Check Internet connectivity """

        self.util.connected_to_internet = self.check_internet_connectivity()
        self.set_modes()

    def handle_event(self, event):
        """ Event handler

        :param event: event to handle
        """
        if not self.visible or event.type == pygame.MOUSEMOTION: return

        mouse_events = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]
        pos = None
        try:
            pos = event.pos
        except:
            pass

        if pos and event.type in mouse_events:
            if self.menu_layout.collidepoint(event.pos):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return

                self.go_home(None)
                self.redraw_observer()
            else:
                for b in self.navigator.components:
                    if b.bounding_box.collidepoint(event.pos):
                        b.set_selected(True)
                    else:
                        b.set_selected(False)
                    b.clean_draw_update()

        Container.handle_event(self, event)

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
