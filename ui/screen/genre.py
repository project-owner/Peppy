# Copyright 2016 Peppy Player peppy.player@gmail.com
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

from ui.screen.screen import Screen
from ui.menu.genremenu import GenreMenu
from util.util import KEY_GENRE

class GenreScreen(Screen):
    """ Genre Screen. Extends base Screen class """
    
    def __init__(self, util, listener):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        Screen.__init__(self, util, KEY_GENRE)
        self.genre_menu = GenreMenu(util, (0, 0, 0), self.layout.CENTER)
        self.genre_menu.add_listener(listener)
        self.add_menu(self.genre_menu)
