# Copyright 2018 Peppy Player peppy.player@gmail.com
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

from ui.container import Container
from ui.screen.menuscreen import MenuScreen 
from ui.menu.multipagemenu import MultiPageMenu
from util.keys import KEY_CHOOSE_GENRE, LABELS, GENRE
from ui.menu.menu import ALIGN_MIDDLE
from ui.factory import Factory
from util.util import KEY_GENRE
from util.config import COLORS, COLOR_DARK_LIGHT, CURRENT, LANGUAGE, CURRENT_STATIONS, STATIONS
from ui.menu.radiogroupnavigator import RadioGroupNavigator
from ui.layout.borderlayout import BorderLayout
import math

MENU_ROWS = 3
MENU_COLUMNS = 3
PAGE_SIZE = MENU_ROWS * MENU_COLUMNS

class RadioGroupScreen(MenuScreen):
    """ Radio group screen """
    
    def __init__(self, util, listeners, voice_assistant):
        self.util = util
        self.config = util.config
        self.groups_list = self.util.get_stations_folders()
        self.factory = Factory(util)
        d = [MENU_ROWS, MENU_COLUMNS]
        MenuScreen.__init__(self, util, listeners, MENU_ROWS, MENU_COLUMNS, voice_assistant, d, self.turn_page, page_in_title=False)
        self.total_pages = math.ceil(len(self.groups_list) / PAGE_SIZE)
        self.title = util.get_stations_top_folder()
        m = self.factory.create_genre_menu_button
        
        self.groups_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, m, MENU_ROWS, MENU_COLUMNS, None, (0, 0, 0), self.menu_layout, align=ALIGN_MIDDLE)
        self.groups_menu.add_listener(listeners[KEY_GENRE])
        self.set_menu(self.groups_menu)
        
        color_dark_light = self.config[COLORS][COLOR_DARK_LIGHT]
        self.navigator = RadioGroupNavigator(self.util, self.layout.BOTTOM, listeners, color_dark_light, self.total_pages)
        self.components.append(self.navigator)
        
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
    
    def get_current_group_name(self):
        key = STATIONS + "." + self.config[CURRENT][LANGUAGE]
        name = None
        try:
            name = self.config[key][CURRENT_STATIONS]
        except:
            pass
        return name
    
    def get_page(self):
        start = (self.current_page - 1) * PAGE_SIZE
        end = self.current_page * PAGE_SIZE
        page = self.groups_list[start : end]          
        tmp_layout = self.groups_menu.get_layout(self.groups_list)        
        button_rect = tmp_layout.constraints[0]
        groups_dict = self.util.load_stations_folders(button_rect)
        
        return self.util.get_radio_group_slice(groups_dict, start, end)
        
    def turn_page(self):
        """ Turn book genre page """
        
        group_page = self.get_page()
        self.groups_menu.set_items(group_page, 0, self.change_group, False)
        current_name = self.get_current_group_name()
        
        try:
            self.current_genre = group_page[current_name]
            self.groups_menu.item_selected(self.current_genre)
        except:
            keys = list(group_page.keys())
            self.groups_menu.item_selected(group_page[keys[0]])

        if self.navigator and self.total_pages > 1:
            self.navigator.left_button.change_label(str(self.current_page - 1))
            self.navigator.right_button.change_label(str(self.total_pages - self.current_page))
            
        self.set_title(self.current_page)
        self.groups_menu.clean_draw_update()
        
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
        
    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.navigator.add_observers(update_observer, redraw_observer)
        self.groups_menu.add_menu_observers(update_observer, redraw_observer, release=False)
