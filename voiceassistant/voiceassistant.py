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

import logging
import pygame

from util.util import NUMBERS
from util.config import VOICE_ASSISTANT, VOICE_ASSISTANT_TYPE, VOICE_ASSISTANT_CREDENTIALS, \
    VOICE_DEVICE_MODEL_ID, VOICE_DEVICE_ID, PLAYER_SETTINGS, MUTE, PAUSE, CURRENT, LANGUAGE
from util.keys import KEY_SUB_TYPE, SUB_TYPE_KEYBOARD, KEY_ACTION, KEY_KEYBOARD_KEY, \
    USER_EVENT_TYPE, VOICE_EVENT_TYPE, KEY_VOICE_COMMAND
from voiceassistant.voicekeyboardmap import VOICE_KEYBOARD_MAP
from sounddevice import PortAudioError

class VoiceAssistant(object):
    """ Voice Assistant. Currently supports only menu navigation. """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object which contains configuration
        """
        self.util = util
        self.config = util.config
        self.type = self.config[VOICE_ASSISTANT][VOICE_ASSISTANT_TYPE]
        self.credentials = self.config[VOICE_ASSISTANT][VOICE_ASSISTANT_CREDENTIALS]
        can_use_voice_assistant = True
        self.assistant = None
        self.text_recognized_listeners = []   
        self.init_voice_assistant() 
                    
    def init_voice_assistant(self):
        """ Stop voice assistant if it's running and create new instance """
        
        if self.assistant and self.is_running():
            self.stop()
        
        self.commands = self.util.get_voice_commands()
        language = self.util.get_voice_assistant_language_code(self.config[CURRENT][LANGUAGE])
        if self.type == "Google Assistant":
            try:
                from voiceassistant.googleassistant.googleassistant import GoogleAssistant
                from voiceassistant.googleassistant.conversationstream import ConversationStream
                from voiceassistant.googleassistant.sounddevicestream import SoundDeviceStream
                import google_auth_oauthlib
                import google.rpc
                import google.assistant.embedded.v1alpha2
                
                device_model_id = self.config[VOICE_ASSISTANT][VOICE_DEVICE_MODEL_ID]
                device_id = self.config[VOICE_ASSISTANT][VOICE_DEVICE_ID]
                self.assistant = GoogleAssistant(self.credentials, language, self.util.voice_commands, device_model_id, device_id)
            except PortAudioError as e1:
                logging.debug("Cannot use microphone")
                raise e1
            except Exception as e2:
                logging.debug("Cannot use voice assistant: " + str(e2))
                raise e2
        
        if self.assistant:      
            self.assistant.add_text_listener(self.handle_text)
    
    def change_language(self):
        language = self.util.get_voice_assistant_language_code(self.config[CURRENT][LANGUAGE])
        self.commands = self.util.get_voice_commands()
        was_running = self.is_running()
        if was_running:
            self.stop()
        self.assistant.change_language(language, self.util.voice_commands)
        if was_running:
            self.start()
        
    def is_running(self):
        """ Check if assistant is running
        
        :return: True - assistant is running, False - assistant is not running
        """
        return self.assistant.is_running()
    
    def start(self):
        """ Start voice assistant """
        
        self.assistant.start()
        
    def stop(self):
        """ Stop voice assistant """
        
        self.assistant.stop()
    
    def handle_text(self, text):
        """ Handle recognized text event
        
        :param text: recognized text
        """
        t = text.lower().strip()
        logging.debug(t)
        
        self.notify_text_recognized_listeners(t)
        
        if text.startswith(self.commands["VA_GO_TO_PAGE"].strip()):
            self.generate_go_to_page_events(t, self.commands["VA_GO_TO_PAGE"].strip())
        elif text.startswith(self.commands["VA_PAGE_NUMBER"].strip()):
            self.generate_go_to_page_events(t, self.commands["VA_PAGE_NUMBER"].strip())
        elif self.get_number(text) != None:
            self.generate_number_events(n)
        elif text == self.commands["VA_STOP"].strip():
            self.stop()
        else:
            self.generate_string_events(t)
    
    def generate_number_events(self, n):
        """ Generate keyboard number event
        
        :param n: recognized number
        """
        voice_key = None
        logging.debug("number: " + n)
        
        for s in n:
            for k, v in self.commands.items():
                if s == v.strip():
                    voice_key = k.strip()
                    break
            self.create_keyboard_events(voice_key)
        self.create_keyboard_events("VA_OK")
    
    def generate_go_to_page_events(self, text, command):
        """ Generate go to page event
        
        :param text: recognized text
        :param command: command text
        """
        start = len(command) + 1
        s = text[start:].strip()
        n = self.get_number(s)
        self.generate_number_events(n)
    
    def generate_string_events(self, t):
        """ Generate string event. Used mostly for menu navigation
        
        :param t: recognized text
        """
        voice_key = None
        
        for k, v in self.commands.items():
            try:
                if t == v.strip():
                    voice_key = k.strip()
                    break
            except:
                pass
        
        if voice_key and voice_key in VOICE_KEYBOARD_MAP.keys():
            self.create_keyboard_events(voice_key)
        else:
            self.create_menu_event(t)
            
    def create_keyboard_events(self, voice_key):
        """ Create keyboard events (key pressed/key released)
        
        :param voice_key: voice key
        """
        d = {}
        d[KEY_SUB_TYPE] = SUB_TYPE_KEYBOARD
        d[KEY_ACTION] = pygame.KEYDOWN
        d[KEY_KEYBOARD_KEY] = VOICE_KEYBOARD_MAP[voice_key]
        event = pygame.event.Event(USER_EVENT_TYPE, **d)
        pygame.event.post(event)
        d[KEY_ACTION] = pygame.KEYUP
        event = pygame.event.Event(USER_EVENT_TYPE, **d)
        pygame.event.post(event)

    def create_menu_event(self, text):
        """ Create event which should be handled by menu
        
        :param text: recognized text
        """
        d = {}
        d[KEY_VOICE_COMMAND] = text
        event = pygame.event.Event(VOICE_EVENT_TYPE, **d)
        pygame.event.post(event)
    
    def get_number(self, text):
        """ Return string number
        
        :param text: recognized text
        :return: number
        """
        if not text: return
        
        if text == self.commands["VA_ONE"]:
            return "1"
        elif text == self.commands["VA_TWO"]:
            return "2"
        elif text == self.commands["VA_THREE"]:
            return "3"
        elif text == self.commands["VA_FOUR"]:
            return "4"
        elif text == self.commands["VA_FIVE"]:
            return "5"
        elif text == self.commands["VA_SIX"]:
            return "6"
        elif text == self.commands["VA_SEVEN"]:
            return "7"
        elif text == self.commands["VA_EIGHT"]:
            return "8"
        elif text == self.commands["VA_NINE"]:
            return "9"
        
        tokens = text.split(" ")
        
        for t in tokens:
            if not t.isdigit(): 
                if t in NUMBERS.keys():
                    t = str(NUMBERS[t])
                if not t.isdigit(): return None
        
        result = ""
        
        for t in tokens:
            result += t

        return result
    
    def add_text_recognized_listener(self, listener):
        """ Add text recognized listener
        
        :param listener: event listener
        """
        if listener not in self.text_recognized_listeners:
            self.text_recognized_listeners.append(listener)
            
    def notify_text_recognized_listeners(self, text):
        """ Notify all text recognized listeners
        
        :param text: text recognized
        """
        for listener in self.text_recognized_listeners:
            listener(text)   
                     
