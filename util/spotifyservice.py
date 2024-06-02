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

from minim.spotify import WebAPI
from util.streamingservice import *
from ui.state import State

SPOTIFY_TYPE_ARTIST = "artist"
SPOTIFY_TYPE_ALBUM = "album"
SPOTIFY_TYPE_TRACK = "track"
SPOTIFY_URL = "href"
TYPE_TRACK = "track"

SPOTIFY_ARTIST_ID = "id"
SPOTIFY_ARTIST_NAME = "name"
SPOTIFY_ARTIST_GENRES = "genres"
SPOTIFY_ARTIST_IMAGES = "images"
SPOTIFY = "spotify"
SPOTIFY_URLS = "external_urls"

SPOTIFY_ALBUM_ID = "id"
SPOTIFY_ALBUM_TITLE = "name"
SPOTIFY_ALBUM_TRACKS = "total_tracks"
SPOTIFY_ALBUM_DATE = "release_date"

SPOTIFY_TRACK_ID = "id"
SPOTIFY_TRACK_TITLE = "name"
SPOTIFY_TRACK_URL = "href"
SPOTIFY_TRACK_PREVIEW = "preview_url"
SPOTIFY_TRACK_POSITION = "track_number"
SPOTIFY_TRACK_DURATION = "duration_ms"
SPOTIFY_TRACK_ARTIST_ID = "id"
SPOTIFY_TRACK_ARTIST_NAME = "name"

PICTURE = "picture"
ALBUM = "album"
ALBUMS = "albums_count"
IMAGES = "images"
SPOTIFY_ITEMS = "items"
WIDTH = "width"
DEFAULT_WIDTH = 200
URL = "url"
TYPE = "type"
ARTISTS = "artists"
TOTAL = "total"

FILTER_ARTIST = " artist:"
FILTER_ALBUM = " album:"
FILTER_TRACK = " track:"

LIMIT = 50
ITEMS_MAX = 200

