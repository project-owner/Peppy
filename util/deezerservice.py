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

from deezer import Client
from operator import itemgetter
from util.streamingservice import *
from ui.state import State

DEEZER_GENRE_ID = "id"
DEEZER_GENRE_NAME = "name"

DEEZER_ARTIST_ID = "id"
DEEZER_ARTIST_PICTURE = "picture_medium"
DEEZER_ARTIST_NAME = "name"
DEEZER_ARTIST_ALBUMS = "nb_album"
DEEZER_ARTIST_LINK = "link"

DEEZER_ALBUM_ID = "id"
DEEZER_ALBUM_TITLE = "title"
DEEZER_ALBUM_URL = "link"
DEEZER_ALBUM_IMAGE = "cover_medium"
DEEZER_ALBUM_LABEL = "label"
DEEZER_ALBUM_TRACKS = "nb_tracks"
DEEZER_ALBUM_DURATION = "duration"
DEEZER_ALBUM_DATE = "release_date"

DEEZER_TRACK_ID = "id"
DEEZER_TRACK_TITLE = "title"
DEEZER_TRACK_URL = "link"
DEEZER_TRACK_DURATION = "duration"
DEEZER_TRACK_POSITION = "track_position"
DEEZER_TRACK_DATE = "release_date"
DEEZER_TRACK_PREVIEW = "preview"
DEEZER_TRACK_ARTIST_ID = "artist"
DEEZER_TRACK_ARTIST_NAME = "artit.name"
DEEZER_TRACK_ALBUM_ID = "album"
DEEZER_IMAGE_MEDIUM = "picture_medium"
DEEZER_IMAGE_BIG = "picture_big"
DEEZER_COVER_MEDIUM = "cover_medium"
DEEZER_COVER_BIG = "cover_big"

