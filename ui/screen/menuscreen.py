# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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
from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.menu.booknavigator import BookNavigator
from util.keys import SCREEN_RECT, COLOR_DARK_LIGHT, COLOR_CONTRAST, COLORS, \
    GO_LEFT_PAGE, GO_RIGHT_PAGE, KEY_LOADING, LABELS
from util.cache import Cache
from ui.layout.multilinebuttonlayout import MultiLineButtonLayout, LINES
from util.config import COLOR_DARK, COLOR_BRIGHT
from pygame import Rect
from ui.state import State
from ui.screen.screen import Screen

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 16.50
PERCENT_TITLE_FONT = 66.66

MENU_NEW_BOOKS = "books"
MENU_BOOKS_BY_GENRE = "books by genre"
MENU_GENRE = "genre"
MENU_ABC = "abc"
MENU_AUTHORS = "authors"
MENU_AUTHORS_BOOKS = "authors books"
MENU_TRACKS = "tracks"

class MenuScreen(Screen):
    """ Site Menu Screen. Base class for all book menu screens """
    
    def __init__(self, util, listeners, rows, columns, voice_assistant, d=None, turn_page=None):
        """ Initializer
        
        :param util: utility object
        :param listeners: file browser listeners
        :param rows: menu rows
        :param d: dictionary with menu button flags
        :param turn_page: turn page callback
        :param util: utility object
        """
        self.util = util
        self.config = util.config
        self.factory = Factory(util)
        self.bounding_box = self.config[SCREEN_RECT]        
        self.player = None
        self.turn_page = turn_page
        self.cache = Cache(self.util)
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)              
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT, voice_assistant, "menu_screen_screen_title", True, layout.TOP)
        
        color_dark_light = self.config[COLORS][COLOR_DARK_LIGHT]
        self.menu_layout = layout.CENTER
        
        self.menu_button_layout = self.get_menu_button_layout(d)
        self.img_rect = self.menu_button_layout.image_rectangle
        
        listeners[GO_LEFT_PAGE] = self.previous_page
        listeners[GO_RIGHT_PAGE] = self.next_page
         
        self.navigator = BookNavigator(util, layout.BOTTOM, listeners, color_dark_light, d[4])
        Container.add_component(self, None)
        Container.add_component(self, self.navigator)
        
        self.total_pages = 0
        self.current_page = 1
        self.menu = None
        
        self.loading_listeners = []
        self.LOADING = util.config[LABELS][KEY_LOADING]
    
    def get_menu_button_layout(self, d):
        """ Return menu button layout
        
        :param d: dictionary with menu button flags
        
        :return: menu button layout
        """
        s = State()
        s.show_img = True
        s.show_label = True
        button_w = int(self.menu_layout.w / d[1])
        button_h = int(self.menu_layout.h / d[0])
        label_padding = 2
        image_padding = 4
        self.show_author = d[2]
        self.show_genre = d[3]        
        s.bounding_box = Rect(0, 0, button_w, button_h)
        return MultiLineButtonLayout(s, label_padding, image_padding)
        
    def previous_page(self, state):
        """ Handle click on left button 
        
        :param state: button state object
        """
        if self.current_page == 1:
            return
        
        self.current_page -= 1
        if getattr(state, "select_last", False):            
            self.components[1].selected_index = 0
        
        self.menu.current_page = self.current_page
        self.menu.selected_index = 0    
        self.turn_page()        
        
    def next_page(self, state):
        """ Handle click on right button 
        
        :param state: button state object
        """
        if self.total_pages <= 1 or self.total_pages == self.current_page:
            return
        
        self.current_page += 1
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        
        self.menu.current_page = self.current_page
        self.menu.selected_index = 0
        self.turn_page()        
    
    def set_menu(self, menu):
        """ Set menu 
        
        :param menu: menu object
        """
        self.menu = self.components[1] = menu    
    
    def set_title(self, page_num):
        """ Set screen title 
        
        :param page_num: menu page number
        """
        if self.total_pages == 1:
            self.screen_title.set_text(self.title)
            return
            
        if len(str(page_num)) <= len(str(self.total_pages)):
            self.screen_title.set_text(self.title + " (" + str(page_num) + ")")
        
    def reset_title(self):
        """ Reset screen title """
        
        self.screen_title.set_text(self.title + " (" + str(self.current_page) + ")")
        
    def go_to_page(self, page_num):
        """ Handle go to page event 
        
        :param page_num: menu page number
        """
        n = int(page_num)
        if n > self.total_pages:
            n = self.total_pages
        if n == 0:
            n = 1
        self.current_page = n
        self.menu.current_page = self.current_page
        self.turn_page()
        
    def get_image_from_cache(self, url):
        """ Return image from cache
        
        :param url: image url
        
        :return: image
        """
        return self.cache.get_image(url)
    
    def put_image_to_cache(self, url, img):
        """ Put image into cache
        
        :param url: image url
        :param img: image
        """
        self.cache.cache_image(img, url)
    
    def set_button_image(self, b, icon, img_y=None):
        """ Set button image
        
        :param b: button
        :param icon: image
        :param img_y: image Y coordinate
        """
        bb = b.bounding_box
        comps = b.components
        im = comps[1]
        im.content = icon            
        w = im.content.get_size()[0]
        h = im.content.get_size()[1]
        im.content_x = bb.x + (bb.width - w)/2
        
        if img_y == None:
            img_area_height = bb.height - ((bb.height / LINES) * 2)
            img_y = bb.y + (img_area_height - h)/2
        
        im.content_y = img_y
        self.components[1].clean_draw_update() 
    
    def set_loading(self, name):
        """ Show Loading... sign
        
        :name: screen title
        """
        b = self.config[COLORS][COLOR_DARK]
        f = self.config[COLORS][COLOR_BRIGHT]
        fs = int(self.bounding_box.h * 0.07)
        bb = self.menu_layout
        t = self.factory.create_output_text(self.LOADING, bb, b, f, fs)
        t.set_text(self.LOADING)
        self.screen_title.set_text(name)
        self.set_visible(True)        
        self.add_component(t)
        self.clean_draw_update()
        self.notify_loading_listeners()
        
    def reset_loading(self): 
        """ Remove Loading... sign """
                   
        del self.components[-1]
        self.notify_loading_listeners()
        
    def add_loading_listener(self, listener):
        """ Add loading listener
        
        :param listener: event listener
        """
        if listener not in self.loading_listeners:
            self.loading_listeners.append(listener)
            
    def notify_loading_listeners(self):
        """ Notify all loading listeners """
        
        for listener in self.loading_listeners:
            listener(None)
        