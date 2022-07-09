# Copyright 2022 Peppy Player peppy.player@gmail.com
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
from util.keys import KEY_YA_STREAM_BROWSER, KEY_PAGE_DOWN, KEY_PAGE_UP, KEY_PLAYER
from util.config import PADDING, IMAGE_AREA, ALIGN_BUTTON_CONTENT_X, H_ALIGN_LEFT, H_ALIGN_RIGHT, \
    H_ALIGN_CENTER, WRAP_LABELS, HORIZONTAL_LAYOUT, BACKGROUND, MENU_BGR_COLOR, FONT_HEIGHT_PERCENT, \
    HIDE_FOLDER_NAME, IMAGE_SIZE, YA_STREAM_ID, LABELS, YA_STREAM, YA_STREAM_NAME
from util.yastreamutil import MENU_ROWS, MENU_COLUMNS
from ui.layout.buttonlayout import CENTER, LEFT, RIGHT, TOP, BOTTOM
from ui.menu.menu import Menu, ALIGN_LEFT
from ui.navigator.radio import RadioNavigator
from copy import copy

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

ICON_LOCATION = LEFT
BUTTON_PADDING = 5
ICON_AREA = 25
ICON_SIZE = 80
FONT_HEIGHT = 16

class YaStreamBrowserScreen(MenuScreen):
    """ Stream Browser Screen """
    
    def __init__(self, util, listeners, voice_assistant):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        :param voice_assistant: the voice assistant
        :param volume_control: volume control
        """
        self.util = util
        self.config = util.config
        self.ya_stream_util = util.ya_stream_util
        self.factory = Factory(util)
        rows = MENU_ROWS
        columns = MENU_COLUMNS
        d = [MENU_ROWS, MENU_COLUMNS]
        self.page_size = rows * columns

        MenuScreen.__init__(self, util, listeners, rows, columns, voice_assistant, d, self.turn_page, page_in_title=False)
        self.total_pages = 0
        self.title = ""
        m = self.create_ya_stream_browser_menu_button
        button_height = (self.menu_layout.h / rows) - (self.config[PADDING] * 2)
        bgr = self.config[BACKGROUND][MENU_BGR_COLOR]

        if self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            font_size = int(((100 - self.config[IMAGE_AREA]) / 100) * self.config[FONT_HEIGHT_PERCENT])
        else:
            font_size = int((button_height / 100) * self.config[FONT_HEIGHT_PERCENT])

        self.navigator = RadioNavigator(self.util, self.layout.BOTTOM, listeners, "ya.stream.navigator")
        self.add_navigator(self.navigator)
        self.left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        self.right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)
        self.player_button = self.navigator.get_button_by_name(KEY_PLAYER)

        h = self.config[HORIZONTAL_LAYOUT]
        self.ya_stream_menu = Menu(util, bgr, self.menu_layout, rows, columns, create_item_method=m, align=ALIGN_LEFT, horizontal_layout=h, font_size=font_size)
        self.set_menu(self.ya_stream_menu)
        
        self.current_page = None
        self.YA_STREAM_LABEL = util.config[LABELS][YA_STREAM]
        self.turn_page()

        self.animated_title = True

    def create_ya_stream_browser_menu_button(self, state, constr, action, scale, font_size):
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

        b = self.factory.create_menu_button(s, constr, action, scale, label_area_percent=label_area_percent, show_label=s.show_label, font_size=font_size)

        return b

    def set_current(self, state):
        """ Set current state
        
        :param state: button state
        """
        self.turn_page()

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
        playlist = self.ya_stream_util.get_ya_stream_playlist()
        playlist_length = len(playlist)
        self.total_pages = math.ceil(playlist_length / self.page_size)
        
        if self.total_pages == 0:
            self.left_button.change_label("0")
            self.right_button.change_label("0")
            return []
        
        if self.current_page == None:
            self.current_page = self.get_page_by_id()

        start = (self.current_page - 1) * self.page_size
        end = self.current_page * self.page_size

        return playlist[start : end]

    def get_page_by_id(self):
        """ Get the page by index

        :return: the page
        """
        id = None
        page = 1
        try:
            id = self.config[YA_STREAM][YA_STREAM_ID]
        except:
            pass

        if not id:
            return page
        
        index = self.ya_stream_util.get_index_by_id(id)
        if index < self.page_size:
            page = 1
        else:
            page = math.ceil(index / self.page_size)

        return page

    def turn_page(self):
        """ Turn page """

        page = self.get_page()
        d = self.ya_stream_menu.make_dict(page)
        self.ya_stream_menu.set_items(d, 0, self.change_stream, False)

        id = self.config[YA_STREAM][YA_STREAM_ID]

        if not self.config[YA_STREAM][YA_STREAM_NAME]:
            self.screen_title.set_text(self.YA_STREAM_LABEL)
        else:
            self.screen_title.set_text(self.config[YA_STREAM][YA_STREAM_NAME])
        
        index = self.ya_stream_util.get_index_by_id(id)
        menu_selected = self.ya_stream_menu.select_by_index(index)

        if self.navigator and self.total_pages > 1:
            self.left_button.change_label(str(self.current_page - 1))
            self.right_button.change_label(str(self.total_pages - self.current_page))
        else:
            self.left_button.change_label("0")
            self.right_button.change_label("0")

        for b in self.ya_stream_menu.buttons.values():
            b.parent_screen = self

        self.ya_stream_menu.clean_draw_update()
        if menu_selected:
            self.navigator.unselect()

        self.link_borders()
        navigator_selected = self.navigator.is_selected()

        if (len(page) == 0 or (not menu_selected and not navigator_selected)) and self.navigator:
            self.navigator.unselect()
            self.player_button.set_selected(True)
            self.player_button.clean_draw_update()

    def change_stream(self, state):
        """ Change stream

        :param state: state object
        """
        state.source = KEY_YA_STREAM_BROWSER
        state.name = state.l_name
        state.time = "0.0"

        self.go_player(state)
