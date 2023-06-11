# Copyright 2016-2023 Peppy Player peppy.player@gmail.com
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
import json
import logging
import requests

from util.config import CURRENT, LANGUAGE, WEB_SERVER, HTTP_PORT, HOME_MENU, RADIO, AUDIO_FILES, COLLECTION, PODCASTS, AUDIOBOOKS, \
    STREAM, CD_PLAYER, AIRPLAY, SPOTIFY_CONNECT, BLUETOOTH_SINK, YA_STREAM, JUKEBOX
from voiceassistant.playhelper import PlayHelper
from voiceassistant.voiceassistantutil import VoiceAssistantUtil, VOICE_ASSISTANT_TYPE, VOICE_ASSISTANT_TRANSLATE_NAMES

PLAY_FILE_PREFIX = "play_file"
PLAY_STATION_PREFIX = "play_station"
PLAYSTATION_PREFIX = "playstation"
PLAY_DISC_PREFIX = "play_disc"
PLAY_SONG_PREFIX = "play_song"
VOLUME_PREFIX = "volume"
VOLUME_COMMANDS = ["volume_up", "volume_down"]
TOPIC_PREFIX = "topic"

COMMAND_PLAY_RADIO = "play_radio"
COMMAND_FILES = "files"
COMMAND_PLAY_FILES = "play_files"
COMMAND_BOOKS = "books"
COMMAND_PLAY_BOOKS = "play_books"
COMMAND_PLAY_STREAM = "play_stream"
COMMAND_PLAY_CD = "play_cd"
COMMAND_PLAY_PODCAST = "play_podcast"
COMMAND_BLUE_TOOTH = "blue_tooth"
COMMAND_YOUTUBE_AUDIO = "youtube_audio"
COMMAND_JUKE_BOX = "juke_box"
COMMAND_PLAY_JUKEBOX = "play_jukebox"

