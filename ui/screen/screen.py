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
from ui.factory import Factory
from ui.layout.borderlayout import BorderLayout
from util.util import LABELS
from util.config import SCREEN_RECT, COLORS, COLOR_DARK_LIGHT, COLOR_CONTRAST, USAGE, USE_VOICE_ASSISTANT, \
    KEY_VA_START, KEY_VA_STOP, KEY_WAITING_FOR_COMMAND, KEY_VA_COMMAND
from tornado.test.log_test import LoggingOptionTest

PERCENT_TOP_HEIGHT = 14.00
PERCENT_TITLE_FONT = 54.00

class Screen(Container):
    """ Base class for all screens. Extends Container class """
    
    def __init__(self, util, title_key, percent_bottom_height=0, voice_assistant=None, screen_title_name="screen_title", create_dynamic_title=False, title_layout=None):
        """ Initializer
        
        :param util: utility object
        :param title_key: the resource bundle key for the screen title
        """
        Container.__init__(self, util)
        self.util = util
        factory = Factory(util)
        self.config = util.config
        self.bounding_box = self.config[SCREEN_RECT]
        self.bgr = (0, 0, 0)
        self.layout = BorderLayout(self.config[SCREEN_RECT])
        self.layout.set_percent_constraints(PERCENT_TOP_HEIGHT, percent_bottom_height, 0, 0)
        self.voice_assistant = voice_assistant

        font_size = (self.layout.TOP.h * PERCENT_TITLE_FONT)/100.0
        d = self.config[COLORS][COLOR_DARK_LIGHT]
        c = self.config[COLORS][COLOR_CONTRAST]
        
        t_layout = self.layout.TOP
        if title_layout:
            t_layout = title_layout
        
        if create_dynamic_title:
            self.screen_title = factory.create_dynamic_text(screen_title_name, t_layout, d, c, int(font_size))
        else:
            self.screen_title = factory.create_output_text(screen_title_name, t_layout, d, c, int(font_size))
            
        if title_key and len(title_key) > 0:
            label = self.config[LABELS][title_key]
            self.screen_title.set_text(label) 
        
        if voice_assistant:
            self.screen_title.add_select_listener(self.handle_voice_assistant)
            self.layout.TOP.w += 1
            self.voice_command = factory.create_output_text("voice_command", self.layout.TOP, d, c, int(font_size))
            self.voice_command.add_select_listener(self.handle_voice_assistant)
            self.voice_assistant.add_text_recognized_listener(self.text_recognized)
            self.voice_assistant.assistant.add_start_conversation_listener(self.start_conversation)
            self.voice_assistant.assistant.add_stop_conversation_listener(self.stop_conversation)
        
        if voice_assistant and voice_assistant.is_running():
            self.title_selected = False
        else:
            self.title_selected = True
            
        self.draw_title_bar()        
        self.player_screen = False
        self.update_web_observer = None
        self.update_web_title = None
    
    def draw_title_bar(self):
        if len(self.components) != 0 and self.title_selected:
            self.components[0] = self.voice_command
            self.title_selected = False
        elif len(self.components) != 0 and not self.title_selected:
            self.components[0] = self.screen_title
            self.title_selected = True
        elif len(self.components) == 0 and self.title_selected:
            self.components.append(self.screen_title)
        elif len(self.components) == 0 and not self.title_selected:
            self.voice_command.set_text(self.config[LABELS][KEY_WAITING_FOR_COMMAND])
            self.components.append(self.voice_command)
            
    def handle_voice_assistant(self, state=None):
        if self.title_selected:
            self.voice_assistant.start()
        else:
            self.voice_assistant.stop()
    
    def text_recognized(self, text):
        c = self.config[LABELS][KEY_VA_COMMAND] + " " + text
        self.voice_command.set_text(c)
        self.voice_command.clean_draw_update()
        if self.update_web_title:
            self.update_web_title(self.voice_command)
        
    def start_conversation(self, event):
        if self.visible: 
            self.voice_command.set_visible(True)
        self.voice_command.set_text_no_draw(self.config[LABELS][KEY_WAITING_FOR_COMMAND])
        self.components[0] = self.voice_command
        self.title_selected = False
        if self.visible:
            self.voice_command.clean_draw_update()
            if self.update_web_observer:
                self.update_web_observer()
    
    def stop_conversation(self):
        if self.visible: 
            self.screen_title.set_visible(True)
        self.components[0] = self.screen_title
        self.title_selected = True
        if self.visible:
            self.screen_title.clean_draw_update()
            if self.update_web_observer:
                self.update_web_observer()
    
    def add_menu(self, menu):
        """ Add menu to the screen
        
        :param menu: the menu to add
        """
        self.menu = menu
        self.add_component(menu)
    
    def enable_player_screen(self, flag):
        """ Enable player screen
        
        :param flag: enable/disable flag
        """
        pass
    
    def exit_screen(self):
        """ Complete actions required to save screen state """
        
        self.set_visible(False)
    
    def add_screen_observers(self, update_observer, redraw_observer, title_to_json=None):
        """ Add screen observers.
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        self.update_web_observer = redraw_observer
        self.update_web_title = title_to_json
