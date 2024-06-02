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
import logging

from ui.component import Component
from ui.screen.menuscreen import MenuScreen
from ui.factory import Factory
from util.keys import *
from util.config import *
from ui.layout.buttonlayout import CENTER, LEFT, RIGHT, TOP, BOTTOM
from ui.menu.menu import Menu, ALIGN_LEFT
from ui.navigator.catalogbase import CatalogBaseNavigator
from copy import copy
from util.serviceutil import MENU_PAGE_SIZE, MENU_COLUMNS, MENU_ROWS
from multiprocessing.dummy import Pool
from util.streamingservice import ALBUM_IMAGE_SMALL, ALBUM_IMAGE_LARGE

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

ICON_LOCATION = LEFT
BUTTON_PADDING = 5
ICON_AREA = 0
ICON_SIZE = 0
FONT_HEIGHT = 16

class CatalogBase(MenuScreen):
    """ Catalog Base Screen """

    def __init__(self, util, mode, listeners, title, custom_nav_button=None):
        """ Initializer

        :param util: utility object
        :param mode: browser mode
        :param listeners: screen event listeners
        :param title: screen title
        :param custom_nav_button: custom navigator button
        """
        self.util = util
        self.image_util = util.image_util
        self.mode = mode
        self.go_to_details = listeners[KEY_DETAILS]

        self.config = util.config
        self.factory = Factory(util)

        d = [MENU_ROWS, MENU_COLUMNS]
        self.page_size = MENU_PAGE_SIZE

        MenuScreen.__init__(self, util, listeners, d, self.turn_page, page_in_title=False)
        self.total_pages = 0
        self.title = title
        self.screen_title.set_text(self.title)
        m = self.create_catalog_album_menu_button
        button_height = (self.menu_layout.h / MENU_ROWS) - (self.config[PADDING] * 2)
        bgr = self.config[BACKGROUND][MENU_BGR_COLOR]

        if self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            font_size = int(((100 - self.config[IMAGE_AREA]) / 100) * self.config[FONT_HEIGHT_PERCENT])
        else:
            font_size = int((button_height / 100) * self.config[FONT_HEIGHT_PERCENT])

        self.navigator = CatalogBaseNavigator(self.util, self.layout.BOTTOM, listeners, "catalog.album.navigator", custom_nav_button)
        self.add_navigator(self.navigator)
        self.left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        self.right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)
        self.player_button = self.navigator.get_button_by_name(KEY_PLAYER)

        h = self.config[HORIZONTAL_LAYOUT]
        self.album_menu = Menu(util, bgr, self.menu_layout, MENU_ROWS, MENU_COLUMNS, create_item_method=m, align=ALIGN_LEFT, horizontal_layout=h, font_size=font_size)
        self.set_menu(self.album_menu)

        self.total_items = 0
        self.items = []
        self.current_page = 1
        self.animated_title = True
        self.current_album = None
        self.album_cache = set()
        self.query = None

    def create_catalog_album_menu_button(self, state, constr, action, scale, font_size):
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
        s.show_label = True
        s.show_img = True

        b = self.factory.create_menu_button(s, constr, action, scale, label_area_percent=label_area_percent, 
                                            show_img=s.show_img, show_label=s.show_label, font_size=font_size)
        return b

    def get_service_searcher(self):
        """ Lazy load Service Utility

        :return: service utility
        """
        if not hasattr(self.util, "service_util"):
            from util.serviceutil import ServiceUtil
            self.util.service_util = ServiceUtil()

        return self.util.service_util.searchers[self.mode]

    def set_current(self, state):
        """ Set current state

        :param state: button state
        """
        source = getattr(state, "source", None)
        id = getattr(state, "id", None)

        if source == "menu" or source == "back" or source == self.mode or source == "album" or source == "artist":
            return

        if self.current_album and self.current_album == getattr(state, "url", None):
            return

        self.current_album = getattr(state, "url", None)
        if hasattr(state, "title"):
            self.title = state.title
            self.screen_title.set_text(self.title)

        if id not in self.album_cache:
            self.set_loading(None)

        svc = getattr(state, KEY_CATALOG_SERVICE, None)
        if svc:
            self.util.set_scatalog_ervice(svc)

        self.turn_page(state)
        if id not in self.album_cache:
            self.reset_loading()

        if id:
            self.album_cache.add(id)

    def get_page(self, state=None):
        """ Get the current page from the playlist

        :return: the page
        """
        items = []
        try:
            searcher = self.get_service_searcher()
        except Exception as e:
            logging.debug(e)
            return []

        if state and getattr(state, "id", None) != None:
            items = searcher(getattr(state, "id", None))
        else:
            if self.current_album:
                tokens = self.current_album.split("/")
                id = tokens[-1]
                if "?" in id:
                    tokens = id.split("?")
                    id = tokens[0]
                items = searcher(id)
            else:
                query = getattr(state, "callback_var", None)
                if state and query:
                    self.query = query
                    self.current_page = 1
                    self.total_pages = 0
                    self.left_button.change_label("0")
                    self.right_button.change_label("0")
                    items = searcher(query, self.current_page - 1)
                else:
                    if self.query:
                        items = searcher(self.query, self.current_page - 1)
                    else:
                        items = searcher(self.current_page - 1)
        if items:
            if isinstance(items, list):
                if len(items) <= self.page_size:
                    return items
                self.total_pages = math.ceil(len(items) / self.page_size)
                start = (self.current_page - 1) * self.page_size
                stop = start + self.page_size
                return items[start : stop]
            else:
                self.total_pages = items[0]
                return items[1]
        else:
            self.total_pages = 0
            self.left_button.change_label("0")
            self.right_button.change_label("0")
            return []

    def turn_page(self, state=None):
        """ Turn page """

        page = self.get_page(state)

        if not page:
            return

        d = self.album_menu.make_dict(page)
        self.album_menu.set_items(d, 0, self.change_item, False, lazy_load_images=True)

        pool = Pool(processes=MENU_PAGE_SIZE)
        pool.map(self.set_image, self.album_menu.buttons.values())
        pool.close()
        pool.join()

        if self.navigator and self.total_pages > 1:
            self.left_button.change_label(str(self.current_page - 1))
            self.right_button.change_label(str(self.total_pages - self.current_page))
        else:
            self.left_button.change_label("0")
            self.right_button.change_label("0")

        for b in self.album_menu.buttons.values():
            b.parent_screen = self

        self.album_menu.clean_draw_update()
        self.link_borders()
        navigator_selected = self.navigator.is_selected()

        if (len(page) == 0 or not navigator_selected) and self.navigator:
            self.navigator.unselect()
            self.player_button.set_selected(True)
            self.player_button.clean_draw_update()

        self.clean()
        self.draw()
        self.update_component = True

    def set_image(self, b):
        """ Set button image

        :param b: button
        """
        img_rect = b.layout.image_rectangle
        x = img_rect.x
        y = img_rect.y
        url = None

        if hasattr(b.state, ALBUM_IMAGE_SMALL):
            url = getattr(b.state, ALBUM_IMAGE_SMALL, None)
        elif hasattr(b.state, ALBUM_IMAGE_LARGE):
            url = getattr(b.state, ALBUM_IMAGE_LARGE, None)

        img = self.get_image_from_cache(url)
        if img:
            if b.components[1] == None:
                c = Component(self.util)
                b.components[1] = c
                c.name = GENERATED_IMAGE + str(b.state.index)
                c.image_filename = c.name
            self.set_button_image(b, img, x, y)
        else:
            if url:
                c = Component(self.util)
                b.components[1] = c
                c.name = GENERATED_IMAGE + str(b.state.index)
                c.image_filename = c.name
                if url.startswith("http"):
                    img = self.image_util.load_menu_screen_image(url, img_rect.w, img_rect.h)
                else:
                    img = self.image_util.load_icon_main(url, img_rect, 0.7)
                    if img:
                        img = img[1]
                if img:
                    self.set_button_image(b, img, x, y)
                    self.put_image_to_cache(url, img)
        b.clean()
        b.draw()

    def set_button_image(self, b, icon, x, y):
        """ Set button image

        :param b: button
        :param icon: image
        :param x: image X coordinate
        :param y: image Y coordinate
        """
        c = b.components[1]
        c.content = icon            
        c.content_x = x + int((b.bounding_box.w / 100) * self.config[PADDING])
        c.content_y = y + (b.bounding_box.h/2 - icon.get_size()[1]/2)

    def change_item(self, state):
        """ Change item

        :param state: state object
        """
        state.source = self.mode
        self.go_to_details(state)
