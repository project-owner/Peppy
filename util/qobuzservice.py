# Copyright 2024 Peppy Player peppy.player@gmail.com
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

import math
import logging

from minim.qobuz import PrivateAPI
from operator import itemgetter
from util.streamingservice import *
from ui.state import State

QOBUZ_TYPE_ARTIST = "MainArtist"
QOBUZ_TYPE_ALBUM = "Album"
QOBUZ_TYPE_TRACK = "ReleaseName"

QOBUZ_ARTIST_ID = "id"
QOBUZ_ARTIST_NAME = "name"
QOBUZ_ARTIST_IMAGE = "picture"
QOBUZ_ARTIST_ALBUMS = "albums_count"

QOBUZ_ALBUM_ID = "id"
QOBUZ_ALBUM_TITLE = "title"
QOBUZ_ALBUM_URL = "url"
QOBUZ_ALBUM_DATE = "release_date_original"
QOBUZ_ALBUM_IMAGE = "image"
QOBUZ_ALBUM_TRACKS = "tracks_count"
QOBUZ_ALBUM_GENRE = "genre"
QOBUZ_ALBUM_ARTIST_ID = "artist_id"
QOBUZ_ALBUM_ARTIST_NAME = "name"

QOBUZ_TRACK_ID = "id"
QOBUZ_TRACK_TITLE = "title"
QOBUZ_TRACK_DURATION = "duration"
QOBUZ_TRACK_POSITION = "track_number"
QOBUZ_TRACK_DATE = "release_date_original"
QOBUZ_TRACK_ARTIST_ID = "id"
QOBUZ_TRACK_ARTIST_NAME = "name"

LIMIT=50
OFFSET=0

