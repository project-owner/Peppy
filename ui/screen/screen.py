# Copyright 2016-2020 Peppy Player peppy.player@gmail.com
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

import time

from pygame import Rect
from ui.container import Container
from ui.factory import Factory
from ui.layout.borderlayout import BorderLayout
from util.keys import KEY_LOADING, LABELS
from util.config import COLORS, COLOR_CONTRAST, USAGE, USE_VOICE_ASSISTANT, COLOR_BRIGHT, VOICE_ASSISTANT, \
    KEY_VA_START, KEY_VA_STOP, KEY_WAITING_FOR_COMMAND, KEY_VA_COMMAND, COLOR_DARK_LIGHT, VOICE_COMMAND_DISPLAY_TIME, \
    BACKGROUND, HEADER_BGR_COLOR, COLOR, BGR_TYPE, BGR_TYPE_IMAGE, GENERATED_IMAGE, MENU_BGR_COLOR

PERCENT_TOP_HEIGHT = 14.00
PERCENT_TITLE_FONT = 54.00

class Screen(Container):
    """ Base class for all screens. Extends Container class """
    
    def __init__(self, util, title_key, percent_bottom_height=0, voice_assistant=None, screen_title_name="screen_title", 
        create_dynamic_title=False, title_layout=None, title=None, bgr=None):
        """ Initializer
        
        :param util: utility object
        :param title_key: the resource bundle key for the screen title
        """
        self.util = util
        self.factory = Factory(util)
        self.config = util.config
        self.bounding_box = util.screen_rect

        if title_key:
            self.name = title_key
        else:
            self.name = "tmp"

        bg = self.util.get_background(self.name, bgr)
        self.bgr_type = bg[0]
        self.bgr = bg[1]
        self.bgr_key = bg[5]
        Container.__init__(self, util, bounding_box=self.bounding_box, background=bg[1], content=bg[2], image_filename=bg[3])
        self.original_image_filename = None
        try:
            self.original_image_filename = bg[4].replace("\\", "/")
        except:
            pass

        self.layout = BorderLayout(util.screen_rect)
        self.layout.set_percent_constraints(PERCENT_TOP_HEIGHT, percent_bottom_height, 0, 0)
        self.voice_assistant = voice_assistant

        self.font_size = int((self.layout.TOP.h * PERCENT_TITLE_FONT)/100.0)
        b = self.config[BACKGROUND][HEADER_BGR_COLOR]
        c = self.config[COLORS][COLOR_CONTRAST]
        
        t_layout = self.layout.TOP
        if title_layout:
            t_layout = title_layout
        
        if create_dynamic_title:
            self.screen_title = self.factory.create_dynamic_text(screen_title_name, t_layout, b, c, self.font_size)
        else:
            self.screen_title = self.factory.create_output_text(screen_title_name, t_layout, b, c, self.font_size)
        
        if title:
            self.screen_title.set_text(title)
        else:    
            if title_key and len(title_key) > 0:
                try:
                    label = self.config[LABELS][title_key]
                    self.screen_title.set_text(label)
                except:
                    pass 
        
        if voice_assistant:
            self.screen_title.add_select_listener(self.handle_voice_assistant)
            self.layout.TOP.w += 1
            self.voice_command = self.factory.create_output_text("voice_command", self.layout.TOP, b, c, self.font_size)
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

        self.loading_listeners = []
        self.LOADING = util.config[LABELS][KEY_LOADING]
        self.animated_title = False
    
    def add_component(self, c):
        """ Add screen component

        :param c: component to add
        """
        if c:
            c.set_parent_screen(self)
        Container.add_component(self, c)

    def draw_title_bar(self):
        """ Draw title bar on top of the screen """
        
        if len(self.components) != 0 and self.title_selected:
            self.add_component(self.voice_command)
            self.title_selected = False
        elif len(self.components) != 0 and not self.title_selected:
            self.add_component(self.screen_title)
            self.title_selected = True
        elif len(self.components) == 0 and self.title_selected:
            self.add_component(self.screen_title)
        elif len(self.components) == 0 and not self.title_selected:
            self.voice_command.set_text(self.config[LABELS][KEY_WAITING_FOR_COMMAND])
            self.add_component(self.voice_command)
            
    def handle_voice_assistant(self, state=None):
        """ Start/Stop voice assistant 
        
        :state: not used
        """
        if self.title_selected:
            self.voice_assistant.start()
        else:
            self.voice_assistant.stop()
    
    def text_recognized(self, text):
        """ Handle text recognized event 
        
        :text: recognized text
        """
        c = self.config[LABELS][KEY_VA_COMMAND] + " " + text
        self.voice_command.set_text(c)
        self.voice_command.clean_draw_update()
        time.sleep(self.config[VOICE_ASSISTANT][VOICE_COMMAND_DISPLAY_TIME])
        if self.update_web_title:
            self.update_web_title(self.voice_command)
        
    def start_conversation(self, event):
        """ Start voice conversation
        
        :event: not used
        """
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
        """ Stop voice conversation """
        
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

    def set_loading(self, name=None, menu_bb=None, text=None):
        """ Show Loading... sign

        :param name: screen title
        :param menu_bb: menu bounding box
        :param text: screen text
        """
        b = self.config[BACKGROUND][MENU_BGR_COLOR]
        f = self.config[COLORS][COLOR_BRIGHT]
        fs = int(self.bounding_box.h * 0.07)

        if menu_bb != None:
            bb = menu_bb
        else:
            bb = self.bounding_box

        bb = Rect(bb.x, bb.y + 1, bb.w, bb.h - 1)

        t = self.factory.create_output_text(self.LOADING, bb, b, f, fs)
        if not text:
            t.set_text_no_draw(self.LOADING)
        else:
            t.set_text_no_draw(text)

        if name != None:
            self.screen_title.set_text(name)

        self.set_visible(True)
        self.add_component(t)
        if getattr(self, "menu", None) != None:
            self.menu.buttons = {}
            self.menu.components = []
        self.clean_draw_update()
        self.notify_loading_listeners()

    def reset_loading(self):
        """ Remove Loading label """

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
