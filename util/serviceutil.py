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

from util.keys import *

SERVICE_ITUNES = "itunes"
SERVICE_QOBUZ = "qobuz"
SERVICE_SPOTIFY = "spotify"
SERVICE_TIDAL = "tidal"
SERVICE_DEEZER = "deezer"

GET_NEW_RELEASE = "new.release.getter"
GET_BESTSELLER = "bestseller.getter"
GET_GENRE = "genre.getter"
GET_ARTIST = "artist.getter"
GET_ALBUM = "album.getter"
GET_TRACK = "track.getter"

MENU_ROWS = 5
MENU_COLUMNS = 2
MENU_PAGE_SIZE = MENU_ROWS * MENU_COLUMNS

class ServiceUtil(object):
    """ Streaming Service Utility """

    def __init__(self):
        """ Initializer """

        self.services = {
            SERVICE_QOBUZ: None,
            SERVICE_DEEZER: None,
            SERVICE_ITUNES: None,
            SERVICE_SPOTIFY: None,
            SERVICE_TIDAL: None
        }

        self.service_types = {
            KEY_CATALOG_NEW_RELEASE_SERVICE: self.set_new_release_service,
            KEY_CATALOG_BESTSELLER_SERVICE: self.set_bestseller_service,
            KEY_CATALOG_GENRE_SERVICE: self.set_genre_service,
            KEY_CATALOG_ARTIST_SERVICE: self.set_artist_service,
            KEY_CATALOG_ALBUM_SERVICE: self.set_album_service,
            KEY_CATALOG_TRACK_SERVICE: self.set_track_service
        }

        self.set_new_release_service()
        self.set_bestseller_service()
        self.set_genre_service()
        self.set_artist_service()
        self.set_album_service()
        self.set_track_service()

        self.searchers = {
            KEY_CATALOG_NEW_ALBUMS: self.get_new_releases,
            KEY_CATALOG_BESTSELLERS: self.get_bestsellers,
            KEY_CATALOG_NEW_RELEASE_TRACKS: self.get_album_tracks,
            KEY_CATALOG_BESTSELLER_TRACKS: self.get_album_tracks,
            KEY_CATALOG_GENRES: self.get_genres,
            KEY_CATALOG_GENRE_ARTISTS: self.get_genre_artists,
            KEY_CATALOG_GENRE_ARTIST_ALBUMS: self.get_genre_artist_albums,
            KEY_CATALOG_GENRE_ALBUM_TRACKS: self.get_genre_artist_album_tracks,
            KEY_CATALOG_ARTISTS: self.get_artists,
            KEY_CATALOG_ARTIST_ALBUMS: self.get_artist_albums,
            KEY_CATALOG_ARTIST_ALBUM_TRACKS: self.get_artist_album_tracks,
            KEY_CATALOG_ALBUMS: self.get_albums,
            KEY_CATALOG_ALBUM_TRACKS: self.get_album_tracks,
            KEY_CATALOG_SEARCH_TRACK: self.get_tracks
        }

    def set_service(self, catalog_service):
        """ Set service type to specific service

        :param catalog_service: tuple, where 0 - service type, 1 - service name
        """
        self.service_types[catalog_service[0]](catalog_service[1])

    def get_service(self, service_name):
        """ Get service defined by name. Use cache

        :param service_name: service name

        :return: service object
        """
        if self.services.get(service_name, None):
            return self.services[service_name]
        
        if service_name == SERVICE_QOBUZ:
            from util.qobuzservice import QobuzService
            service = QobuzService()
            self.services[SERVICE_QOBUZ] = service
        elif service_name == SERVICE_DEEZER:
            from util.deezerservice import DeezerService
            service = DeezerService()
            self.services[SERVICE_DEEZER] = service
        elif service_name == SERVICE_SPOTIFY:
            from util.spotifyservice import SpotifyService
            service = SpotifyService()
            self.services[SERVICE_SPOTIFY] = service
        elif service_name == SERVICE_ITUNES:
            from util.itunesservice import ItunesService
            service = ItunesService()
            self.services[SERVICE_ITUNES] = service

        return self.services[service_name]

    def set_new_release_service(self, service_name=SERVICE_QOBUZ):
        """ Set new release service

        :param service_name: service name
        """
        self.new_release_service = self.get_service(service_name)

    def set_bestseller_service(self, service_name=SERVICE_QOBUZ):
        """ Set bestseller service

        :param service_name: service name
        """
        self.bestseller_service = self.get_service(service_name)

    def set_genre_service(self, service_name=SERVICE_DEEZER):
        """ Set genre service

        :param service_name: service name
        """
        self.genre_service = self.get_service(service_name)

    def set_artist_service(self, service_name=SERVICE_SPOTIFY):
        """ Set artist service

        :param service_name: service name
        """
        self.artist_service = self.get_service(service_name)

    def set_album_service(self, service_name=SERVICE_SPOTIFY):
        """ Set album service

        :param service_name: service name
        """
        self.album_service = self.get_service(service_name)

    def set_track_service(self, service_name=SERVICE_SPOTIFY):
        """ Set track service

        :param service_name: service name
        """
        self.track_service = self.get_service(service_name)

    def get_new_releases(self, page, page_size=MENU_PAGE_SIZE):
        """ Get new release albums

        :param page: page number
        :param page_size: page size

        :return: list of albums
        """
        return self.new_release_service.get_new_releases(page, page_size)
    
    def get_bestsellers(self, page, page_size=MENU_PAGE_SIZE):
        """ Get new bestseller albums

        :param page: page number
        :param page_size: page size

        :return: list of albums
        """
        return self.bestseller_service.get_bestsellers(page, page_size)
    
    def get_album_tracks(self, album_id):
        """ Get album tracks by album ID

        :param album_id: album ID

        :return: list of album tracks
        """
        return self.bestseller_service.get_tracks_by_album_id(album_id)
    
    def get_genre_artist_album_tracks(self, album_id):
        """ Get genre artist album tracks by album ID

        :param album_id: album ID

        :return: list of album tracks
        """
        return self.track_service.get_genre_artist_album_tracks(album_id)
    
    def get_genres(self):
        """ Get genres

        :return: list of genres
        """
        return self.genre_service.get_genres()
    
    def get_genre_artists(self, genre_id):
        """ Get artists by genre ID

        :param genre_id: genre ID

        :return: list of genre artists
        """
        return self.genre_service.get_artists_by_genre_id(genre_id)
    
    def get_genre_artist_albums(self, artist_id):
        """ Get genre artist albums by artist ID

        :param artist_id: artist ID

        :return: list of albums
        """
        return self.genre_service.get_albums_by_artist_id(artist_id)
    
    def get_artists(self, artist_name, page):
        """ Get artists by artist name

        :param album_id: artist name
        :param page: page number

        :return: list of artists
        """
        return self.artist_service.get_artists_by_name(artist_name, page)
    
    def get_artist_albums(self, artist_id):
        """ Get artist albums by artist ID

        :param album_id: artist ID

        :return: list of albums
        """
        return self.album_service.get_albums_by_artist_id(artist_id)
    
    def get_artist_album_tracks(self, album_id):
        """ Get artist album tracks by album ID

        :param album_id: album ID

        :return: list of album tracks
        """
        return self.track_service.get_tracks_by_album_id(album_id)
    
    def get_album_tracks(self, album_id):
        """ Get album tracks by album ID

        :param album_id: album ID

        :return: list of album tracks
        """
        return self.track_service.get_tracks_by_album_id(album_id)

    def get_albums(self, album_title, page):
        """ Get albums by album title

        :param album_title: album title
        :param page: page number

        :return: list of albums
        """
        return self.album_service.get_albums_by_title(album_title, page)
    
    def get_tracks(self, track_title):
        """ Get tracks by track ID

        :param track_title: track title

        :return: list of tracks
        """
        return self.track_service.get_tracks_by_title(track_title)
