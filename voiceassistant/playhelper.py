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

import os
import logging
import requests

from util.config import CURRENT, MODE, AUDIO_FILES, FILE_PLAYBACK, CURRENT_FOLDER, MUSIC_FOLDER, PLAYER_SETTINGS, \
    VOLUME, LANGUAGE, COLLECTION, BASE_FOLDER
from util.selector import Selector

TRANSLATE_TO_LANGUAGE = "en"
ZERO = "zero"
TEN = "ten"
TWENTY = "twenty"
THIRTY = "thirty"
FORTY = "forty"
FIFTY = "fifty"
SIXTY = "sixty"
SEVENTY = "seventy"
EIGHTY = "eighty"
NINETY = "ninety"
HUNDRED = "hundred"

class PlayHelper(object):
    """ Functions for playing stations, files etc """
    
    def __init__(self, util, base_url_api, translate_names=False):
        """ Initializer
        
        :param util: utility object which contains configuration
        :param base_url_api: base API URL
        :param translate_names: defines if names should be translated or not
        """
        self.util = util
        self.config = util.config
        self.BASE_URL_API = base_url_api
        dbutil = util.get_db_util()
        self.translate_names = translate_names
        self.selector = Selector(dbutil)
        self.NUMBER_MAPPING = {
            ZERO: 0,
            TEN: 10,
            TWENTY: 20,
            THIRTY: 30,
            FORTY: 40,
            FIFTY: 50,
            SIXTY: 60,
            SEVENTY: 70,
            EIGHTY: 80,
            NINETY: 90,
            HUNDRED: 100
        }

    def get_numbers(self, commands):
        n = {}
        n[ZERO] = commands[ZERO]
        n[TEN] = commands[TEN]
        n[TWENTY] = commands[TWENTY]
        n[THIRTY] = commands[THIRTY]
        n[FORTY] = commands[FORTY]
        n[FIFTY] = commands[FIFTY]
        n[SIXTY] = commands[SIXTY]
        n[SEVENTY] = commands[SEVENTY]
        n[EIGHTY] = commands[EIGHTY]
        n[NINETY] = commands[NINETY]
        n[HUNDRED] = commands[HUNDRED]
        return n

    def volume(self, command, prefix, voice_commands):
        """ Volume command
        
        :param command: voice command to adjust volume
        :param prefix: command prefix
        :param voice_commands: all voice commands
        """
        logging.debug(f"Received volume command '{command}'")
        suffix = command[len(prefix):].strip()
        numbers = self.get_numbers(voice_commands)
        current_volume = int(self.config[PLAYER_SETTINGS][VOLUME])

        if command == voice_commands["volume_up"]:
            v = current_volume + 20
            if v > 100:
                v = 100
            p = {"volume": v}
            requests.put(self.BASE_URL_API + "volume", json=p)
        elif command == voice_commands["volume_down"]:
            v = current_volume - 20
            if v < 0:
                v = 0
            p = {"volume": v}
            requests.put(self.BASE_URL_API + "volume", json=p)
        elif suffix in list(numbers.values()):
            n = -1
            for k, v in numbers.items():
                if v == suffix:
                    n = self.NUMBER_MAPPING[k]
            if n != -1:
                p = {"volume": n}
                requests.put(self.BASE_URL_API + "volume", json=p)

    def play_file(self, command, prefix):
        """ Play file

        :param command: voice command to play file. It contains filename
        :param prefix: play command prefix
        """
        logging.debug(f"Received play file command '{command}'")
        
        if self.util.file_util.current_folder:
            folder = self.util.file_util.current_folder
        else:
            folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER]
            if not folder:
                folder = self.config[MUSIC_FOLDER]
                self.config[FILE_PLAYBACK][CURRENT_FOLDER] = folder

        audio_files = self.util.get_audio_files_in_folder(folder)
        if not audio_files:
            logging.debug(f"No files found in folder '{folder}'")
            return

        received_command = command[len(prefix):].strip()
        if not received_command:
            logging.debug("No filename found in command")
            return

        translated_name = self.translate_name(received_command).lower()
        received_tokens = set(translated_name.split())
        first_match = None

        for f in audio_files:
            if f.file_type != "file":
                continue
            matching_tokens = 0
            for t in received_tokens:
                filename = f.file_name.lower()
                if t in filename:
                    matching_tokens += 1
            if matching_tokens >= len(received_tokens):
                first_match = f
                break

        if not first_match:
            logging.debug("No matched filename found")
            return

        logging.debug(f"Playing the first matched file '{first_match.file_name}'")

        mode = self.config[CURRENT][MODE]
        if mode != AUDIO_FILES:
            logging.debug(f"Switching to the file player mode")
            p = {"mode": "audio-files"}
            requests.put(self.BASE_URL_API + "mode", json=p)

        p = {
            "folder": first_match.folder, 
            "file": first_match.file_name
        }
        requests.put(self.BASE_URL_API + "fileplayer", json=p)

    def play_station(self, command, prefix):
        """ Play radio station

        :param command: voice command to play station. It contains station name
        :param prefix: play command prefix
        """
        logging.debug(f"Received play station command '{command}'")
        received_command = command[len(prefix):].strip()

        if not received_command:
            logging.debug("No station name found in command")
            return

        received_tokens = set(received_command.lower().split())
        genres = list(self.util.get_genres().values())
        first_match = None

        for g in genres:
            playlist = self.util.get_radio_playlist(self.util.radio_browser_playlist_cache, g.l_name)
            for s in playlist:
                matching_tokens = 0
                for t in received_tokens:
                    station = s.l_name.lower()
                    if t in station:
                        matching_tokens += 1
                if matching_tokens >= len(received_tokens):
                    first_match = s
                    break
            if first_match:
                break

        if not first_match:
            logging.debug("No matched station found")
            return

        logging.debug(f"Playing the first matched station '{first_match.l_name}'")
        p = {
            "genre": first_match.genre, 
            "index": first_match.index,
            "url": first_match.url
        }
        requests.put(self.BASE_URL_API + "radioplayer", json=p)

    def topic(self, command, prefix):
        """ Radio topic/genre command
        
        :param command: voice command for topic
        :param prefix: command prefix
        """
        logging.debug(f"Received topic/genre command '{command}'")
        suffix = command[len(prefix):].strip()

        if suffix.capitalize() not in list(self.util.get_genres().keys()):
            logging.debug(f"Radio genre '{suffix}' was not found")
            return

        p = {"genre": suffix.capitalize()}
        requests.put(self.BASE_URL_API + "genre", json=p)

    def play_disc(self, command, prefix):
        """ Play collection disc
        
        :param command: voice command to play disc. It contains disk name
        :param prefix: play command prefix
        """
        logging.debug(f"Received play disc command '{command}'")
        received_name = command[len(prefix):].strip()

        if not received_name:
            logging.debug("No disc name found in command")
            return

        translated_name = self.translate_name(received_name)
        found = self.selector.get_page_by_pattern("album", translated_name)

        if not found:
            logging.debug(f"No disc name '{translated_name}' found in collection")
            return

        album_name = found[0]
        disc_details = self.selector.get_page_by_column("album", album_name, 1)
        if not disc_details:
            logging.debug(f"No path found in collection for name {album_name}")
            return

        path = self.config[COLLECTION][BASE_FOLDER] + disc_details[0]
        logging.debug(f"Playing disc on path '{path}'")
        p = {
            "path": path
        }
        requests.post(self.BASE_URL_API + "collection/play/disc", json=p)

    def play_song(self, command, prefix):
        """ Play song from collection
        
        :param command: voice command to play song. It contains song name
        :param prefix: play command prefix
        """
        logging.debug(f"Received play song command '{command}'")
        received_name = command[len(prefix):].strip()

        if not received_name:
            logging.debug("No song name found in command")
            return

        translated_name = self.translate_name(received_name)
        found = self.selector.get_page_by_pattern("title", translated_name)

        if not found:
            logging.debug(f"No song name '{translated_name}' found in collection")
            return

        title = found[0]
        song_details = self.selector.get_page_by_column("title", title, 1)
        if not song_details:
            logging.debug(f"No path found in collection for name '{title}'")
            return

        folder = song_details[0]
        file_name = self.selector.get_filename_by_title(folder, title)
        url = os.path.join(self.config[COLLECTION][BASE_FOLDER], folder, file_name)

        p = {
            "file_name": file_name,
            "folder": folder,
            "topic": "title",
            "url": url
        }
        logging.debug(f"Playing song '{url}'")
        requests.post(self.BASE_URL_API + "collection/play/song", json=p)

    def translate_name(self, recieved_name):
        """ Translate name to English
        
        :param recieved_name: received name

        :return: translated name
        """
        translated_name = recieved_name

        if not self.translate_names:
            return recieved_name

        current_language = self.config[CURRENT][LANGUAGE]
        language_code = self.util.get_voice_assistant_language_code(current_language)

        if language_code.startswith(TRANSLATE_TO_LANGUAGE):
            return recieved_name

        translated_name = self.util.translate(recieved_name, language_code, TRANSLATE_TO_LANGUAGE)
        logging.debug(f"Translated '{recieved_name}' to '{translated_name}'")

        return translated_name
