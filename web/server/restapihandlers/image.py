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

from web.server.jsonfactory import JsonFactory
from web.server.peppyrequesthandler import PeppyRequestHandler

class ImageHandler(PeppyRequestHandler):
    def initialize(self, peppy):
        self.peppy = peppy
        self.json_factory = JsonFactory(peppy.util, peppy)

    def get(self):
        try:
            current_player_screen = self.peppy.current_player_screen
            if not current_player_screen:
                return

            s = self.peppy.screens[current_player_screen]
            if not s:
                return
                
            center_button = s.center_button
            content = center_button.components[1].content
            if isinstance(content, tuple):
                surface = content[1]
            else:
                surface = content
            
            img = self.peppy.util.image_util.get_png_from_surface(surface)
            self.set_header("Content-Type", "image/png")
            self.write(img)
        except:
            self.set_status(500)
            return self.finish()
