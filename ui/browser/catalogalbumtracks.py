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

from ui.browser.catalogbase import CatalogBase
from util.keys import KEY_PLAYER, CATALOG_TRACKS, KEY_CATALOG_SERVICE
from util.config import PADDING, IMAGE_AREA, ALIGN_BUTTON_CONTENT_X, H_ALIGN_LEFT, H_ALIGN_RIGHT, H_ALIGN_CENTER
from ui.layout.buttonlayout import CENTER, LEFT, RIGHT, TOP, BOTTOM
from copy import copy
from util.streamingservice import ALBUM_IMAGE_LARGE

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

ICON_LOCATION = LEFT
BUTTON_PADDING = 5
ICON_AREA = 0
ICON_SIZE = 0
FONT_HEIGHT = 16

class CatalogAlbumTracks(CatalogBase):
    """ Catalog Album Tracks Screen """
    
    def __init__(self, util, mode, listeners, title, custom_nav_button):
        """ Initializer

        :param util: utility object
        :param mode: browser mode
        :param listeners: screen event listeners
        :param title: screen title
        :param custom_nav_button: custom navigator button
        """
        CatalogBase.__init__(self, util, mode, listeners, title, custom_nav_button)
        self.go_player = listeners[KEY_PLAYER]
        self.album_change_listeners = []
        self.album_cache = set()

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
        s.show_img = False

        b = self.factory.create_menu_button(s, constr, action, scale, label_area_percent=label_area_percent, 
                                            show_img=s.show_img, show_label=s.show_label, font_size=font_size)
        return b

    def set_current(self, state):
        """ Set current state

        :param state: button state
        """
        source = getattr(state, "source", None)
        state_title = getattr(state, "title", None)
        id = getattr(state, "id", None)

        if (source == "resume" or source == "back" or self.screen_title.text == state_title) and self.config.get(CATALOG_TRACKS, None):
            return

        if not getattr(state, "name", None):
            return

        if self.album_menu.buttons and getattr(state, "id", None) == None:
            return

        self.album_image_large = getattr(state, ALBUM_IMAGE_LARGE, None)

        artist_name = getattr(state, "artist_name", None)
        if artist_name:
            title = artist_name + " - " + state.name
        else:
            title = state.name

        self.screen_title.set_text(title)
        self.album_id = getattr(state, "id", None)
        self.current_page = 1
        self.notify_album_change_listeners()

        if id not in self.album_cache:
            self.set_loading(None)

        svc = getattr(state, KEY_CATALOG_SERVICE, None)
        if svc:
            self.util.set_scatalog_ervice(svc)

        self.turn_page()

        if id not in self.album_cache:
            self.reset_loading()

        if id:
            self.album_cache.add(id)

    def turn_page(self):
        """ Turn page """

        page = self.get_page()

        if not page:
            return

        d = self.album_menu.make_dict(page)
        self.album_menu.set_items(d, 0, self.change_item, False, lazy_load_images=True)

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

    def get_page(self):
        """ Get the current page from the playlist

        :return: the page
        """
        self.total_pages = 0
        searcher = self.get_service_searcher()
        items = searcher(self.album_id)

        if items:
            self.config[CATALOG_TRACKS] = items
            self.total_pages = math.ceil(len(items) / self.page_size)
            start = (self.current_page - 1) * self.page_size
            stop = start + self.page_size
            return items[start : stop]
        else:
            self.total_pages = 0
            self.config[CATALOG_TRACKS] = []
            self.left_button.change_label("0")
            self.right_button.change_label("0")
            return []

    def change_item(self, state):
        """ Change item

        :param state: state object
        """
        state.source = self.mode
        if not hasattr(state, ALBUM_IMAGE_LARGE):
            state.album_image_large = self.album_image_large
        self.go_player(state)

    def handle_track_change(self, state):
        """ Handle track change event

        :param state: event state object
        """
        if getattr(state, "index", None) == None:
            return

        page_start_index = (self.current_page - 1) * self.page_size
        page_end_index = self.current_page * self.page_size - 1
        length = len(self.config[CATALOG_TRACKS])

        if state.index == 0 and self.current_page != 1:
            self.current_page = 1
            self.turn_page()
        elif state.index == length - 1 and self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self.turn_page()
        elif state.index > page_end_index:
            self.current_page += 1
            self.turn_page()
        elif state.index < page_start_index:
            self.current_page -= 1
            self.turn_page()    

        for button in self.album_menu.buttons.values():
            if button.state.index == state.index:
                button.set_selected(True)
                self.album_menu.selected_index = state.index
                self.navigator.unselect()
            else:
                button.set_selected(False)
            
            if self.album_menu.visible:
                button.clean()
                button.draw()

        self.update_component = True

    def add_album_change_listener(self, listener):
        """ Add album change listener

        :param listener: event listener
        """
        if listener not in self.album_change_listeners:
            self.album_change_listeners.append(listener)

    def notify_album_change_listeners(self):
        """ Notify all album change listeners """

        for listener in self.album_change_listeners:
            try:
                listener()
            except:
                pass
