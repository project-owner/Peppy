# Copyright 2021-2023 Peppy Player peppy.player@gmail.com
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

from copy import copy
from ui.screen.menuscreen import MenuScreen 
from ui.menu.menu import Menu, ALIGN_CENTER
from ui.factory import Factory
from util.favoritesutil import FavoritesUtil
from util.config import LIST_VIEW_ROWS, LIST_VIEW_COLUMNS, PADDING, IMAGE_AREA, ALIGN_BUTTON_CONTENT_X, \
    H_ALIGN_LEFT, H_ALIGN_RIGHT, H_ALIGN_CENTER, WRAP_LABELS, IMAGE_SIZE, HIDE_FOLDER_NAME, FONT_HEIGHT_PERCENT, \
    CURRENT, LANGUAGE, HORIZONTAL_LAYOUT, BACKGROUND, MENU_BGR_COLOR
from ui.navigator.radio import RadioNavigator
from ui.layout.buttonlayout import CENTER, LEFT, RIGHT, TOP, BOTTOM
from util.keys import KEY_PLAYER, KEY_RADIO_BROWSER, KEY_FAVORITES, KEY_PAGE_DOWN, KEY_PAGE_UP

ICON_LOCATION = TOP
BUTTON_PADDING = 5
ICON_AREA = 70
ICON_SIZE = 60

