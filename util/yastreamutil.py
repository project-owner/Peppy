# Copyright 2022-2023 Peppy Player peppy.player@gmail.com
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
import codecs
import logging
import pafy

from util.keys import *
from ui.state import State
from util.config import COLORS, COLOR_DARK, FOLDER_PLAYLISTS

FILE_YA_STREAMS = "yastreams.m3u"
MENU_ROWS = 5
MENU_COLUMNS = 1
PAGE_SIZE = MENU_ROWS * MENU_COLUMNS

class YaStreamUtil(object):
    """ YA Stream Utility class """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """
        self.util = util
        self.config = util.config
        self.image_util = util.image_util
        self.ya_stream_player_playlist_cache = []
        
    def get_ya_stream_playlist(self):
        """ Get YA Stream playlist

        :return: the playlist
        """
        if len(self.ya_stream_player_playlist_cache) != 0:
            return self.ya_stream_player_playlist_cache

        items = []
        lines = []
        item_name = None
        index = 0

        folder = os.path.join(os.getcwd(), FOLDER_PLAYLISTS)
        path = os.path.join(folder, FILE_YA_STREAMS)

        for encoding in ["utf8", "utf-8-sig", "utf-16"]:
            try:
                lines = codecs.open(path, "r", encoding).read().split("\n")
                break
            except Exception as e:
                logging.error(e)           
        
        for line in lines:
            if len(line.rstrip()) == 0: 
                continue
            
            if line.startswith("#") and not item_name:
                item_name = line[1:].rstrip()
                continue

            if item_name == None:
                continue

            name = item_name.rstrip()
            state = State()
            state.index = index
            state.id = line.rstrip()
            state.name = str(index)
            state.l_name = name
            state.comparator_item = name
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = False
            state.show_label = True
            state.h_align = H_ALIGN_LEFT
            state.v_align = V_ALIGN_TOP
            state.v_offset = 35
            state.file_name = ""
            items.append(state)
            item_name = None
            index += 1

        self.ya_stream_player_playlist_cache = items
        return items

    def get_index_by_id(self, id):
        """ Get item index by its URL

        :param id: item ID

        :return: item index
        """
        index = 0
        if not id:
            return index

        playlist = self.get_ya_stream_playlist()
        
        for i, stream in enumerate(playlist):
            if stream.id == id:
                index = i
                break
        return index

    def get_stream_by_id(self, id):
        """ Get stream object by ID
        
        :param id: straem ID

        :return: stream object from playlist
        """
        stream = None
        if not id:
            return stream

        playlist = self.get_ya_stream_playlist()
        
        for s in playlist:
            if s.id == id:
                stream = s
                break

        return stream    

    def get_stream_properties(self, state, bb):
        """ Get YA Stream properties

        :param state: state object
        :param bb: bounding box
        """
        if state == None or state.id == None:
            return

        playlist_state = self.get_stream_by_id(state.id)
        if playlist_state == None or hasattr(playlist_state, "url"):
            return

        v = pafy.new(state.id)

        if v == None:
            return

        state.duration = v.duration
        
        a = v.getbestaudio()

        if a == None:
            return

        state.url = a.url
        thumbnail_url = None

        if v.bigthumbhd:
            thumbnail_url = v.bigthumbhd
        elif v.bigthumb:
            thumbnail_url = v.bigthumb
        elif v.thumb:
            thumbnail_url = v.thumb

        img = self.image_util.get_thumbnail(thumbnail_url, 1.0, 1.0, bb)
        state.image_path = img[0]
        state.full_screen_image = img[1]

        playlist_state.url = state.url
        playlist_state.duration = state.duration
        playlist_state.image_path = state.image_path
        playlist_state.full_screen_image = state.full_screen_image

    def get_yastreams_string(self):
        """ Read file

        :return: string
        """
        path = os.path.join(os.getcwd(), FOLDER_PLAYLISTS, FILE_YA_STREAMS)
        for encoding in ["utf8", "utf-8-sig", "utf-16"]:
            try:
                with codecs.open(path, 'r', encoding) as file:
                    return file.read()
            except Exception as e:
                logging.error(e)

    def save_yastreams(self, yastreams):
        """ Save YA Streams playlist file

        :param yastreams: file with YA Streams links
        """
        path = os.path.join(os.getcwd(), FOLDER_PLAYLISTS, FILE_YA_STREAMS)
        with codecs.open(path, 'w', UTF8) as file:
            file.write(yastreams)
