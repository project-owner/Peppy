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

import json
import logging

from tornado.web import RequestHandler

class FilePlaylistsHandler(RequestHandler):
    def initialize(self, util):
        self.file_util = util.file_util

    def get(self):
        """
        curl localhost:8000/api/fileplaylists
        curl localhost:8000/api/fileplaylists?name="C:\playlists\playlist.m3u"
        """
        if self.request.arguments:
            name = self.get_argument("name")
            playlist = self.file_util.get_m3u_playlist(name)
            self.write(json.dumps(playlist))
        else:
            playlists = self.file_util.get_file_playlists()
            if not playlists:
                self.set_status(500)
                self.finish(json.dumps({ "message": "Playlists not found"}))
            else:
                self.write(json.dumps(playlists))

    def post(self):
        """
        curl -X POST localhost:8000/api/fileplaylists?name="playlist1.m3u"
        """
        if self.request.arguments:
            name = self.get_argument("name")
            try:
                self.file_util.create_file_playlist(name)
            except Exception as e:
                logging.debug(e)
                self.set_status(500, reason=str(e))
                return self.finish()

    def put(self):
        """
        curl -X PUT -d @"c:\\playlists\\playlist.json" localhost:8000/api/fileplaylists
        """
        try:
            j = json.loads(self.request.body.decode("utf-8"))
            name = j["name"]
            content = j["content"]
            self.file_util.update_file_playlist(name, content)
        except Exception as e:
            logging.debug(e)
            self.set_status(500, reason=str(e))
            return self.finish()

    def delete(self):
        """
        curl -X DELETE localhost:8000/api/fileplaylists?name="C:\playlists\playlist.m3u"
        """
        try:
            if self.request.arguments:
                name = self.get_argument("name")
                self.file_util.delete_file_playlist(name)
        except Exception as e:
            logging.debug(e)
            self.set_status(500, reason=str(e))
            return self.finish()
