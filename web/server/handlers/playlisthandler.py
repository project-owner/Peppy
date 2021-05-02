# Copyright 2021 Peppy Player peppy.player@gmail.com
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
import json
import logging

from tornado.web import RequestHandler, HTTPError

class PlaylistHandler(RequestHandler):
    def initialize(self, root):
        self.root = root

    def get(self):
        path = self.root + os.sep + self.request.arguments["path"][0].decode("utf-8")
        if not path or not os.path.exists(path):
            raise HTTPError(404)

        filename = path.split("/")[-1]
        self.set_header('Content-Type', 'application/force-download')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % filename)    
        with open(path, "rb") as f:
            try:
                while True:
                    buffer = f.read(4096)
                    if buffer:
                        self.write(buffer)
                    else:
                        f.close()
                        self.finish()
                        return
            except:
                raise HTTPError(404)

    def post(self):
        file = self.request.files["data"][0]
        path = self.root + os.sep + self.request.arguments["path"][0].decode("utf-8") + file.filename
        logging.debug(path)

        try:
            logging.debug(f"Saving file: {path}")
            new_file = open(path, "wb")
            new_file.write(file["body"])
            logging.debug(f"Saved file: {path}")
        except Exception as e:
            logging.debug(e)
            self.set_status(500)
            self.finish(json.dumps({ "message": f"Cannot save file: {path}"}))
