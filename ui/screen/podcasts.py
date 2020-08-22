# Copyright 2019-2020 Peppy Player peppy.player@gmail.com
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
from util.keys import KEY_PODCAST_EPISODES, V_ALIGN_TOP, H_ALIGN_LEFT
from util.config import COLORS, COLOR_DARK_LIGHT, COLOR_BRIGHT, COLOR_MEDIUM, COLOR_CONTRAST, LABELS, PODCASTS, \
    PODCAST_URL, BACKGROUND, MENU_BGR_COLOR
from ui.menu.multipagemenu import MultiPageMenu
from util.podcastsutil import PodcastsUtil, MENU_ROWS_PODCASTS, MENU_COLUMNS_PODCASTS, PAGE_SIZE_PODCASTS
from ui.menu.podcastnavigator import PodcastNavigator
from ui.button.podcastbutton import PodcastButton
from ui.layout.buttonlayout import LEFT, CENTER

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

ICON_LOCATION = LEFT
BUTTON_PADDING = 5
ICON_AREA = 25
ICON_SIZE = 80
FONT_HEIGHT = 16

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
        MenuScreen.__init__(self, util, listeners, MENU_ROWS_PODCASTS, MENU_COLUMNS_PODCASTS, voice_assistant, d, self.turn_page, 
            page_in_title=False, show_loading=True)        
        self.title = self.config[LABELS][PODCASTS]
        
        m = self.create_podcast_menu_button
        font_size = int(((self.menu_layout.h / MENU_ROWS_PODCASTS) / 100) * FONT_HEIGHT)
        self.podcasts_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title, 
            self.go_to_page, m, MENU_ROWS_PODCASTS, MENU_COLUMNS_PODCASTS, None, (0, 0, 0, 0), self.menu_layout, align=ALIGN_CENTER, font_size=font_size)
        self.set_menu(self.podcasts_menu)
        
        self.navigator = PodcastNavigator(self.util, self.layout.BOTTOM, listeners, PAGE_SIZE_PODCASTS + 1)
        self.add_component(self.navigator)
        
        url = self.config[PODCASTS][PODCAST_URL]
        if url and len(url) > 0:
            self.current_page = self.podcasts_util.get_podcast_page(url, PAGE_SIZE_PODCASTS)
        else:
            self.current_page = 1

        self.animated_title = True

    def create_podcast_menu_button(self, s, constr, action, scale, font_size):
        """ Create podcast menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images

        :return: genre menu button
        """
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = True
        s.show_label = True
        s.image_location = ICON_LOCATION
        s.label_location = CENTER
        s.label_area_percent = 30
        s.image_size_percent = ICON_SIZE
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        s.scale = scale
        s.source = None
        s.v_align = V_ALIGN_TOP
        s.h_align = H_ALIGN_LEFT
        s.v_offset = (constr.h/100) * 5
        s.bgr = self.config[BACKGROUND][MENU_BGR_COLOR]
        s.image_area_percent = ICON_AREA
        s.fixed_height = font_size

        button = PodcastButton(self.util, s)
        button.add_release_listener(action)
        if not getattr(s, "enabled", True):
            button.set_enabled(False)
        elif getattr(s, "icon_base", False) and not getattr(s, "scaled", False):
            button.components[1].content = s.icon_base
        button.scaled = scale
        return button

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
        self.podcasts_menu.set_parent_screen(self)
    
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
        