class RadioBrowserScreen(MenuScreen):
    """ Radio Browser Screen """
    
    def __init__(self, util, listeners):
        """ Initializer
        
        :param util: utility object
        :param listeners: screen event listeners
        """
        self.util = util
        self.config = util.config
        self.groups_list = self.util.get_stations_folders()
        self.factory = Factory(util)
        self.favorites_util = FavoritesUtil(self.util)
        rows = self.config[LIST_VIEW_ROWS]
        columns = self.config[LIST_VIEW_COLUMNS]
        d = [rows, columns]
        self.page_size = rows * columns

        MenuScreen.__init__(self, util, listeners, rows, columns, d, self.turn_page, page_in_title=False)
        self.total_pages = 0
        self.title = ""
        m = self.create_radio_browser_menu_button
        button_height = (self.menu_layout.h / rows) - (self.config[PADDING] * 2)
        bgr = self.config[BACKGROUND][MENU_BGR_COLOR]

        if self.config[ALIGN_BUTTON_CONTENT_X] == 'center':
            font_size = int(((100 - self.config[IMAGE_AREA]) / 100) * self.config[FONT_HEIGHT_PERCENT])
        else:
            font_size = int((button_height / 100) * self.config[FONT_HEIGHT_PERCENT])

        self.navigator = RadioNavigator(self.util, self.layout.BOTTOM, listeners)
        self.add_navigator(self.navigator)
        self.left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        self.right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)
        self.player_button = self.navigator.get_button_by_name(KEY_PLAYER)

        h = self.config[HORIZONTAL_LAYOUT]
        self.stations_menu = Menu(util, bgr, self.menu_layout, rows, columns, create_item_method=m, align=ALIGN_CENTER, horizontal_layout=h, font_size=font_size)
        self.set_menu(self.stations_menu)
        
        self.current_page = None
        self.current_language = self.config[CURRENT][LANGUAGE]
        self.current_genre = self.util.get_current_genre()
        self.turn_page()

        self.animated_title = True

    def create_radio_browser_menu_button(self, state, constr, action, scale, font_size):
        """ Factory function for menu button

        :param state: button state
        :param constr: bounding box
        :param action: action listener
        :param scale: True - sacle, False - don't scale
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
        s.scaled = True
        self.util.add_icon(s, self.get_scale_factor(s))

        scale = True
        if hasattr(s, "show_label"):
            b = self.factory.create_menu_button(s, constr, action, scale, label_area_percent=label_area_percent, show_label=s.show_label, font_size=font_size)
        else:
            b = self.factory.create_menu_button(s, constr, action, scale, label_area_percent=label_area_percent, font_size=font_size)

        b.state.icon_selected_scaled = b.state.icon_base_scaled
        b.state.icon_selected = s.icon_base
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

    def get_playlist(self, genre=None):
        """ Get playlist

        :param genre: the genre

        :return: the playlist
        """
        if genre and genre == KEY_FAVORITES:
            return self.favorites_util.get_favorites_playlist()
        else:
            return self.util.get_radio_browser_playlist(genre)

    def get_page(self):
        """ Get the current page from the playlist

        :return: the page
        """
        language = self.config[CURRENT][LANGUAGE]
        genre = self.util.get_current_genre()
        playlist = self.get_playlist(genre.l_name)
        playlist_length = len(playlist)
        self.total_pages = math.ceil(playlist_length / self.page_size)
        
        if self.current_page == None or language != self.current_language or self.current_genre != genre:
            self.current_language = language
            self.current_genre = genre
            playlist = self.get_playlist(genre.l_name)
            playlist_length = len(playlist)
            self.total_pages = math.ceil(playlist_length / self.page_size)
            if self.total_pages == 0:
                self.left_button.change_label("0")
                self.right_button.change_label("0")
                self.set_title()
                return []
            self.current_page = self.get_page_by_index()
        
        self.set_title()
        self.stations_menu.current_page = self.current_page

        start = (self.current_page - 1) * self.page_size
        end = self.current_page * self.page_size
        return playlist[start : end]

    def get_page_by_index(self):
        """ Get the page by index

        :return: the page
        """
        page = None
        index = self.util.get_current_radio_station_index()
        if index < self.page_size:
            page = 1
        else:
            page = math.ceil(index / self.page_size)
        return page

    def set_title(self):
        """ Set the screen title """

        genre = self.util.get_current_genre()
        if genre.name == KEY_FAVORITES:
            station = self.favorites_util.get_current_favorites_station()
        else:
            station = self.util.get_current_radio_station()

        if station:
            title = station.comparator_item
        else:
            title = ""
        d = {"current_title" : title}
        self.screen_title.set_text(d)

    def turn_page(self):
        """ Turn page """
        
        page = self.get_page()
        d = self.stations_menu.make_dict(page)
        self.stations_menu.set_items(d, 0, self.change_station, False)
        self.favorites_util.mark_favorites(self.stations_menu.buttons)
        index = self.util.get_current_radio_station_index()
        menu_selected = self.stations_menu.select_by_index(index)

        if self.navigator and self.total_pages > 1:
            self.left_button.change_label(str(self.current_page - 1))
            self.right_button.change_label(str(self.total_pages - self.current_page))
        else:
            self.left_button.change_label("0")
            self.right_button.change_label("0")

        for b in self.stations_menu.buttons.values():
            b.parent_screen = self
            b.release_listeners.insert(0, self.handle_favorite)

        self.stations_menu.clean_draw_update()
        if menu_selected:
            self.navigator.unselect()

        self.link_borders()
        navigator_selected = self.navigator.is_selected()

        if (len(page) == 0 or (not menu_selected and not navigator_selected)) and self.navigator:
            self.navigator.unselect()
            self.player_button.set_selected(True)
            self.player_button.clean_draw_update()
        
    def change_station(self, state):
        """ Change station

        :param state: state object
        """
        found = False
        for b in self.stations_menu.buttons.values():
            if b.state == state:
                found = True
                break

        if not found: # after deleting favorite
            playlist = self.get_playlist(self.current_genre.l_name)
            index = self.util.get_current_radio_station_index()
            if playlist and len(playlist) > 0:
                state = playlist[index]
            else:
                state = None

        if state:
            state.source = KEY_RADIO_BROWSER
            state.name = self.util.get_current_genre().name
            self.util.set_radio_station_index(state.index)
        else:
            self.util.set_radio_station_index(None)
        self.go_player(state)
        self.set_title()
        
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.navigator.add_observers(update_observer, redraw_observer)
        self.stations_menu.add_menu_observers(update_observer, redraw_observer, release=False)

    def set_current(self, state=None):
        """ Set current screen

        :param state: the source button state object
        """
        self.turn_page()

    def handle_event(self, event):
        """ Handle screen event

        :param event: the event to handle
        """
        self.handle_event_common(event)

    def handle_favorite(self, state):
        """ Add/Remove station to/from the favorites
        
        :param state: button state
        """
        if state == None or not getattr(state, "long_press", False):
            return

        favorites, lang_dict = self.favorites_util.get_favorites_from_config()
        
        if self.favorites_util.is_favorite(favorites, state):
            self.favorites_util.remove_favorite(favorites, state)
            if self.current_genre.name == KEY_FAVORITES:
                current_index = state.index
                if len(favorites) == 0:
                    self.util.set_radio_station_index(None)
                else:
                    if current_index == 0:
                        self.util.set_radio_station_index(0)
                    else:
                        self.util.set_radio_station_index(current_index - 1)
                self.turn_page()
            else:
                selected_button = self.stations_menu.get_selected_item()
                if selected_button and len(selected_button.components) == 4:
                    del selected_button.components[3]
                    selected_button.clean_draw_update()        
        else:
            self.favorites_util.add_favorite(favorites, state)
            self.favorites_util.mark_favorites(self.stations_menu.buttons)
