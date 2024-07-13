# Copyright 2022-2024 Peppy Player peppy.player@gmail.com
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
import urllib.request
import urllib.parse

from yt_dlp import YoutubeDL
from util.keys import *
from ui.state import State
from util.config import COLORS, COLOR_DARK, FOLDER_PLAYLISTS

FILE_YA_STREAMS = "yastreams.m3u"
MENU_ROWS = 5
MENU_COLUMNS = 1
PAGE_SIZE = MENU_ROWS * MENU_COLUMNS
SEARCH_URL = "https://www.youtube.com/results?search_query="
VIDEO_URL_PREFIX = "https://www.youtube.com/watch?v="

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
        self.search_cache = {}
        self.playlist_updated = False

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
            state = self.get_playlist_item(index, name, line.rstrip())
            items.append(state)
            item_name = None
            index += 1

        self.ya_stream_player_playlist_cache = items
        return items

    def get_playlist_item(self, index, name, id):
        """ Get playlist item

        :param index: item index
        :param name: item name
        :param id: item id/url

        :return: state object representing item
        """
        state = State()
        state.index = index
        state.id = id
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
        return state

    def get_search_item(self, index, id, title, source=None):
        """ Create playlist item

        :param index: index in the playlist
        :param id: number ID
        :param title: stream title

        :return: state object representing a playlist item
        """
        s = State()
        s.index = index
        s.id = id.rstrip()
        s.name = str(index)
        s.l_name = title
        s.comparator_item = title
        s.bgr = self.config[COLORS][COLOR_DARK]
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = False
        s.show_label = True
        s.h_align = H_ALIGN_LEFT
        s.v_align = V_ALIGN_TOP
        s.v_offset = 35
        s.file_name = ""
        s.source = source
        return s

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

    def get_best_audio_stream(self, id):
        """ Go through all formats and find the best quality audio stream

        :param id: video ID

        :return: state object with stream duration, image and URL
        """
        s = State()
        with YoutubeDL({}) as ydl:
            info = ydl.extract_info(id, download=False)
            if not info:
                return None
            formats = info['formats']
            if not formats:
                return None
            s.duration = info["duration"]
            s.image = info["thumbnail"]
            abr = asr = 0
            for f in formats:
                if f.get("acodec") == "none" or f.get("vcodec") != "none":
                    continue
                if f.get("asr", 0) != 0 and f.get("abr", 0) != 0:
                    if (f.get("asr", 0) > asr and f.get("abr", 0) > abr) or (f.get("asr", 0) == asr and f.get("abr", 0) > abr):
                        s.url = f.get("url", None)
                        asr = f.get("asr", 0)
                        abr = f.get("abr", 0)
        return s

    def get_playlist_stream_properties(self, state, bb):
        """ Get YA Stream properties

        :param state: state object
        :param bb: bounding box
        """
        if state == None or state.id == None:
            return

        playlist_state = self.get_stream_by_id(state.id)
        if playlist_state == None or hasattr(playlist_state, "url"):
            return

        a = self.get_best_audio_stream(state.id)
        if not a:
            return

        state.duration = a.duration
        state.url = a.url
        img = self.image_util.get_thumbnail(a.image, 1.0, 1.0, bb)
        state.image_path = img[0]
        state.full_screen_image = img[1]

        playlist_state.url = state.url
        playlist_state.duration = state.duration
        playlist_state.image_path = state.image_path
        playlist_state.full_screen_image = state.full_screen_image

    def get_search_stream_properties(self, state, bb):
        """ Get YA Stream properties

        :param state: state object
        :param bb: bounding box
        """
        if state == None or state.id == None:
            return

        if state == None or hasattr(state, "url"):
            return

        a = self.get_best_audio_stream(state.id)
        if not a:
            return

        state.duration = a.duration
        state.url = a.url
        img = self.image_util.get_thumbnail(a.image, 1.0, 1.0, bb)
        if img:
            state.image_path = img[0]
            state.full_screen_image = img[1]

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

    def search(self, query):
        """ Search YouTube by query

        :param query: query string

        :return: playlist with search results
        """
        if not query:
            return []

        if query != None and self.search_cache.get(query, None) != None:
            return self.search_cache[query]

        search_query = urllib.parse.quote(query)
        url = SEARCH_URL + search_query
        query_low = query.lower()
        query_tokens = set(query_low.split())

        try:
            html = urllib.request.urlopen(url)
        except Exception as e:
            logging.debug(e)
            return []

        content = html.read().decode()
        start_token = "\"title\":{\"runs\":[{\"text\":\""
        start_token_len = len(start_token)
        start_index = content.find(start_token, 0)
        stop_token = "\"}]"
        stop_token_len = len(stop_token)
        video_token = "watch?v="
        video_token_len = len(video_token)
        index = 0
        playlist = []

        while start_index != -1:
            start = start_index + start_token_len
            stop_index = content.find(stop_token, start)
            title = content[start: stop_index]
            title_low = title.lower()
            title_tokens = set(title_low.split())
            video_index = content.find(video_token, stop_index + stop_token_len)

            if video_index == -1:
                break

            start_video_index = video_index + video_token_len
            stop_video_index = start_video_index + 11
            video_id = VIDEO_URL_PREFIX + content[start_video_index : stop_video_index]

            if query_tokens.issubset(title_tokens) or title_tokens.issubset(query_tokens):
                video_id = VIDEO_URL_PREFIX + content[start_video_index : stop_video_index]
                item = self.get_search_item(index, video_id, title, "search")
                item.search = query
                playlist.append(item)
                index += 1

            start_index = content.find(start_token, stop_video_index)

        self.search_cache[query] = playlist

        return playlist

    def handle_playlist_item(self, name, id):
        """ Add/delete item to/from the playlist

        :param name: item name
        :param id: item id/url
        """
        playlist = self.get_ya_stream_playlist()
        item = self.get_stream_by_id(id)

        if item != None: # delete
            del playlist[item.index]
            for i, s in enumerate(playlist):
                s.index = i
        else: # add
            index = len(playlist)
            s = self.get_playlist_item(index, name, id)
            playlist.append(s)

        self.playlist_updated = True

    def save_playlist(self):
        """ Save YA Stream playlist """

        playlist_file_content = ""
        playlist = self.get_ya_stream_playlist()

        if playlist:
            for i in playlist:
                playlist_file_content += f"#{i.l_name}\n{i.id}\n\n"

        self.save_yastreams(playlist_file_content)