class QobuzService(StreamingService):
    """ Qobuz service """

    def __init__(self):
        """ Initializer """

        self.api = PrivateAPI()
        self.new_releases_cache = []
        self.best_sellers_cache = []
        self.album_tracks_cache = {}

    def get_artist(self, artist_dict):
        """ Create artist dictionary

        :param artist_dict: qobuz specific dictionary

        :return: artist dictionary
        """
        a = {}
        a[ARTIST_ID] = artist_dict.get(QOBUZ_ARTIST_ID, None)
        a[ARTIST_NAME] = artist_dict.get(QOBUZ_ARTIST_NAME, None)
        a[ARTIST_IMAGE] = artist_dict.get(QOBUZ_ARTIST_IMAGE, None)
        a[ARTIST_ALBUMS] = artist_dict.get(QOBUZ_ARTIST_ALBUMS, None)
        return a

    def get_album(self, album_dict, index):
        """ Create album object

        :param album_dict: qobuz specific dictionary
        :param index: element index

        :return: album object
        """
        s = State()

        setattr(s, INDEX, index)
        setattr(s, ALBUM_ID, album_dict.get(QOBUZ_ALBUM_ID, None))
        setattr(s, ALBUM_URL, album_dict.get(QOBUZ_ALBUM_URL, None))
        setattr(s, ALBUM_TRACKS, album_dict.get(QOBUZ_ALBUM_TRACKS, None))
        setattr(s, ALBUM_DATE, album_dict.get(QOBUZ_ALBUM_DATE, None))

        if album_dict.get(QOBUZ_ALBUM_GENRE, None) and album_dict[QOBUZ_ALBUM_GENRE].get(NAME, None):
            setattr(s, ALBUM_GENRE, album_dict.get(QOBUZ_ALBUM_GENRE, None))

        if album_dict.get(QOBUZ_ALBUM_IMAGE, None):
            if album_dict[QOBUZ_ALBUM_IMAGE].get(SMALL, None):
                setattr(s, ALBUM_IMAGE_SMALL, album_dict[QOBUZ_ALBUM_IMAGE][SMALL])
            if album_dict[QOBUZ_ALBUM_IMAGE].get(LARGE, None):
                setattr(s, ALBUM_IMAGE_LARGE, album_dict[QOBUZ_ALBUM_IMAGE][LARGE])

        if album_dict.get(ARTIST, None):
            if album_dict[ARTIST].get(QOBUZ_ALBUM_ARTIST_ID, None):
                setattr(s, ALBUM_ARTIST_ID, album_dict[ARTIST][QOBUZ_ALBUM_ARTIST_ID])
            if album_dict[ARTIST].get(QOBUZ_ALBUM_ARTIST_NAME, None):
                setattr(s, ALBUM_ARTIST_NAME, album_dict[ARTIST][QOBUZ_ALBUM_ARTIST_NAME])

        if hasattr(s, ALBUM_ARTIST_NAME):
            title = getattr(s, ALBUM_ARTIST_NAME) + " - " + album_dict.get(QOBUZ_ALBUM_TITLE, None)
        else:
            title = album_dict.get(QOBUZ_ALBUM_TITLE, None)
        setattr(s, ALBUM_TITLE, title)
        setattr(s, NAME, album_dict.get(QOBUZ_ALBUM_TITLE, None))
        setattr(s, LNAME, title)

        return s

    def get_track(self, track_dict, index):
        """ Create track object

        :param track_dict: qobuz specific dictionary

        :return: track object
        """
        s = State()

        setattr(s, INDEX, index)
        setattr(s, TRACK_ID, track_dict.get(QOBUZ_TRACK_ID, None))
        title = track_dict.get(QOBUZ_TRACK_TITLE, None)
        setattr(s, TRACK_TITLE, title)
        setattr(s, TRACK_DURATION, track_dict.get(QOBUZ_TRACK_DURATION, None))
        setattr(s, TRACK_POSITION, track_dict.get(QOBUZ_TRACK_POSITION, None))
        setattr(s, TRACK_DATE, track_dict.get(QOBUZ_TRACK_DATE, None))
        setattr(s, NAME, title)
        setattr(s, LNAME, title)
        setattr(s, PLAYBACK_MODE, CATALOG)

        if track_dict.get(PERFORMER, None):
            if track_dict[PERFORMER].get(QOBUZ_TRACK_ARTIST_ID, None):
                setattr(s, TRACK_ARTIST_ID, track_dict[PERFORMER][QOBUZ_TRACK_ARTIST_ID])
            if track_dict[PERFORMER].get(QOBUZ_TRACK_ARTIST_NAME, None):
                setattr(s, TRACK_ARTIST_NAME, track_dict[PERFORMER][QOBUZ_TRACK_ARTIST_NAME])

        try:
            track_url = self.api.get_track_file_url(track_id=getattr(s, TRACK_ID, None), format_id=5)
            if track_url and track_url.get(URL, None):
                setattr(s, URL, track_url[URL])
        except:
            pass

        return s

    def get_artists_by_name(self, artist_name):
        """ Get list of artists by name

        :param artist_name: artist name

        :return: list of artists
        """
        response = None
        try:
            response = self.api.search(query=artist_name, strict=True, limit=LIMIT)
        except:
            pass

        if not response or response.get(ARTISTS, None) == None or response[ARTISTS].get(ITEMS, None) == None:
            return []

        results = response[ARTISTS][ITEMS]
        artists = []

        for r in results:
            artists.append(self.get_artist(r))

        return artists

    def get_albums_by_artist_name(self, artist_name):
        """ Get albums by artist name

        :param artist_name: artist name

        :return: list of albums
        """
        response = None
        try:
            response = self.api.search(query=artist_name, strict=True, limit=LIMIT)
        except:
            pass

        if not response or response.get(ALBUMS, None) == None or response[ALBUMS].get(ITEMS, None) == None:
            return []

        results = response[ALBUMS][ITEMS]
        albums = []
        for r in results:
            if r[ARTIST] and r[ARTIST][NAME] and r[ARTIST][NAME].lower() != artist_name.lower():
                continue
            albums.append(self.get_album(r))

        sorted_albums = sorted(albums, key=itemgetter(ALBUM_DATE), reverse=False)

        return sorted_albums

    def get_albums_by_artist_id(self, artist_id):
        """ Get albums by artist ID

        :param artist_id: artist ID

        :return: list of albums
        """
        response = None
        try:
            response = self.api.get_artist(artist_id=artist_id, extras=ALBUMS, limit=LIMIT)
        except:
            pass

        if not response or not response[ALBUMS] or not response[ALBUMS][ITEMS]:
            return []

        results = response[ALBUMS][ITEMS]
        albums = []
        for r in results:
            albums.append(self.get_album(r))

        sorted_albums = sorted(albums, key=itemgetter(ALBUM_DATE), reverse=False)

        return sorted_albums

    def get_albums_by_title(self, album_title):
        """ Get albums by album title

        :param album_title: album title

        :return: list of albums
        """
        response = None
        try:
            response = self.api.search(query=album_title, strict=True, limit=LIMIT)
        except:
            pass

        if not response or response.get(ALBUMS, None) == None or response[ALBUMS].get(ITEMS, None) == None:
            return []

        results = response[ALBUMS][ITEMS]
        albums = []
        for r in results:
            if not self.is_strict_match(album_title, r[QOBUZ_ALBUM_TITLE]):
                continue
            albums.append(self.get_album(r))

        sorted_albums = sorted(albums, key=itemgetter(ALBUM_DATE), reverse=False)

        return sorted_albums

    def get_tracks_by_album_id(self, album_id):
        """ Get tracks by album ID

        :param album_id: album ID

        :return: list of tracks
        """

        if album_id and self.album_tracks_cache and self.album_tracks_cache.get(album_id, None):
            return self.album_tracks_cache[album_id]

        response = None
        try:
            response = self.api.get_album(album_id)
        except:
            pass

        if not response or not response[TRACKS] or not response[TRACKS][ITEMS]:
            return []

        results = response[TRACKS][ITEMS]
        tracks = []
        for i, r in enumerate(results):
            t = self.get_track(r, i)
            if getattr(t, URL, None):
                tracks.append(t)

        self.album_tracks_cache[album_id] = tracks

        return tracks

    def get_tracks_by_title(self, track_title):
        """ Get list of tracks by track title

        :param track_title: track title

        :return: list of tracks
        """
        response = None
        try:
            response = self.api.search(query=track_title, strict=True, limit=LIMIT)
        except:
            pass

        if not response or not response[TRACKS] or not response[TRACKS][ITEMS]:
            return []

        results = response[TRACKS][ITEMS]
        tracks = []
        for r in results:
            if not self.is_strict_match(track_title, r[QOBUZ_TRACK_TITLE]):
                continue
            tracks.append(self.get_track(r))

        return tracks

    def get_new_releases(self, page, page_size):
        """ Get list of newly released albums

        :param page: page number
        :param page_size: page size

        :return: list of albums
        """
        return self.get_featured_albums("new-releases", self.new_releases_cache, page, page_size)

    def get_bestsellers(self, page, page_size):
        """ Get list of the best selled albums

        :param page: page number
        :param page_size: page size

        :return: list of albums
        """
        return self.get_featured_albums("best-sellers", self.best_sellers_cache, page, page_size)

    def get_featured_albums(self, type, cache, page, page_size):
        """ Get list of the featured albums

        :param type: featured albums type
        :param page: cache
        :param page: page number
        :param page_size: page size

        :return: list of albums
        """
        if cache and page < len(cache):
            return cache[page]

        if page > len(cache):
            return []

        pages = int((len(cache) * page_size) / LIMIT)
        offset = pages * LIMIT
        response = None

        try:
            response = self.api.get_featured_albums(type=type, limit=LIMIT, offset=offset)
        except Exception as e:
            logging.debug(e)

        if not response or response.get(ALBUMS, None) == None or response[ALBUMS].get(ITEMS, None) == None:
            return {}
        total = math.ceil(response[ALBUMS][TOTAL] / page_size)
        results = response[ALBUMS][ITEMS]
        albums = []
        for i, r in enumerate(results):
            albums.append(self.get_album(r, i))

        for i in range(0, len(albums), page_size):
            p = albums[i : i + page_size]
            cache.append(p)
        if cache and page < len(cache):
            return (total, cache[page])
        else:
            return []
