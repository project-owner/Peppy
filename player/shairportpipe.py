# Copyright 2019-2023 Peppy Player peppy.player@gmail.com
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
import base64
import pygame
from io import BytesIO
import binascii
import re
import math

from threading import Thread

UTF8 = "utf-8"
ASCII = "ascii"
ITEM_START = "<item>"
CODE_ARTIST = "asar"
CODE_TRACK_TITLE = "minm"
CODE_METADATA_END = "mden"
CODE_PLAYBACK_END = "pend"
CODE_PLAYBACK_BEGIN = "pbeg"
CODE_PLAYBACK_RESUME = "prsm"
CODE_VOLUME = "pvol"
CODE_PICTURE = "PICT"
VALID_CODES = [
    CODE_METADATA_END,
    CODE_VOLUME,
    CODE_ARTIST,
    CODE_TRACK_TITLE,
    CODE_PICTURE
]
PLAYBACK_CODES = [
    CODE_PLAYBACK_END,
    CODE_PLAYBACK_BEGIN,
    CODE_PLAYBACK_RESUME,
]

METADATA_PIPE = "/tmp/shairport-sync-metadata"

class ShairportPipeConnector(object):
    """ Implements named pipe metadata reader for shairport-sync. """

    def __init__(self, util, notify_player_listeners):
        """ Initializer

        :param util: utility functions
        :param notify_player_listeners: player callback
        """
        self.util = util
        self.image_util = util.image_util
        self.notify_player_listeners = notify_player_listeners
        self.metadata_reader_running = False
        self.enable_volume_callback = True
        self.item_re = r"<item><type>(([A-Fa-f0-9]{2}){4})</type><code>(([A-Fa-f0-9]{2}){4})</code><length>(\d*)</length>"
        self.metadata = {}

    def start_metadata_reader(self):
        """ Start metadata reader """

        self.metadata_reader_running = True
        metadata_thread = Thread(target=self.metadata_reader)
        metadata_thread.start()

    def stop_metadata_reader(self):
        """ Stop metadata reader """

        self.metadata_reader_running = False

    def metadata_reader(self):
        """ Thread method to read shairport-sync metadata from the named pipe """

        metadata = {}
        with open(METADATA_PIPE) as pipe:
            while self.metadata_reader_running:
                line = pipe.readline()
                if not line.startswith(ITEM_START):
                    continue

                matches = re.findall(self.item_re, line)
                item_code = str(binascii.unhexlify(matches[0][2]), ASCII)
                item_length = int(matches[0][4])

                if item_code in PLAYBACK_CODES:
                    self.trigger_playback_event(item_code)
                    continue
                elif item_code not in VALID_CODES:
                    continue

                line = pipe.readline()
                if not line.startswith("<data"):
                    continue

                line = pipe.readline()
                size = 4 * math.ceil((item_length) / 3)
                data = line[:size]

                if item_code != CODE_PICTURE:
                    try:
                        d = base64.b64decode(data)
                        data = d.decode()
                    except Exception as e:
                        logging.debug(e)
                        data = ""

                if item_code == CODE_METADATA_END:
                    self.trigger_metadata_event(metadata)
                    metadata = {}
                elif item_code == CODE_VOLUME:
                    self.trigger_volume_event(data)
                elif item_code == CODE_ARTIST:
                    metadata[CODE_ARTIST] = data
                elif item_code == CODE_TRACK_TITLE:
                    metadata[CODE_TRACK_TITLE] = data
                elif item_code == CODE_PICTURE:
                    self.trigger_picture_event(data)

    def trigger_metadata_event(self, metadata):
        """  Prepare and trigger metadata event

        :param metadata: metadata dictionary
        """
        if not metadata:
            return

        state = {}
        if CODE_ARTIST in metadata.keys() and CODE_TRACK_TITLE in metadata.keys():
            state["current_title"] = metadata[CODE_ARTIST] + \
                " - " + metadata[CODE_TRACK_TITLE]
        elif CODE_ARTIST in metadata.keys() and CODE_TRACK_TITLE not in metadata.keys():
            state["current_title"] = metadata[CODE_ARTIST]
        elif CODE_ARTIST not in metadata.keys() and CODE_TRACK_TITLE in metadata.keys():
            state["current_title"] = metadata[CODE_TRACK_TITLE]
        else:
            state["current_title"] = ""

        self.notify_player_listeners(state)
        metadata = {}

    def trigger_picture_event(self, picture):
        """  Prepare and trigger picture event

        :param picture: picture as a base 64 encoded string
        """
        if picture == None or len(picture) == 0: return

        try:
            self.image_util.image_cache_base64["current_shairport_image"] = picture
            data = base64.b64decode(picture)
            buffer = BytesIO(data)
            state = {}
            state["picture"] = pygame.image.load(buffer).convert_alpha()
            self.notify_player_listeners(state)
        except Exception as e:
            logging.debug(e)

    def trigger_volume_event(self, volume):
        """ Trigger volume event

        :param volume: volume in range -30-0
        """
        if not self.enable_volume_callback:
            self.enable_volume_callback = True
            return

        if not volume:
            return

        tokens = volume.split(",")
        if not tokens or not tokens[0]:
            return

        vol = int(100 - (abs(float(tokens[0])) * (100/30)))
        state = {}
        state["volume"] = vol
        self.notify_player_listeners(state)

    def trigger_playback_event(self, code):
        """ Trigget playback events - play/pause

        :param code: code type
        """
        state = {}
        command = "begin"
        if code == CODE_PLAYBACK_END:
            command = "end"
        state["stream"] = command
        self.notify_player_listeners(state)
