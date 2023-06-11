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

import sounddevice
import logging
import json

from queue import Queue
from voiceassistant.baseassistant import BaseAssistant
from vosk import KaldiRecognizer
from voiceassistant.voskassistant.voskutil import VoskUtil
from vosk import SetLogLevel
SetLogLevel(-1)

DEFAULT_LANGUAGE = "en-us"

class VoskAssistant(BaseAssistant):
    """ Vosk Assistant """
    
    def __init__(self, util, language_code, commands, command_executor):
        """ Initializer
        
        :param util: utility object which contains configuration
        :param language_code: language code
        :param commands: language specific voice commands
        :param command_executor: callback function for commands
        """
        BaseAssistant.__init__(self, language_code, commands)
        self.util = util
        self.config = util.config
        self.command_executor = command_executor
        device_info = sounddevice.query_devices(None, "input")
        self.samplerate = int(device_info["default_samplerate"])
        self.recognizer = None
        self.vosk_util = VoskUtil(util)
        self.initialized_successfully = self.change_language(language_code, commands)

    def callback(self, indata, frames, time, status):
        """ This is called (from a separate thread) for each audio block """

        try:
            self.stream_queue.put(bytes(indata))
        except:
            pass

    def get_input_stream(self):
        """ Get input stream
        
        :return: input stream
        """
        return sounddevice.RawInputStream(
            samplerate=self.samplerate,
            blocksize = 12000,
            dtype="int16", 
            channels=1,
            callback=self.callback
        )

    def start(self):
        """ Start assistant thread """

        if not self.initialized_successfully:
            return

        self.stream_queue = Queue()
        self.input_stream = self.get_input_stream()
        self.input_stream.start()
        BaseAssistant.start(self)

    def stop(self):
        """ Stop assistant thread """

        if not self.initialized_successfully:
            return

        BaseAssistant.stop(self)
        self.input_stream.stop()
        self.input_stream.close()
        self.recognizer = None

    def change_language(self, language, commands):
        """ Change assistant language
        
        :param language: language code
        :param commands: language specific commands
        """
        model = self.vosk_util.get_model(language)
        
        if not model:
            logging.debug(f"Model for language '{language}' not found")
            return False

        self.commands = commands 
        
        try:
            self.recognizer = KaldiRecognizer(model, self.samplerate)
        except Exception as e:
            logging.debug(e)
            return False
        
        return True

    def assist(self):
        """ Main thread function """

        if self.recognizer == None:
            return
        data = self.stream_queue.get()
        try:
            if self.recognizer.AcceptWaveform(data):
                r = self.recognizer.Result()
                if r:
                    js = json.loads(r)
                    command = js["text"]
                    if command.startswith("the "):
                        command = command[4:]
                    if command and command.strip() and command != "huh":
                        self.notify_text_listeners(command)
                        self.command_executor(command)
        except Exception as e:
            logging.debug(e)