class DeezerService(StreamingService):
    """ Deezer service """
    
    def __init__(self):
        """ Initializer """

        self.client = Client()
        self.genres_cache = []
        self.genre_artists_cache = {}
        self.artist_albums = {}
        self.album_tracks = {}

    def get_genre(self, genre_obj):
        """ Create genre object

        :param genre_obj: deezer specific object

        :return: genre object
        """
        s = State()

        setattr(s, ID, getattr(genre_obj, DEEZER_GENRE_ID, None))
        name = getattr(genre_obj, DEEZER_GENRE_NAME, None)
        setattr(s, NAME, name)
        setattr(s, LNAME, name)
        setattr(s, ALBUM_IMAGE_SMALL, getattr(genre_obj, DEEZER_IMAGE_MEDIUM, None))
        setattr(s, ALBUM_IMAGE_LARGE, getattr(genre_obj, DEEZER_IMAGE_BIG, None))

        return s

    def get_artist(self, artist_obj):
        """ Create artist object
        
        :param artist_obj: deezer specific object

        :return: artist object
        """
        s = State()

        setattr(s, ID, getattr(artist_obj, DEEZER_ARTIST_ID, None))
        name = getattr(artist_obj, DEEZER_ARTIST_NAME, None)
        setattr(s, NAME, name)
        setattr(s, LNAME, name)
        setattr(s, ALBUM_IMAGE_SMALL, getattr(artist_obj, DEEZER_IMAGE_MEDIUM, None))
        setattr(s, ALBUM_IMAGE_LARGE, getattr(artist_obj, DEEZER_IMAGE_BIG, None))
        setattr(s, ARTIST_ALBUMS, getattr(artist_obj, DEEZER_ARTIST_ALBUMS, None))
        setattr(s, ARTIST_URL, getattr(artist_obj, DEEZER_ARTIST_LINK, None))

        return s
    
    def get_album(self, album_obj):
        """ Create album object

        :param album_obj: deezer specific object

        :return: album object
        """
        s = State()

        setattr(s, ID, getattr(album_obj, DEEZER_ALBUM_ID, None))
        name = getattr(album_obj, DEEZER_ALBUM_TITLE, None)
        setattr(s, NAME, name)
        setattr(s, LNAME, name)
        setattr(s, ALBUM_URL, getattr(album_obj, DEEZER_ALBUM_URL, None))
        setattr(s, ALBUM_IMAGE_SMALL, getattr(album_obj, DEEZER_COVER_MEDIUM, None))
        setattr(s, ALBUM_IMAGE_LARGE, getattr(album_obj, DEEZER_COVER_BIG, None))
        setattr(s, ALBUM_DURATION, getattr(album_obj, DEEZER_ALBUM_DURATION, None))
        setattr(s, ALBUM_DATE, getattr(album_obj, DEEZER_ALBUM_DATE, None))
        setattr(s, ALBUM_TRACKS, getattr(album_obj, DEEZER_ALBUM_TRACKS, None))

        artist = getattr(album_obj, DEEZER_TRACK_ARTIST_ID, None)
        if artist:
            setattr(s, ALBUM_ARTIST_NAME, artist.name)

        return s

    def get_track(self, track_obj, index):
        """ Create track object

        :param track_obj: deezer specific object
        :param index: track index

        :return: track object
        """
        s = State()
        s.index = index

        setattr(s, ID, getattr(track_obj, DEEZER_TRACK_ID, None))
        name = getattr(track_obj, DEEZER_TRACK_TITLE, None)
        setattr(s, NAME, name)
        setattr(s, LNAME, name)
        setattr(s, TRACK_URL, getattr(track_obj, DEEZER_TRACK_URL, None))
        setattr(s, TRACK_DURATION, getattr(track_obj, DEEZER_TRACK_DURATION, None))
        setattr(s, TRACK_DATE, getattr(track_obj, DEEZER_TRACK_DATE, None))
        setattr(s, PLAYBACK_MODE, CATALOG)
        setattr(s, URL, getattr(track_obj, DEEZER_TRACK_PREVIEW, None))

        return s

    def get_genres(self):
        """ Get the list of genres

        :return: list of genres
        """
        if self.genres_cache:
            return self.genres_cache

        response = None

        try:
            response = self.client.list_genres()
            if not response:
                return []
        except Exception as e:
            return []

        genres = []
        for g in response:
            if getattr(g, DEEZER_GENRE_NAME, None) == "All":
                continue
            genres.append(self.get_genre(g))

        genres.sort(key=lambda s: s.name, reverse=False)
        for i, g in enumerate(genres):
            g.index = i

        self.genres_cache = genres

        return genres
    
    def get_artists_by_genre_id(self, genre_id):
        """ Get list of artists by genre ID

        :param genre_id: genre ID

        :return: list of artists
        """
        if self.genre_artists_cache.get(genre_id, None):
            return self.genre_artists_cache[genre_id]

        genre = None
        try:
            genre = self.client.get_genre(genre_id)
            if not genre:
                return []
        except Exception as e:
            return []

        response = None
        artists = []

        try:
            response = genre.get_artists()
            if not response:
                return []
        except Exception as e:
            return []

        for r in response:
            artists.append(self.get_artist(r))

        artists.sort(key=lambda s: s.name, reverse=False)
        for i, a in enumerate(artists):
            a.index = i

        self.genre_artists_cache[genre_id] = artists

        return artists

    def get_artists_by_name(self, artist_name):
        """ Get list of artists by name

        :param artist_name: artist name

        :return: list of artists
        """
        response = None
        artists = []

        try:
            response = self.client.search_artists(query=artist_name)
            if not response:
                return []
        except Exception as e:
            return []

        for r in response:
            response_name = getattr(r, DEEZER_ARTIST_NAME, "")
            if not self.is_strict_match(artist_name, response_name):
                continue
            artists.append(self.get_artist(r))

        return artists

    def get_albums_by_artist_name(self, artist_name):
        """ Get albums by artist name

        :param artist_name: artist name

        :return: list of albums
        """
        artist = self.get_artists_by_name(artist_name=artist_name)
        response = None

        if not artist:
            return []

        artist_id = artist[0][ARTIST_ID]

        try:
            response = self.client.get_artist(artist_id)
            if not response:
                return []
        except Exception as e:
            return []

        try:
            artist_albums = response.get_albums()
            if not artist_albums:
                return []
        except Exception as e:
            return []   

        albums = []
        for album in artist_albums:
            albums.append(self.get_album(album))

        sorted_albums = sorted(albums, key=itemgetter(ALBUM_DATE), reverse=False)

        return sorted_albums
    
    def get_albums_by_artist_id(self, artist_id):
        """ Get albums by artist ID

        :param artist_name: artist ID

        :return: list of albums
        """
        if self.artist_albums.get(artist_id, None):
            return self.artist_albums[artist_id]

        response = None
        artist_albums = None

        try:
            response = self.client.get_artist(artist_id)
            if not response:
                return []
        except Exception as e:
            return []

        try:
            artist_albums = response.get_albums()
            if not artist_albums:
                return []
        except Exception as e:
            return []

        albums = []
        for album in artist_albums:
            if getattr(album, "record_type", None) != "single":
                albums.append(self.get_album(album))

        albums.sort(key=lambda s: s.date, reverse=False)
        for i, a in enumerate(albums):
            a.index = i

        self.artist_albums[artist_id] = albums

        return albums

    def get_albums_by_title(self, album_title):
        """ Get albums by title

        :param album_title: album title

        :return: list of albums
        """
        response = None

        try:
            response = self.client.search_albums(query=album_title, strict=True)
            if not response:
                return []
        except Exception as e:
            return []

        albums = []
        for album in response:
            if not self.is_strict_match(album_title, getattr(album, DEEZER_ALBUM_TITLE, "")):
                continue
            albums.append(self.get_album(album))

        sorted_albums = sorted(albums, key=itemgetter(ALBUM_DATE), reverse=False)

        return sorted_albums

    def get_genre_artist_album_tracks(self, album_id):
        """ Get tracks by album ID

        :param album_id: album ID

        :return: list of tracks
        """
        if self.album_tracks.get(album_id, None):
            return self.album_tracks[album_id]

        response = None
        try:
            response = self.client.get_album(album_id)
        except Exception as e:
            return []

        if not response:
            return []

        if not response.get_tracks():
            return

        artist = response.get_artist()
        response_tracks = response.get_tracks()
        tracks = []
        for i, t in enumerate(response_tracks):
            track = self.get_track(t, i)
            if artist and artist.name:
                setattr(track, TRACK_ARTIST_NAME, artist.name)
            tracks.append(track)

        self.album_tracks[album_id] = tracks

        return tracks

    def get_tracks_by_title(self, track_title):
        """ Get list of tracks by track title

        :param track_title: track title

        :return: list of tracks
        """
        response = None

        try:
            response = self.client.search(track=track_title, strict=True)
            if not response:
                return []
        except Exception as e:
            return []

        tracks = []
        for i, t in enumerate(response):
            tracks.append(self.get_track(t, i))

        return tracks

    def get_track_by_id(self, track_id):
        """ Get track info by track ID

        :param track_id: track ID

        :return: track info
        """
        response = None

        try:
            response = self.client.get_track(track_id)
            if not response:
                return []
        except Exception as e:
            return []

        track = self.get_track(response, 0)
        artist = response.get_artist()
        if artist:
            track[TRACK_ARTIST_ID] = artist.name
        album = response.get_album()
        if album:
            track[TRACK_ALBUM_ID] = album.title

        return track
