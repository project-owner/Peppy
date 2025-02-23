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

from web.server.peppyrequesthandler import PeppyRequestHandler

class GenreIconHandler(PeppyRequestHandler):
    """ curl http://localhost:8000/api/genreicon?category=line&name=home&color1=(100,100,100)&color2=(200,200,200)
    """
    def initialize(self, peppy):
        self.util = peppy.util
        self.image_util = peppy.util.image_util

    def get(self):
        try:
            category = name = color_1 = color_2 = None

            if not self.request.arguments:
                return
            
            genres = self.util.get_genres()

            if not genres:
                return

            type = self.get_argument("type", default=None)
            category = self.get_argument("category", default=None)
            name = self.get_argument("name", default=None)

            color_1 = self.get_colors(self.get_argument("color1", default=None))
            color_2 = self.get_colors(self.get_argument("color2", default=None))

            c_1 = self.image_util.color_to_hex(color_1)
            c_2 = self.image_util.color_to_hex(color_2)

            for genre in genres.keys():
                if genre == name:
                    path = genres[genre].folder_image_svg
                    img = self.image_util.load_svg_icon_main(type, name, c_1, c_2, category, filepath=path)

            self.set_header("Content-Type", "image/svg+xml")
            self.write(img)
        except:
            self.set_status(500)
            return self.finish()
