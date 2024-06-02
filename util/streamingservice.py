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

CATALOG = "catalog"

GENRE_ID = "id"
GENRE_NAME = "name"
GENRE_IMAGE = "image"

ARTIST_ID = "id"
ARTIST_NAME = "name"
ARTIST_GENRE = "genre"
ARTIST_URL = "url"
ARTIST_IMAGE = "image"
ARTIST_ALBUMS = "albums"

ALBUM_ID = "id"
ALBUM_TITLE = "title"
ALBUM_URL = "url"
ALBUM_IMAGE_SMALL = "album_image_small"
ALBUM_IMAGE_LARGE = "album_image_large"
ALBUM_LABEL = "label"
ALBUM_TRACKS = "tracks"
ALBUM_DURATION = "duration"
ALBUM_DATE = "date"
ALBUM_GENRE = "genre"
ALBUM_ARTIST_ID = "artist_id"
ALBUM_ARTIST_NAME = "artist_name"

TRACK_ID = "id"
TRACK_TITLE = "title"
TRACK_URL = "url"
TRACK_DURATION = "duration"
TRACK_POSITION = "position"
TRACK_DATE = "date"
TRACK_PREVIEW = "preview"
TRACK_ARTIST_ID = "artist id"
TRACK_ARTIST_NAME = "artist name"
TRACK_ALBUM_ID = "album"
TRACK_ALBUM_TITLE = "album title"
TRACK_IMAGE = "track image"
TRACK_GENRE = "track genre"
TRACK_IMAGE_URL = "image url"

ID = "id"
INDEX = "index"
IMAGE = "image"
ARTISTS = "artists"
ARTIST = "artist"
ALBUMS = "albums"
TRACKS = "tracks"
ITEMS = "items"
NAME = "name"
LNAME = "l_name"
SMALL = "small"
LARGE = "large"
PERFORMER = "performer"
URL = "url"
TOTAL = "total"
PLAYBACK_MODE = "playback_mode"

class StreamingService(object):
    """ Streaming Service """

    def is_strict_match(self, request_str, response_str):
        """ Compare request and response strings for match

        :param request_str: request string
        :param response_str: response string

        :return: True - request string is a asubset of response string, False - otherwise
        """
        if not request_str or not response_str:
            return False

        request_str_low = request_str.lower()
        reponse_str_low = response_str.lower()
        request_str_tokens = set(request_str_low.split())
        reponse_str_tokens = set(reponse_str_low.split())

        if request_str_tokens.issubset(reponse_str_tokens):
            return True
        else:
            return False
