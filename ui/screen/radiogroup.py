# Copyright 2018-2024 Peppy Player peppy.player@gmail.com
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
from util.keys import GENRE, KEY_PAGE_DOWN, KEY_PAGE_UP, KEY_PLAYER, KEY_GENRE
from ui.menu.menu import ALIGN_CENTER
from ui.factory import Factory
from util.config import CURRENT, LANGUAGE, CURRENT_STATIONS, STATIONS
from ui.navigator.radiogroup import RadioGroupNavigator
from ui.layout.buttonlayout import TOP, CENTER

MENU_ROWS = 3
MENU_COLUMNS = 3
PAGE_SIZE = MENU_ROWS * MENU_COLUMNS

ICON_LOCATION = TOP
BUTTON_PADDING = 5
ICON_AREA = 70
ICON_SIZE = 60
FONT_HEIGHT = 60

class RadioGroupScreen(MenuScreen):
    """ Radio group screen """
    
    def __init__(self, util, listeners):
        self.util = util
        self.config = util.config
        self.groups_list = self.util.get_stations_folders()
        self.factory = Factory(util)
        d = [MENU_ROWS, MENU_COLUMNS]
        MenuScreen.__init__(self, util, listeners, d, self.turn_page, page_in_title=False)
        self.total_pages = math.ceil(len(self.groups_list) / PAGE_SIZE)
        self.title = util.get_stations_top_folder()
        m = self.create_genre_menu_button
        label_area = ((self.menu_layout.h / MENU_ROWS) / 100) * (100 - ICON_AREA)
        font_size = int((label_area / 100) * FONT_HEIGHT)
        
        self.navigator = RadioGroupNavigator(self.util, self.layout.BOTTOM, listeners, self.total_pages)
        self.add_navigator(self.navigator)
        self.player_button = self.navigator.get_button_by_name(KEY_PLAYER)
        if self.total_pages > 1:
            self.left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
            self.right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)

        self.groups_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, m, MENU_ROWS, MENU_COLUMNS, None, (0, 0, 0, 0), self.menu_layout, align=ALIGN_CENTER, font_size=font_size)
        self.groups_menu.add_listener(listeners[KEY_GENRE])
        self.set_menu(self.groups_menu)
        
        current_name = self.get_current_group_name()
        
        if current_name == None:
            self.current_page = 1            
        else:
            try:
                current_group_index = self.groups_list.index(current_name)
                self.current_page = int(current_group_index / PAGE_SIZE) + 1
            except:
                current_group_index = 0
        
        self.turn_page()

    def create_genre_menu_button(self, s, constr, action, scale, font_size):
        """ Create Genre Menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images

        :return: genre menu button
        """
        s.padding = BUTTON_PADDING
        s.image_area_percent = ICON_AREA
        s.fixed_height = font_size
        s.v_align = CENTER

        return self.factory.create_menu_button(s, constr, action, scale, font_size=font_size)

    def get_current_group_name(self):
        group = self.util.get_current_genre()
        if group != None:
            return group.name
        else:
            return None

    def get_page(self):
        start = (self.current_page - 1) * PAGE_SIZE
        end = self.current_page * PAGE_SIZE
        tmp_layout = self.groups_menu.get_layout(self.groups_list)        
        button_rect = tmp_layout.constraints[0]
        image_box = self.factory.get_icon_bounding_box(button_rect, ICON_LOCATION, ICON_AREA, ICON_SIZE, BUTTON_PADDING)
        groups_dict = self.util.load_stations_folders(image_box)
        
        return self.util.get_radio_group_slice(groups_dict, start, end)
        
    def turn_page(self):
        """ Turn book genre page """
        
        group_page = self.get_page()
        self.groups_menu.set_items(group_page, 0, self.change_group, False)
        current_name = self.get_current_group_name()
        self.current_genre = None
        try:
            self.current_genre = group_page[current_name]
        except:
            pass
        self.groups_menu.item_selected(self.current_genre)

        if self.navigator and self.total_pages > 1:
            self.left_button.change_label(str(self.current_page - 1))
            self.right_button.change_label(str(self.total_pages - self.current_page))

        for b in self.groups_menu.buttons.values():
            b.parent_screen = self

        self.groups_menu.clean_draw_update()
        menu_selected = self.groups_menu.get_selected_item() != None
        if menu_selected:
            self.navigator.unselect()

        self.link_borders()
        navigator_selected = self.navigator.is_selected()
        if (len(group_page) == 0 or (not menu_selected and not navigator_selected)) and self.navigator:
            self.navigator.unselect()
            self.player_button.set_selected(True)
            self.player_button.clean_draw_update()

        self.set_title(self.current_page)
        
    def change_group(self, state):
        """ Change group event listener
         
        :param state: button state
        """
        if not self.visible:
            return
        self.current_genre = state
         
        key = STATIONS + "." + self.config[CURRENT][LANGUAGE]
        self.config[key][CURRENT_STATIONS] = state.genre
        state.source = GENRE        
        self.groups_menu.notify_listeners(state)
    
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
        self.groups_menu.add_menu_observers(update_observer, redraw_observer, release=False)
