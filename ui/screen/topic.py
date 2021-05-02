# Copyright 2020-2021 Peppy Player peppy.player@gmail.com
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

from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.screen.menuscreen import MenuScreen
from ui.menu.menu import Menu, ALIGN_LEFT
from util.config import LABELS, TOPIC_DETAIL, BASE_FOLDER, COLLECTION, COLLECTION_PLAYBACK, COLLECTION_TOPIC, \
    HORIZONTAL_LAYOUT, BACKGROUND, MENU_BGR_COLOR
from util.keys import KEY_SOURCE, KEY_NAME, KEY_ABC, KEY_SEARCH, KEY_AUDIO_FOLDER, KEY_CALLBACK_VAR, KEY_FILE, KEY_LIST, \
    KEY_NAVIGATOR, KEY_BACK, KEY_MENU
from util.selector import Selector
from ui.state import State
from ui.navigator.topic import TopicNavigator
from util.collector import FOLDER, FILENAME

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625
ROWS = 5
COLUMNS = 2
PAGE_SIZE = ROWS * COLUMNS
FONT_HEIGHT = 34

class TopicScreen(MenuScreen):
    """ Collection Topic Screen """

    def __init__(self, util, listeners, voice_assistant):
        """ Initializer

        :param util: utility object
        :param listeners: listeners
        :param voice_assistant: voice assistant
        """
        self.util = util
        self.config = util.config
        self.listeners = listeners
        self.listeners[KEY_LIST] = self.set_list
        self.factory = Factory(util)
        dbutil = util.get_db_util()
        self.selector = Selector(dbutil)

        self.bounding_box = util.screen_rect
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)

        MenuScreen.__init__(self, util, listeners, ROWS, COLUMNS, voice_assistant, [ROWS, COLUMNS],
                            self.turn_page, page_in_title=False, show_loading=False)        

        m = self.factory.create_collection_menu_button
        font_size = int(((self.menu_layout.h / ROWS) / 100) * FONT_HEIGHT)

        h = self.config[HORIZONTAL_LAYOUT]
        bgr = self.config[BACKGROUND][MENU_BGR_COLOR]
        self.topic_menu = Menu(util, bgr, self.menu_layout, ROWS, COLUMNS, create_item_method=m, align=ALIGN_LEFT, horizontal_layout=h, font_size=font_size)
        self.set_menu(self.topic_menu)

        self.navigator = TopicNavigator(self.util, self.layout.BOTTOM, listeners)
        self.add_navigator(self.navigator)

        self.current_topic = None
        self.current_item = None
        self.current_page_items = None
        self.first_item = None
        self.last_item = None
        self.collection_topic = None
        self.previous_page = 1
        self.search_string = None
        self.source = None
        self.mode = KEY_LIST
        self.animated_title = True

    def set_current(self, state):
        """ Set current state

        :param state: button state
        """
        self.source = getattr(state, KEY_SOURCE, None)
        if self.source:
            if self.source == KEY_ABC:
                self.mode = KEY_ABC
            elif self.source == KEY_SEARCH:
                self.mode = KEY_SEARCH
            elif self.source == KEY_LIST:
                self.mode = KEY_LIST

        if self.current_topic and (self.source == KEY_NAVIGATOR or self.source == KEY_BACK or self.source == None):
            return

        if self.source == KEY_MENU:
            self.config[COLLECTION_PLAYBACK][COLLECTION_TOPIC] = state.name
            self.mode = KEY_LIST

        if hasattr(state, "genre"):
            if self.current_topic == state.genre:
                return
            else:
                self.current_topic = state.genre
                self.current_item = None

        name = self.config[COLLECTION_PLAYBACK][COLLECTION_TOPIC]
        if self.source:
            if self.source == KEY_ABC:
                name = getattr(state, KEY_NAME, None)
            elif self.source == KEY_SEARCH:
                name = getattr(state, KEY_CALLBACK_VAR, None)

        if not self.source or not name:
            return

        if self.source != KEY_ABC and self.source != KEY_SEARCH:
            self.collection_topic = name
            self.search_string == None
        else:            
            self.search_string = name

        self.navigator.set_buttons(self.collection_topic)
        self.navigator.left_button.change_label("0")
        self.navigator.right_button.change_label("0")
        self.navigator.set_parent_screen(self)
        self.current_page_items = None
        self.first_item = ""
        self.last_item = ""
        self.current_page = 1
        self.previous_page = 1

        if not self.current_topic:
            return

        self.title = self.get_title(name)
        self.set_title(1) 
        self.set_loading(self.title)
        self.total_pages = self.get_total_pages(name)        
        self.turn_page()
        self.reset_loading()

    def set_list(self, state=None):
        """ Set list view """

        s = State()
        s.source = KEY_LIST
        s.name = self.collection_topic
        self.set_current(s)

    def get_title(self, search_string):
        """ Return title based on call source. The source can be:
        - Collection screen
        - ABC keyboard
        - Keyboard Search screen

        :param search_string: search string from keyboard

        :return: title which depends on call source
        """
        title = None
        try:
            title = self.config[LABELS][self.collection_topic]
        except:
            pass

        if self.source == KEY_ABC:
            title = f"{title}. {search_string.strip()}"
        elif self.source == KEY_SEARCH:
            title = f"{title}. *{search_string.strip()}*"

        return title

    def get_total_pages(self, search_string):
        """ Return the number of total pages for defined search criteria

        :param search_string: search string from keyboard

        :return: total pages number
        """
        mode = self.collection_topic
        if mode == KEY_AUDIO_FOLDER:
            mode = FOLDER
        elif mode == KEY_FILE:
            mode = FILENAME

        total_pages = 0

        if self.source == KEY_ABC:
            total_pages = self.selector.get_page_count_by_char(mode, search_string.strip(), PAGE_SIZE)
        elif self.source == KEY_SEARCH:
            total_pages = self.selector.get_page_count_by_pattern(mode, search_string.strip(), PAGE_SIZE)
        else:
            total_pages = self.selector.get_page_count(mode, PAGE_SIZE)
            
        return total_pages

    def turn_page(self):
        """ Turn page """

        if self.total_pages == 0:
            self.topic_menu.set_items({}, 0, self.select_item, False)
            self.link_borders()
            return

        p = self.prepare_page()
        self.topic_menu.set_items(p, 0, self.select_item, False)
        keys = list(p.keys())

        if len(keys) != 0 and self.navigator and self.total_pages > 1:
            self.navigator.left_button.change_label(str(self.current_page - 1))
            self.navigator.right_button.change_label(str(self.total_pages - self.current_page))

        self.topic_menu.clean_draw_update()

        if hasattr(self, "update_observer"):
            self.topic_menu.add_menu_observers(self.update_observer, self.redraw_observer)

        for b in self.topic_menu.buttons.values():
            b.parent_screen = self

        self.topic_menu.unselect()
        self.link_borders()

        if self.navigator.is_selected():
            return

        for b in self.topic_menu.buttons.values():
            b.parent_screen = self
            if self.current_item == b.state.name:
                self.topic_menu.select_by_index(b.state.index)
                return
        self.navigator.menu_button.set_selected(True)
        self.navigator.menu_button.clean_draw_update()

    def prepare_page(self):
        """ Prepare topic page

        :return: page dictionary
        """
        page, self.first_item, self.last_item = self.get_current_page()
        p = {}
        for i, n in enumerate(page):
            s = State()
            s.index = i
            if "\x00" in n:
                n = n.replace("\x00", "")
            s.name = n
            s.l_name = n
            p[str(i)] = s
        return p

    def get_current_page(self):
        """ Get current page content 
        
        :return: page content
        """
        topic = self.collection_topic
        if topic == KEY_AUDIO_FOLDER:
            topic = FOLDER
        elif topic == KEY_FILE:
            topic = FILENAME

        page_items = self.selector.get_topic_page(self.mode, topic, self.search_string, 
            self.current_page, self.previous_page, self.first_item, self.last_item, PAGE_SIZE)

        self.previous_page = self.current_page
    
        if not page_items:
            page_items = []
            first_item = None
            last_item = None
        else:
            first_item = page_items[0]
            last_item = page_items[len(page_items) - 1]

        return (page_items, first_item, last_item)

    def select_item(self, s=None):
        """ Select item from menu

        :param s: button state
        """
        if not s: return

        self.current_item = s.name
        s.collection_topic = self.collection_topic
        self.topic_menu.selected_index = s.index

        if self.collection_topic == KEY_AUDIO_FOLDER:
            s.folder = os.path.join(self.config[COLLECTION][BASE_FOLDER], s.name[1:])
            s.source = KEY_MENU
            files = self.util.get_audio_files_in_folder(s.folder, False)
            if files:
                f = files[0]
                s.file_name = f.file_name
                s.url = os.path.join(s.folder, s.file_name)
            else:
                s.file_name = None
                s.url = None
        
        self.listeners[TOPIC_DETAIL](s)

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers

        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        MenuScreen.add_screen_observers(self, update_observer, redraw_observer)
        self.update_observer = update_observer
        self.redraw_observer = redraw_observer
        self.add_loading_listener(redraw_observer)
        self.topic_menu.add_menu_observers(update_observer, redraw_observer)
        self.navigator.add_observers(update_observer, redraw_observer)
