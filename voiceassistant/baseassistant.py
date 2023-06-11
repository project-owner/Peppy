# Copyright 2023 Peppy Player peppy.player@gmail.com
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
import time

from threading import Thread
from ui.state import State
from util.keys import USER_EVENT_TYPE

class BaseAssistant(object):
    """ Parent class for all assistants """
    
    def __init__(self, language_code, commands):
        """ Initializer
        
        :param language_code: language code e.g. en-US
        :param commands: dictionary of commands for the language
        """
        self.language_code = language_code
        self.commands = commands
        self.text_listeners = []
        self.start_conversation_listeners = []
        self.stop_conversation_listeners = []
        self.run_assistant = False
    
    def is_running(self):
        """ Check if assistant is running
        
        :return: True - assistant is running, False - assistant is not running
        """
        return self.run_assistant
        
    def start(self):
        """ Start assistant thread """
        
        if self.run_assistant:
            return
        
        self.run_assistant = True
        t = Thread(target = self.start_assistant_thread)
        t.start()
        
    def start_assistant_thread(self):
        """ Implementation of the assistant thread """
        
        logging.debug("Start voice assistant thread")
        while self.run_assistant:
            self.notify_start_conversation_listeners()
            try:
                self.assist()
            except:
                pass
        logging.debug("Stopped voice assistant")
        
    def stop(self):
        """ Stop assistant thread """
        
        if not self.run_assistant:
            return
                
        logging.debug("Stopping voice assistant thread...")
        self.notify_stop_conversation_listeners()
        self.run_assistant = False
        time.sleep(3)            
            
    def assist(self):
        """ Send a voice request to the Assistant """
        
        pass

    def add_text_listener(self, listener):
        """ Add recognized text listener
        
        :param listener: text listener
        """
        if listener not in self.text_listeners:
            self.text_listeners.append(listener)
            
    def notify_text_listeners(self, text):
        """ Notify recognized text listeners
        
        :param text: recognized text
        """
        for listener in self.text_listeners:
            listener(text)
            
    def add_start_conversation_listener(self, listener):
        """ Add start conversation listener
        
        :param listener: text listener
        """
        if listener not in self.start_conversation_listeners:
            self.start_conversation_listeners.append(listener)
            
    def notify_start_conversation_listeners(self):
        """ Notify start conversation listeners """

        if not self.run_assistant:
            return

        for listener in self.start_conversation_listeners:
            s = State()
            s.type = USER_EVENT_TYPE
            listener(s)
            
    def add_stop_conversation_listener(self, listener):
        """ Add stop conversation listener
        
        :param listener: text listener
        """
        if listener not in self.stop_conversation_listeners:
            self.stop_conversation_listeners.append(listener)
            
    def notify_stop_conversation_listeners(self):
        """ Notify stop conversation listeners """
        
        for listener in self.stop_conversation_listeners:
            listener()
