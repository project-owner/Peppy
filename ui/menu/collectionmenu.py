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

import logging

from ui.factory import Factory
from ui.menu.menu import Menu
from util.keys import V_ALIGN_TOP, KEY_AUDIO_FOLDER, KEY_FILE
from util.config import USAGE, USE_VOICE_ASSISTANT, NAME, COLLECTION, COLLECTION_MENU, SHOW_NUMBERS, \
    COLLECTION_PLAYBACK, COLLECTION_TOPIC
from util.collector import GENRE, ARTIST, ALBUM, TITLE, DATE, TYPE, COMPOSER, FOLDER, FILENAME, ORIGINOS, BASEFOLDER

class CollectionMenu(Menu):
    """ Collection Menu class """

    def __init__(self, util, bgr=None, bounding_box=None, font_size=None):
        """ Initializer

        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        :param font_size: labels font size
        """
        self.util = util
        self.factory = Factory(util)
        self.config = util.config
        dbutil = util.get_db_util()
        self.stats = dbutil.get_collection_summary()
        suffix = []
        items = []
        item_list = [GENRE, ARTIST, COMPOSER, ALBUM, TITLE, DATE, FOLDER, FILENAME, TYPE]
        if self.config[USAGE][USE_VOICE_ASSISTANT]:
            command_list = ["VA_GENRE", "VA_ARTIST", "VA_COMPOSER", "VA_ALBUM", "VA_TITLE", "VA_DATE", "VA_FOLDER", "VA_FILENAME", "VA_TYPE"]
            va_commands = self.util.get_voice_commands()

        for n, i in enumerate(item_list):
            if self.stats and self.config[COLLECTION][SHOW_NUMBERS]:
                suffix.append(self.stats[i])

            if i == FOLDER and self.config[COLLECTION_MENU][FOLDER]:
                items.append(KEY_AUDIO_FOLDER)
            elif i == FILENAME and self.config[COLLECTION_MENU][FILENAME]:
                items.append(KEY_FILE)
            elif self.config[COLLECTION_MENU][i]:
                items.append(i)
                
            if self.config[USAGE][USE_VOICE_ASSISTANT] and i in items:
                self.add_voice_command(i, command_list[n], va_commands)

        m = self.factory.create_home_menu_button
        Menu.__init__(self, util, bgr, bounding_box, None, None, create_item_method=m, font_size=font_size)
        
        if not items:
            return

        l = self.get_layout(items)
        bounding_box = l.get_next_constraints()
        self.topics = self.util.load_menu(items, NAME, [], V_ALIGN_TOP, bb=bounding_box, scale=0.4, suffix=suffix)
        self.set_items(self.topics, 0, self.change_topic, False)

        topic = self.config[COLLECTION_PLAYBACK][COLLECTION_TOPIC]
        if topic:
            for k in self.topics.keys():
                if k == topic:
                    self.current_topic = self.topics[k]
                    break
        else:
            self.current_topic = self.topics[items[0]]

        self.item_selected(self.current_topic)

    def add_voice_command(self, name, commands, va_commands):
        """ Add voice command

        :param name: item name
        :param commands: item commands
        :param va_commands: voice commands
        """
        c = []
        for m in commands:
            c.append(va_commands[m].strip())
        self.topics[name].voice_commands = c

    def change_topic(self, state):
        """ Change topic event listener

        :param state: button state
        """
        if not self.visible:
            return
        state.previous_mode = self.current_topic.name
        state.source = "menu"
        self.current_topic = state
        self.notify_listeners(state)
