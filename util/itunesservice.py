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

from minim.itunes import SearchAPI
from operator import itemgetter
from util.streamingservice import *
from ui.state import State

ITUNES_ARTIST_ID = "artistId"
ITUNES_ARTIST_NAME = "artistName"
ITUNES_ARTIST_GENRE = "primaryGenreName"
ITUNES_ARTIST_LINK = "artistLinkUrl"

ITUNES_ALBUM_ID = "collectionId"
ITUNES_ALBUM_TITLE = "collectionName"
ITUNES_ALBUM_URL = "collectionViewUrl"
ITUNES_ALBUM_IMAGE = "artworkUrl100"
ITUNES_ALBUM_GENRE = "primaryGenreName"
ITUNES_ALBUM_TRACKS = "trackCount"
ITUNES_ALBUM_DATE = "releaseDate"

ITUNES_TRACK_ID = "trackId"
ITUNES_TRACK_TITLE = "trackName"
ITUNES_TRACK_URL = "trackViewUrl"
ITUNES_TRACK_DURATION = "trackTimeMillis"
ITUNES_TRACK_POSITION = "trackNumber"
ITUNES_TRACK_DATE = "releaseDate"
ITUNES_TRACK_PREVIEW = "previewUrl"
ITUNES_TRACK_ARTIST_ID = "artistId"
ITUNES_TRACK_ARTIST_NAME = "artistName"
ITUNES_TRACK_ALBUM_ID = "collectionId"
ITUNES_TRACK_ALBUM_TITLE = "collectionName"
ITUNES_TRACK_IMAGE = "artworkUrl100"
ITUNES_TRACK_GENRE = "primaryGenreName"

ITUNES_RESULTS = "results"
LIMIT = 200

