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

import os
import math

from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.screen.menuscreen import MenuScreen
from ui.menu.menu import ALIGN_CENTER
from util.keys import KEY_PODCAST_EPISODES
from util.config import COLORS, COLOR_DARK_LIGHT, LABELS, PODCASTS, PODCAST_URL
from ui.menu.multipagemenu import MultiPageMenu
from util.podcastsutil import PodcastsUtil, MENU_ROWS_PODCASTS, MENU_COLUMNS_PODCASTS, PAGE_SIZE_PODCASTS
from ui.menu.podcastnavigator import PodcastNavigator

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

class PodcastsScreen(MenuScreen):
    """ Podcasts Screen """
    
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
        
        self.podcasts_util = util.get_podcasts_util()        
        self.bounding_box = util.screen_rect
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)
        
        d = [MENU_ROWS_PODCASTS, MENU_COLUMNS_PODCASTS]
        MenuScreen.__init__(self, util, listeners, MENU_ROWS_PODCASTS, MENU_COLUMNS_PODCASTS, voice_assistant, d, self.turn_page, page_in_title=False, show_loading=True)        
        self.title = self.config[LABELS][PODCASTS]
        
        m = self.factory.create_podcast_menu_button
        self.podcasts_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, self.go_to_page, m, MENU_ROWS_PODCASTS, MENU_COLUMNS_PODCASTS, None, (0, 0, 0), self.menu_layout, align=ALIGN_CENTER)
        self.set_menu(self.podcasts_menu)
        
        self.navigator = PodcastNavigator(self.util, self.layout.BOTTOM, listeners, self.config[COLORS][COLOR_DARK_LIGHT], PAGE_SIZE_PODCASTS + 1)
        self.components.append(self.navigator)
        
        url = self.config[PODCASTS][PODCAST_URL]
        if url and len(url) > 0:
            self.current_page = self.podcasts_util.get_podcast_page(url, PAGE_SIZE_PODCASTS)
        else:
            self.current_page = 1

        self.animated_title = True
        
    def set_current(self, state):
        """ Set current state
        
        :param state: button state
        """
        if self.util.connected_to_internet:
            podcast_links_num = len(self.podcasts_util.get_podcasts_links())
        else:
            podcast_links_num = len(self.podcasts_util.load_podcasts())
        
        self.total_pages = math.ceil(podcast_links_num / PAGE_SIZE_PODCASTS)
        
        self.set_loading(self.title)        
        self.turn_page()
        self.reset_loading()        
  
    def turn_page(self):
        """ Turn podcasts page """

        page = {}
        if self.util.connected_to_internet:
            page = self.podcasts_util.get_podcasts(self.current_page, PAGE_SIZE_PODCASTS)
        
        if len(list(page.keys())) == 0 or not self.util.connected_to_internet:
            page = self.podcasts_util.get_podcasts_from_disk(self.current_page, PAGE_SIZE_PODCASTS)
            
        self.podcasts_menu.set_items(page, 0, self.listeners[KEY_PODCAST_EPISODES], False)
        
        keys = list(page.keys())
        
        if len(keys) != 0:
            self.podcasts_menu.item_selected(page[keys[0]])
            if self.navigator and self.total_pages > 1:
                self.navigator.left_button.change_label(str(self.current_page - 1))
                self.navigator.right_button.change_label(str(self.total_pages - self.current_page))
            
        self.set_title(self.current_page)
        self.podcasts_menu.clean_draw_update()
        
        if hasattr(self, "update_observer"):
            self.podcasts_menu.add_menu_observers(self.update_observer, self.redraw_observer)
        
        self.podcasts_menu.unselect()
        for i, b in enumerate(self.podcasts_menu.buttons.values()):
            url = self.config[PODCASTS][PODCAST_URL]
            if url == b.state.url:
                self.podcasts_menu.select_by_index(i)
                return
        self.podcasts_menu.select_by_index(0)
    
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
        