class SpotifyService(StreamingService):
    """ Spotify service """

    def __init__(self):
        """ Initializer """

        self.api = WebAPI()

        self.artists_cache = {}
        self.artists_total_pages = {}

        self.artist_albums_cache = {}
        self.albums_cache = {}
        self.albums_total_pages = {}

        self.tracks_cache = {}
        self.tracks_total_pages = {}

    def get_artist(self, artist_dict):
        """ Create artist object
        
        :param artist_dict: spotify specific dictionary

        :return: artist object
        """
        s = State()

        setattr(s, ARTIST_ID, artist_dict.get(SPOTIFY_ARTIST_ID, None))
        name = artist_dict.get(SPOTIFY_ARTIST_NAME, None)
        setattr(s, NAME, name)
        setattr(s, LNAME, name)
        if artist_dict.get(SPOTIFY_URLS, None) and artist_dict[SPOTIFY_URLS].get(SPOTIFY, None):
            setattr(s, ARTIST_URL, artist_dict[SPOTIFY_URLS][SPOTIFY])
        if artist_dict.get(SPOTIFY_ARTIST_IMAGES, None):
            images = artist_dict[SPOTIFY_ARTIST_IMAGES]
            for i in images:
                if i[WIDTH] >= 100 and i[WIDTH] <= 300:
                    setattr(s, ALBUM_IMAGE_SMALL, i[URL])
                elif i[WIDTH] > 300 and i[WIDTH] <= 800:
                    setattr(s, ALBUM_IMAGE_LARGE, i[URL])
        default_image = "artist"
        if getattr(s, ALBUM_IMAGE_SMALL, None) == None:
            setattr(s, ALBUM_IMAGE_SMALL, default_image)
        if getattr(s, ALBUM_IMAGE_LARGE, None) == None:
            setattr(s, ALBUM_IMAGE_LARGE, default_image)

        return s
    
    def get_album(self, album_dict):
        """ Create album object

        :param album_dict: spotify specific dictionary

        :return: album object
        """
        s = State()

        setattr(s, ALBUM_ID, album_dict.get(SPOTIFY_ALBUM_ID, None))
        name = album_dict.get(SPOTIFY_ALBUM_TITLE, None)
        setattr(s, NAME, name)
        setattr(s, LNAME, name)
        setattr(s, ALBUM_URL, album_dict.get(SPOTIFY_URL, None))
        setattr(s, ALBUM_TRACKS, album_dict.get(SPOTIFY_ALBUM_TRACKS, None))
        setattr(s, ALBUM_DATE, album_dict.get(SPOTIFY_ALBUM_DATE, None))

        if album_dict.get(ARTISTS, None):
            artist = album_dict[ARTISTS][0]
            setattr(s, ALBUM_ARTIST_ID, artist[SPOTIFY_ARTIST_ID])
            setattr(s, ALBUM_ARTIST_NAME, artist[SPOTIFY_ARTIST_NAME])

        if album_dict.get(IMAGES, None):
            images = album_dict[IMAGES]
            for i in images:
                if i[WIDTH] >= 100 and i[WIDTH] <= 300:
                    setattr(s, ALBUM_IMAGE_SMALL, i[URL])
                if i[WIDTH] > 300 and i[WIDTH] <= 800:
                    setattr(s, ALBUM_IMAGE_LARGE, i[URL])
        default_image = "album"
        if getattr(s, ALBUM_IMAGE_SMALL, None) == None:
            setattr(s, ALBUM_IMAGE_SMALL, default_image)
        if getattr(s, ALBUM_IMAGE_LARGE, None) == None:
            setattr(s, ALBUM_IMAGE_LARGE, default_image)

        return s

    def get_track(self, track_dict):
        """ Create track object

        :param track_dict: spotify specific dictionary

        :return: track object
        """
        s = State()

        setattr(s, ALBUM_ID, track_dict.get(SPOTIFY_TRACK_ID, None))
        name = track_dict.get(SPOTIFY_TRACK_TITLE, None)
        setattr(s, NAME, name)
        setattr(s, LNAME, name)
        setattr(s, TRACK_DURATION, track_dict.get(SPOTIFY_TRACK_DURATION, None))
        setattr(s, TRACK_POSITION, track_dict.get(SPOTIFY_TRACK_POSITION, None))

        setattr(s, PLAYBACK_MODE, CATALOG)
        setattr(s, URL, track_dict.get(SPOTIFY_TRACK_PREVIEW, None))

        if track_dict.get(ARTISTS, None) and len(track_dict[ARTISTS]) > 0:
            a = track_dict[ARTISTS][0]
            setattr(s, TRACK_ARTIST_ID, a[SPOTIFY_ARTIST_ID])
            setattr(s, TRACK_ARTIST_NAME, a[SPOTIFY_ARTIST_NAME])
            if getattr(s, TRACK_ARTIST_NAME, None):
                setattr(s, LNAME, name + f" ({a[SPOTIFY_ARTIST_NAME]})")
        if track_dict.get(ALBUM, None):
            a = track_dict[ALBUM]
            setattr(s, TRACK_ALBUM_ID, a[SPOTIFY_ALBUM_ID])
            setattr(s, TRACK_ALBUM_TITLE, a[SPOTIFY_ALBUM_TITLE])
            if a.get(IMAGES, None):
                images = a[IMAGES]
                for i in images:
                    if i[WIDTH] >= 100 and i[WIDTH] <= 300:
                        setattr(s, ALBUM_IMAGE_SMALL, i[URL])
                    if i[WIDTH] > 300 and i[WIDTH] <= 800:
                        setattr(s, ALBUM_IMAGE_LARGE, i[URL])
            default_image = "track"
            if getattr(s, ALBUM_IMAGE_SMALL, None) == None:
                setattr(s, ALBUM_IMAGE_SMALL, default_image)
            if getattr(s, ALBUM_IMAGE_LARGE, None) == None:
                setattr(s, ALBUM_IMAGE_LARGE, default_image)

        return s

    def get_albums_by_artist_id(self, artist_id):
        """ Get albums by artist ID

        :param artist_id: artist ID

        :return: list of albums
        """
        if self.artist_albums_cache.get(artist_id, None):
            return self.artist_albums_cache[artist_id]

        response = None
        try:
            response = self.api.get_artist_albums(id=artist_id, limit=LIMIT)
        except:
            pass
        if not response or not response[SPOTIFY_ITEMS]:
            return []

        results = response[SPOTIFY_ITEMS]
        albums = []
        for r in results:
            if r.get(TYPE, None) != ALBUM:
                continue
            albums.append(self.get_album(r))

        albums.sort(key=lambda s: s.date, reverse=False)
        for i, a in enumerate(albums):
            a.index = i

        self.artist_albums_cache[artist_id] = albums

        return albums

    def get_tracks_by_album_id(self, album_id):
        """ Get tracks by album ID

        :param album_id: album ID

        :return: list of tracks
        """
        response = None
        try:
            response = self.api.get_album_tracks(id=album_id, limit=LIMIT)
        except:
            pass
        if not response or not response[SPOTIFY_ITEMS]:
            return []

        results = response[SPOTIFY_ITEMS]
        tracks = []
        for i, r in enumerate(results):
            t = self.get_track(r)
            t.index = i
            tracks.append(t)

        return tracks

    def get_artists_by_name(self, artist_name, page, page_size=ITEMS_MAX):
        """ Get list of artists

        :param artist_name: artist name
        :param page: page number
        :param page_size: page size

        :return: list of artists
        """
        artists = self.search(artist_name, self.get_artist, SPOTIFY_TYPE_ARTIST, self.artists_cache, self.artists_total_pages, page, page_size, FILTER_ARTIST)
        artists.sort(key=lambda s: s.name, reverse=False)
        for i, a in enumerate(artists):
            a.index = i

        return artists

    def get_albums_by_title(self, album_title, page, page_size=ITEMS_MAX):
        """ Get albums by album title

        :param album_title: album title
        :param page: page number
        :param page_size: page size

        :return: list of albums
        """
        albums = self.search(album_title, self.get_album, SPOTIFY_TYPE_ALBUM, self.albums_cache, self.albums_total_pages, page, page_size, FILTER_ALBUM)
        albums.sort(key=lambda s: s.name, reverse=False)
        for i, a in enumerate(albums):
            a.index = i
            if getattr(a, ALBUM_ARTIST_NAME, None):
                setattr(a, LNAME, a.name + f" ({getattr(a, ALBUM_ARTIST_NAME, None)})")

        return albums

    def get_tracks_by_title(self, track_title, page_size=ITEMS_MAX):
        """ Get tracks by track title

        :param track_title: track title
        :param page_size: page size

        :return: list of albums
        """
        tracks = self.search(track_title, self.get_track, SPOTIFY_TYPE_TRACK, self.tracks_cache, self.tracks_total_pages, 0, page_size, FILTER_TRACK)
        for i, t in enumerate(tracks):
            t.index = i

        return tracks

    def get_artists_total_pages(self, artist_name):
        """ Get the number of pages for artist name

        :param artist_name: artist name

        :return: number of pages
        """
        return self.artists_total_pages.get(artist_name, 0)

    def get_albums_total_pages(self, album_title):
        """ Get the number of pages for album title

        :param album_title: album title

        :return: number of pages
        """
        return self.albums_total_pages.get(album_title, 0)

    def get_tracks_total_pages(self, track_title):
        """ Get the number of pages for track title

        :param album_title: track title

        :return: number of pages
        """
        return self.tracks_total_pages.get(track_title, 0)

    def search(self, query, func, type, cache, totals, page, page_size, filter):
        """ Service search function

        :param query: search query
        :param func: object creation function
        :param type: object type to search for
        :param cache: object cache
        :param totals: dictionary keeping total number of objects
        :param page: page number
        :param page_size: page size
        :param filter: search filter

        :return: list of objects
        """
        if not query or len(query) < 3:
            return []

        node = cache.get(query, [])

        if node and page < len(node):
            return node[page]

        if node and page > len(node):
            return []

        response = None
        try:
            response = self.api.search(q=query + filter + query, type=type, limit=LIMIT, offset=0)
        except:
            pass
        if not response or not response.get(SPOTIFY_ITEMS, None):
            return []

        results = response[SPOTIFY_ITEMS]
        items = []
        for r in results:
            items.append(func(r))

        while len(items) < ITEMS_MAX:
            response = None
            try:
                response = self.api.search(q=query + filter + query, type=type, limit=LIMIT, offset=len(items))
            except:
                pass
            if response == None:
                continue
            if response.get(TOTAL, 0) == len(items):
                break
            results = response[SPOTIFY_ITEMS]
            for r in results:
                items.append(func(r))

        total = math.ceil(len(items) / page_size)
        totals[query] = total

        for i in range(0, len(items), page_size):
            p = items[i : i + page_size]
            node.append(p)

        if node:
            cache[query] = node

        if node and page < len(node):
            return node[page]
        else:
            return []
