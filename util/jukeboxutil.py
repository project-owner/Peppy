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
import codecs
import logging

from util.keys import *
from ui.state import State
from util.config import *
from util.fileutil import FILE_AUDIO

JUKEBOX_PLAYLIST = "jukebox.m3u"

class JukeboxUtil(object):
    """ Jukebox Utility class """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """
        self.util = util
        self.config = util.config
        self.image_util = util.image_util
        self.thumbnail_cache = {}
        self.jukebox_playlist_cache = []
        
    def get_jukebox_playlist(self):
        """ Get Jukebox playlist

        :return: the playlist
        """
        if len(self.jukebox_playlist_cache) != 0:
            return self.jukebox_playlist_cache

        items = []
        lines = []
        title = None
        index = 0

        folder = os.path.join(os.getcwd(), FOLDER_PLAYLISTS)
        path = os.path.join(folder, JUKEBOX_PLAYLIST)

        for encoding in ["utf8", "utf-8-sig", "utf-16"]:
            try:
                lines = codecs.open(path, "r", encoding).read().split("\n")
                break
            except Exception as e:
                logging.error(e)
        
        for line in lines:
            if len(line.rstrip()) == 0: 
                continue
            
            if line.startswith("#") and not title:
                title = line[1:].rstrip()
                continue

            if title == None:
                title = line

            name = title.rstrip()

            if line.lower().startswith("http"):
                state = self.get_stream_playlist_item(index, line, name)
            else:
                state = self.get_file_playlist_item(index, line, name)
            
            items.append(state)
            title = None
            index += 1

        self.jukebox_playlist_cache = items
        return items

    def is_online_playlist(self):
        """ Check if the playlist contains HTTP links
        
        :return: True - playlist has HTTP links, False - playlist doesn't have HTTP links
        """
        playlist = self.get_jukebox_playlist()
        if playlist:
            for s in playlist:
                if hasattr(s, "url") and s.url.lower().startswith("http"):
                    return True
            return False
        else:
            return True

    def get_stream_playlist_item(self, index, line, name):
        """ Get stream playlist item
        
        :param index: item index
        :param line: playlist line
        :param name: item name

        :return: state object representing playlist item
        """
        state = State()
        state.index = index
        state.id = line.rstrip()
        state.l_name = name
        state.name = state.l_name
        state.comparator_item = index
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
        state.url = state.id
        state.source = KEY_JUKEBOX_BROWSER
        state.time = "0.0"

        return state

    def get_file_playlist_item(self, index, line, name):
        """ Get file playlist item
        
        :param index: item index
        :param line: playlist line
        :param name: item name

        :return: state object representing playlist item
        """
        state = State()
        state.index = index
        state.playlist_track_number = index
        state.id = line.rstrip()
        state.music_folder = self.config[MUSIC_FOLDER]

        if state.id.startswith(os.sep) or (state.id[1] == ":" and state.id[2] == os.sep):
            state.file_name = state.url = state.id
        else:
            state.file_name = state.url = state.music_folder + state.id
        
        state.file_type = FILE_AUDIO
        if os.sep in state.file_name:
            state.name = state.l_name = state.file_name[state.file_name.rfind(os.sep) + 1 : ]
        else:
            state.name = state.l_name = name
        state.comparator_item = index
        state.h_align = H_ALIGN_LEFT
        state.v_align = V_ALIGN_TOP
        state.v_offset = 35
        state.show_bgr = True
        state.show_img = False
        state.show_label = True
        state.file_type = FILE_AUDIO

        return state

    def get_stream_by_id(self, id):
        """ Get stream object by ID
        
        :param id: straem ID

        :return: stream object from playlist
        """
        stream = None
        if not id:
            return stream

        playlist = self.get_jukebox_playlist()
        
        for s in playlist:
            if s.id == id:
                stream = s
                break

        return stream    

    def get_jukebox_string(self):
        """ Read file

        :return: string
        """
        path = os.path.join(os.getcwd(), FOLDER_PLAYLISTS, JUKEBOX_PLAYLIST)
        for encoding in ["utf8", "utf-8-sig", "utf-16"]:
            try:
                with codecs.open(path, 'r', encoding) as file:
                    return file.read()
            except Exception as e:
                logging.error(e)

    def save_jukebox_playlist(self, playlist):
        """ Save Jukebox playlist file

        :param playlist: Jukebox playlist file
        """
        path = os.path.join(os.getcwd(), FOLDER_PLAYLISTS, JUKEBOX_PLAYLIST)
        with codecs.open(path, 'w', UTF8) as file:
            file.write(playlist)
