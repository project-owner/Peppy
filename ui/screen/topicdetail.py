# Copyright 2020 Peppy Player peppy.player@gmail.com
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
from ui.menu.menu import ALIGN_LEFT
from util.config import LABELS, CURRENT, MODE, COLLECTION, BASE_FOLDER
from util.collector import ALBUM, FILENAME, FOLDER, TITLE
from ui.menu.multipagemenu import MultiPageMenu
from util.keys import KEY_HOME, KEY_KEYBOARD_KEY, KEY_CALLBACK, KEY_PLAY_COLLECTION, KEY_SOURCE, \
    KEY_NAVIGATOR, KEY_BACK, KEY_FILE, KEY_AUDIO_FOLDER
from util.selector import Selector
from ui.state import State
from ui.menu.topicdetailnavigator import TopicDetailNavigator

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

ROWS = 5
COLUMNS = 1
PAGE_SIZE = ROWS * COLUMNS

class TopicDetailScreen(MenuScreen):
    """ Topic Detail Screen """

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
        self.go_home = listeners[KEY_HOME]
        self.go_file_playback = listeners[KEY_PLAY_COLLECTION]

        dbutil = util.get_db_util()
        self.selector = Selector(dbutil)

        self.bounding_box = util.screen_rect
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)

        MenuScreen.__init__(self, util, listeners, ROWS, COLUMNS, voice_assistant, [ROWS, COLUMNS],
                            self.turn_page, page_in_title=False, show_loading=False)        

        m = self.factory.create_collection_menu_button
        self.collection_list_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title,
                                       self.go_to_page, m, ROWS, COLUMNS, None,
                                       (0, 0, 0), self.menu_layout, align=ALIGN_LEFT)
        self.set_menu(self.collection_list_menu)

        self.navigator = TopicDetailNavigator(self.util, self.layout.BOTTOM, listeners)
        self.components.append(self.navigator)
        self.current_item = None
        self.current_page_items = None
        self.first_item = None
        self.last_item = None
        self.collection_topic = None
        self.selection = None
        self.prev_page = 1
        self.animated_title = True

    def set_current(self, state):
        """ Set current state

        :param state: button state
        """
        source = getattr(state, KEY_SOURCE, None)

        if source == KEY_NAVIGATOR or source == KEY_BACK:
            return

        if hasattr(state, "collection_topic"):
            self.collection_topic = getattr(state, "collection_topic", "")

        if self.current_item and self.current_item[0] == getattr(state, "name", None):
            return

        if hasattr(state, "name"):
            self.selection = getattr(state, "name", "")

        self.title = self.config[LABELS][self.collection_topic] + ": " + self.selection
        self.set_title(1)

        self.current_page = 1
        self.prev_page = 1
        self.navigator.left_button.change_label("0")
        self.navigator.right_button.change_label("0")

        self.set_loading(self.title)

        topic = self.get_topic()
        
        self.total_pages = self.selector.get_page_count_by_column(topic, self.selection, PAGE_SIZE)

        if self.total_pages == 0:
            self.reset_loading()
            return
        
        self.filename = None
        self.title = None

        if self.collection_topic == KEY_FILE:
            self.filename = state.name
        elif self.collection_topic == TITLE:
            self.title = state.name

        self.turn_page()
        self.reset_loading()

    def turn_page(self):
        """ Turn page """

        topic = self.get_topic()

        self.current_page_items = self.selector.get_topic_detail_page(topic, self.selection, 
            self.current_page, self.prev_page, self.first_item, self.last_item, PAGE_SIZE)
        self.prev_page = self.current_page
    
        if not self.current_page_items:
            self.current_page_items = []
            return

        self.current_item = self.current_page_items[0]
        self.first_item = self.current_item
        self.last_item = self.current_page_items[len(self.current_page_items) - 1]

        p = {}
        for i, f in enumerate(self.current_page_items):
            s = State()
            s.index = i
            s.folder = f
            if "\x00" in f:
                f = f.replace("\x00", "")
            if "/" in f:
                parts = f.split("/")
                if len(parts) > 1:
                    last = parts[len(parts) - 1]
                    if len(last) > 6:
                        f = last
                    else:
                        f = parts[len(parts) - 2] + "/" + last
            s.name = f            
            s.l_name = s.name
            if self.filename:
                s.file_name = self.filename
            if self.title:
                s.title = self.title
            p[str(i)] = s

        self.collection_list_menu.set_items(p, 0, self.select_item, False)

        keys = list(p.keys())

        if len(keys) != 0 and self.navigator and self.total_pages > 1:
            self.navigator.left_button.change_label(str(self.current_page - 1))
            self.navigator.right_button.change_label(str(self.total_pages - self.current_page))

        self.collection_list_menu.clean_draw_update()

        if hasattr(self, "update_observer"):
            self.collection_list_menu.add_menu_observers(self.update_observer, self.redraw_observer)

        self.collection_list_menu.unselect()
        for i, b in enumerate(self.collection_list_menu.buttons.values()):
            if self.current_item[0] == b.state.name:
                self.collection_list_menu.select_by_index(b.state.index)
                return
        index = (self.current_page - 1) * PAGE_SIZE
        self.collection_list_menu.select_by_index(index)

    def get_topic(self):
        """ Get topic

        :return: proper topic name
        """
        topic = self.collection_topic
        if topic == KEY_AUDIO_FOLDER:
            topic = FOLDER
        elif topic == KEY_FILE:
            topic = FILENAME

        return topic

    def select_item(self, s=None):
        """ Select item from menu

        :param state: button state
        """
        self.current_item = s.name                
        state = State()
        state.folder = os.path.join(self.config[COLLECTION][BASE_FOLDER], s.folder[1:])
        state.topic = self.collection_topic
        
        if state.topic == KEY_FILE:
            state.file_name = s.file_name
        elif state.topic == TITLE:
            state.file_name = self.selector.get_filename_by_title(s.folder, self.title)
            state.url = os.path.join(state.folder, state.file_name)
        else:
            files = self.util.get_audio_files_in_folder(state.folder, False)
            if files:
                f = files[0]
                state.file_name = f.file_name
                state.url = os.path.join(state.folder, state.file_name)
            else:
                state.file_name = None
                state.url = None

        state.source = "detail"
        self.collection_list_menu.select_by_index(s.index)
        self.go_file_playback(state)

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