class VoiceAssistant(object):
    """ Voice Assistant """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object which contains configuration
        """
        self.util = util
        self.config = util.config
        voice_assistant_util = VoiceAssistantUtil()
        self.voiceassistant_config = voice_assistant_util.load_config()

        self.type = self.voiceassistant_config[VOICE_ASSISTANT_TYPE]
        self.assistant = None
        self.text_recognized_listeners = []
        
        self.RADIO_ENABLED = self.config[HOME_MENU][RADIO]
        self.AUDIO_FILES_ENABLED = self.config[HOME_MENU][AUDIO_FILES]
        self.AUDIOBOOKS_ENABLED = self.config[HOME_MENU][AUDIOBOOKS]
        self.STREAM_ENABLED = self.config[HOME_MENU][STREAM]
        self.CD_PLAYER_ENABLED = self.config[HOME_MENU][CD_PLAYER]
        self.PODCASTS_ENABLED = self.config[HOME_MENU][PODCASTS]
        self.AIRPLAY_ENABLED = self.config[HOME_MENU][AIRPLAY]
        self.SPOTIFY_ENABLED = self.config[HOME_MENU][SPOTIFY_CONNECT]
        self.COLLECTION_ENABLED = self.config[HOME_MENU][COLLECTION]
        self.BLUETOOTH_SINK_ENABLED = self.config[HOME_MENU][BLUETOOTH_SINK]
        self.YA_STREAM_ENABLED = self.config[HOME_MENU][YA_STREAM]
        self.JUKEBOX_ENABLED = self.config[HOME_MENU][JUKEBOX]

        self.mappings, self.rest_commands = self.load_rest_commands()
        self.voice_commands = self.util.get_voice_commands()
        self.voice_commands_values = self.voice_commands.values()

        self.BASE_URL = "http://localhost:" + self.config[WEB_SERVER][HTTP_PORT] + "/" 
        self.BASE_URL_API = self.BASE_URL + "api/"
        self.init_voice_assistant()

        translate_names = False
        if self.voiceassistant_config[VOICE_ASSISTANT_TRANSLATE_NAMES] and self.util.connected_to_internet:
            translate_names = True

        self.play_helper = PlayHelper(util, self.BASE_URL_API, translate_names)

    def load_rest_commands(self):
        """ Load commands from JSON file
        
        :return: the tulip with mappings and commands
        """
        voice_commands = None
        path = os.path.join(os.getcwd(), "voiceassistant", "restcommands.json")

        with open(path) as f:
            voice_commands = json.load(f)

        mappings = voice_commands["mappings"]
        commands = voice_commands["commands"]
        
        try:
            if not self.RADIO_ENABLED:
                del mappings[RADIO], mappings[COMMAND_PLAY_RADIO]
            if not self.AUDIO_FILES_ENABLED:
                del mappings[AUDIO_FILES], mappings[COMMAND_FILES], mappings[COMMAND_PLAY_FILES]
            if not self.AUDIOBOOKS_ENABLED:
                del mappings[AUDIOBOOKS], mappings[COMMAND_BOOKS], mappings[COMMAND_PLAY_BOOKS]
            if not self.STREAM_ENABLED:
                del mappings[STREAM], mappings[COMMAND_PLAY_STREAM]
            if not self.CD_PLAYER_ENABLED:
                del mappings[CD_PLAYER], mappings[COMMAND_PLAY_CD]
            if not self.PODCASTS_ENABLED:
                del mappings[PODCASTS], mappings[COMMAND_PLAY_PODCAST]
            if not self.AIRPLAY_ENABLED:
                del mappings[AIRPLAY]
            if not self.SPOTIFY_ENABLED:
                del mappings[SPOTIFY_CONNECT]
            if not self.COLLECTION_ENABLED:
                del mappings[COLLECTION]
            if not self.BLUETOOTH_SINK_ENABLED:
                del mappings[BLUETOOTH_SINK], mappings[COMMAND_BLUE_TOOTH]
            if not self.YA_STREAM_ENABLED:
                del mappings[YA_STREAM], mappings[COMMAND_YOUTUBE_AUDIO]
            if not self.JUKEBOX_ENABLED:
                del mappings[JUKEBOX], mappings[COMMAND_JUKE_BOX], mappings[COMMAND_PLAY_JUKEBOX]
        except:
            pass

        return (mappings, commands)
    
    def init_voice_assistant(self):
        """ Stop voice assistant if it's running and create new instance """
        
        if self.assistant and self.is_running():
            self.stop()
        
        language = self.util.get_voice_assistant_language_code(self.config[CURRENT][LANGUAGE])
        
        if self.type == "Vosk Assistant":
            from voiceassistant.voskassistant.voskassistant import VoskAssistant
            self.assistant = VoskAssistant(self.util, language, self.voice_commands, self.execute_command)
            self.assistant.add_text_listener(self.handle_text)
        else:
            logging.debug(f"Not supported voice assistant type {self.type}")
    
    def change_language(self):
        """ Change voice assistant language """

        language = self.util.get_voice_assistant_language_code(self.config[CURRENT][LANGUAGE])
        self.voice_commands = self.util.get_voice_commands()

        try:
            if not self.RADIO_ENABLED:
                del self.voice_commands[RADIO], self.voice_commands[COMMAND_PLAY_RADIO]
            if not self.AUDIO_FILES_ENABLED:
                del self.voice_commands[AUDIO_FILES], self.voice_commands[COMMAND_FILES], self.voice_commands[COMMAND_PLAY_FILES]
            if not self.AUDIOBOOKS_ENABLED:
                del self.voice_commands[AUDIOBOOKS], self.voice_commands[COMMAND_BOOKS], self.voice_commands[COMMAND_PLAY_BOOKS]
            if not self.STREAM_ENABLED:
                del self.voice_commands[STREAM], self.voice_commands[COMMAND_PLAY_STREAM]
            if not self.CD_PLAYER_ENABLED:
                del self.voice_commands[CD_PLAYER], self.voice_commands[COMMAND_PLAY_CD]
            if not self.PODCASTS_ENABLED:
                del self.voice_commands[PODCASTS], self.voice_commands[COMMAND_PLAY_PODCAST]
            if not self.AIRPLAY_ENABLED:
                del self.voice_commands[AIRPLAY]
            if not self.SPOTIFY_ENABLED:
                del self.voice_commands[SPOTIFY_CONNECT]
            if not self.COLLECTION_ENABLED:
                del self.voice_commands[COLLECTION]
            if not self.BLUETOOTH_SINK_ENABLED:
                del self.voice_commands[BLUETOOTH_SINK], self.voice_commands[COMMAND_BLUE_TOOTH]
            if not self.YA_STREAM_ENABLED:
                del self.voice_commands[YA_STREAM], self.voice_commands[COMMAND_YOUTUBE_AUDIO]
            if not self.JUKEBOX_ENABLED:
                del self.voice_commands[JUKEBOX], self.voice_commands[COMMAND_JUKE_BOX], self.voice_commands[COMMAND_PLAY_JUKEBOX]
        except:
            pass

        self.voice_commands_values = self.voice_commands.values()

        was_running = self.is_running()
        if was_running:
            self.stop()
        self.assistant.change_language(language, self.voice_commands)
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
        self.notify_text_recognized_listeners(t)
    
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

    def handle_play_command(self, voice_command):
        """ Command dispatcher
        
        :param voice_command: voice command

        :return: True - command was handled, False - not handled
        """
        handled = True

        if self.AUDIO_FILES_ENABLED and voice_command.startswith(self.voice_commands[PLAY_FILE_PREFIX]):
            self.play_helper.play_file(voice_command, self.voice_commands[PLAY_FILE_PREFIX])
        elif self.RADIO_ENABLED and voice_command.startswith(self.voice_commands[PLAY_STATION_PREFIX]):
            self.play_helper.play_station(voice_command, self.voice_commands[PLAY_STATION_PREFIX])
        elif self.RADIO_ENABLED and voice_command.startswith(self.voice_commands[PLAYSTATION_PREFIX]):
            self.play_helper.play_station(voice_command, self.voice_commands[PLAYSTATION_PREFIX])
        elif self.COLLECTION_ENABLED and voice_command.startswith(self.voice_commands[PLAY_DISC_PREFIX]):
            self.play_helper.play_disc(voice_command, self.voice_commands[PLAY_DISC_PREFIX])
        elif self.COLLECTION_ENABLED and voice_command.startswith(self.voice_commands[PLAY_SONG_PREFIX]):
            self.play_helper.play_song(voice_command, self.voice_commands[PLAY_SONG_PREFIX])
        else:
            handled = False

        return handled

    def execute_command(self, voice_command):
        """ Execute voice command
        
        :param voice_command: voice command to execute
        """
        command = None
        for k, v in self.voice_commands.items():
            if v == voice_command:
                command = k
                break

        if (command == None and voice_command.startswith(self.voice_commands[VOLUME_PREFIX])) or command in VOLUME_COMMANDS:
            self.play_helper.volume(voice_command, self.voice_commands[VOLUME_PREFIX], self.voice_commands)
            return

        if voice_command not in self.voice_commands_values and self.handle_play_command(voice_command):
            return

        if command == None and voice_command.startswith(self.voice_commands[TOPIC_PREFIX]):
            self.play_helper.topic(voice_command, self.voice_commands[TOPIC_PREFIX])
            return

        if not command in self.mappings:
            logging.debug(f"Command '{command}' was not found in mappings. Voice command '{voice_command}'")
            return
        else:
            logging.debug(f"Recognized command '{command}'")
            c = self.mappings[command]
            rest_command = self.rest_commands[c]

            if isinstance(rest_command, dict):
                self.call_rest_api(rest_command)
            else:
                for c in rest_command:
                    self.call_rest_api(c)

    def call_rest_api(self, rest_command):
        """ Call REST API
        
        :param rest_command: rest command dictionary
        """
        t = rest_command["type"]
        r = rest_command["route"]
        p = {}
        try:
            p = rest_command["payload"]
        except:
            pass

        if r.startswith("command/"):
            url = self.BASE_URL + r
        else:
            url = self.BASE_URL_API + r

        if t == "put":
            requests.put(url, json=p)
        elif t == "post":
            requests.post(url, json=p)