class ItunesService(StreamingService):
    """ iTunes service """

    def __init__(self):
        """ Initializer """

        self.searcher = SearchAPI()
        self.artists_cache = {}
        self.artist_albums_cache = {}
        self.tracks_cache = {}

    def get_artist(self, artist_dict):
        """ Create artist object
        
        :param artist_dict: itunes specific dictionary

        :return: artist object
        """
        s = State()

        setattr(s, ARTIST_ID, artist_dict.get(ITUNES_ARTIST_ID, None))
        name = artist_dict.get(ITUNES_ARTIST_NAME, None)
        setattr(s, NAME, name)
        setattr(s, LNAME, name)
        setattr(s, ARTIST_URL, artist_dict.get(ITUNES_ARTIST_LINK, None))
        setattr(s, ARTIST_GENRE, artist_dict.get(ITUNES_ARTIST_GENRE, None))

        return s

    def get_album(self, album_dict):
        """ Create album object

        :param album_dict: itunes specific dictionary

        :return: album object
        """
        s = State()

        setattr(s, ALBUM_ID, album_dict.get(ITUNES_ALBUM_ID, None))
        name = album_dict.get(ITUNES_ALBUM_TITLE, None)
        setattr(s, NAME, name)
        setattr(s, LNAME, name)
        setattr(s, ALBUM_URL, album_dict.get(ITUNES_ALBUM_URL, None))
        setattr(s, ALBUM_GENRE, album_dict.get(ITUNES_ALBUM_GENRE, None))
        setattr(s, ALBUM_IMAGE_LARGE, album_dict.get(ITUNES_ALBUM_IMAGE, None))
        setattr(s, ALBUM_TRACKS, album_dict.get(ITUNES_ALBUM_TRACKS, None))
        setattr(s, ALBUM_DATE, album_dict.get(ITUNES_ALBUM_DATE, None))

        return s

    def get_track(self, track_dict):
        """ Create track object

        :param track_dict: itunes specific dictionary

        :return: track object
        """
        s = State()

        setattr(s, TRACK_ID, track_dict.get(ITUNES_TRACK_ID, None))
        name = track_dict.get(ITUNES_TRACK_TITLE, None)
        setattr(s, NAME, name)
        setattr(s, LNAME, name)
        setattr(s, PLAYBACK_MODE, CATALOG)
        setattr(s, TRACK_DURATION, track_dict.get(ITUNES_TRACK_DURATION, None))
        setattr(s, TRACK_POSITION, track_dict.get(ITUNES_TRACK_POSITION, None))
        setattr(s, TRACK_DATE, track_dict.get(ITUNES_TRACK_DATE, None))
        setattr(s, URL, track_dict.get(ITUNES_TRACK_PREVIEW, None))
        setattr(s, TRACK_ARTIST_ID, track_dict.get(ITUNES_TRACK_ARTIST_ID, None))
        setattr(s, TRACK_ARTIST_NAME, track_dict.get(ITUNES_TRACK_ARTIST_NAME, None))
        setattr(s, TRACK_ALBUM_ID, track_dict.get(ITUNES_TRACK_ALBUM_ID, None))
        setattr(s, TRACK_ALBUM_TITLE, track_dict.get(ITUNES_TRACK_ALBUM_TITLE, None))
        setattr(s, ALBUM_IMAGE_LARGE, track_dict.get(ITUNES_TRACK_IMAGE, None))
        setattr(s, TRACK_GENRE, track_dict.get(ITUNES_TRACK_GENRE, None))

        return s

    def get_artists_by_name(self, artist_name, page=None):
        """ Get list of artists by name

        :param artist_name: artist name

        :return: list of artists
        """
        if self.artists_cache.get(artist_name, None):
            return self.artists_cache[artist_name]

        response = self.searcher.search(term=artist_name, media="music", entity="musicArtist", limit=LIMIT)
        if not response or not response[ITUNES_RESULTS]:
            return []

        results = response[ITUNES_RESULTS]
        artists = []
        for i, r in enumerate(results):
            a = self.get_artist(r)
            a.index = i
            artists.append(a)

        self.artists_cache[artist_name] = artists

        return artists

    def get_albums_by_artist_name(self, artist_name):
        """ Get albums by artist name

        :param artist_name: artist name

        :return: list of albums
        """
        response = self.searcher.search(term=artist_name, media="music", entity="album", attribute="artistTerm", limit=LIMIT)
        if not response or not response[ITUNES_RESULTS]:
            return []

        results = response[ITUNES_RESULTS]
        albums = []
        for r in results:
            albums.append(self.get_album(r))

        return sorted(albums, key=itemgetter(ALBUM_DATE), reverse=False)

    def get_albums_by_artist_id(self, artist_id):
        """ Get albums by artist ID

        :param artist_name: artist ID

        :return: list of albums
        """
        if self.artist_albums_cache.get(artist_id, None):
            return self.artist_albums_cache[artist_id]

        response = self.searcher.lookup(id=artist_id, entity="album", limit=LIMIT)
        if not response or not response[ITUNES_RESULTS]:
            return []

        results = response[ITUNES_RESULTS]
        albums = []
        for r in results:
            if r.get("collectionType", None) != "Album":
                continue
            albums.append(self.get_album(r))

        albums.sort(key=lambda s: s.date, reverse=False)
        for i, a in enumerate(albums):
            a.index = i

        self.artist_albums_cache[artist_id] = albums

        return albums

    def get_albums_by_title(self, album_title):
        """ Get albums by album title

        :param album_title: album title

        :return: list of albums
        """
        response = self.searcher.search(term=album_title, media="music", entity="album", limit=LIMIT)
        if not response or not response[ITUNES_RESULTS]:
            return []

        results = response[ITUNES_RESULTS]
        albums = []
        for r in results:
            if not self.is_strict_match(album_title, r[ITUNES_ALBUM_TITLE]):
                continue
            albums.append(self.get_album(r))

        return sorted(albums, key=itemgetter(ALBUM_DATE), reverse=False)

    def get_tracks_by_album_id(self, album_id):
        """ Get tracks by album ID

        :param album_id: album ID

        :return: list of tracks
        """
        if self.tracks_cache.get(album_id, None):
            return self.tracks_cache[album_id]

        response = self.searcher.lookup(album_id, entity="song", limit=LIMIT)
        if not response or not response[ITUNES_RESULTS]:
            return []

        results = response[ITUNES_RESULTS]
        tracks = []
        for i, r in enumerate(results):
            if r.get("wrapperType", "") != "track":
                continue
            t = self.get_track(r)
            t.index = i
            tracks.append(t)

        self.tracks_cache[album_id] = tracks

        return tracks

    def get_tracks_by_title(self, track_title):
        """ Get list of tracks by track title

        :param track_title: track title

        :return: list of tracks
        """
        response = self.searcher.search(term=track_title, media="music", entity="song", limit=LIMIT)
        if not response or not response[ITUNES_RESULTS]:
            return []

        results = response[ITUNES_RESULTS]
        tracks = []
        for r in results:
            if r.get("wrapperType", "") != "track" or not self.is_strict_match(track_title, r[ITUNES_TRACK_TITLE]):
                continue
            tracks.append(self.get_track(r))

        return tracks
