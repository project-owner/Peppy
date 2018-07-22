# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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

from ui.screen.screen import Screen, PERCENT_TOP_HEIGHT
from ui.menu.genremenu import GenreMenu
from util.util import KEY_GENRE
from ui.factory import Factory

class RadioGenreScreen(Screen):
    """ Radio Genre Screen. Extends base Screen class """
    
    def __init__(self, util, listeners, voice_assistant):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        screen_title = util.get_stations_top_folder()
        Screen.__init__(self, util, None, PERCENT_TOP_HEIGHT, voice_assistant, title=screen_title)
        self.genre_menu = GenreMenu(util, (0, 0, 0), self.layout.CENTER)
        self.genre_menu.add_listener(listeners[KEY_GENRE])
        self.add_menu(self.genre_menu)
        
        factory = Factory(util)        
        buttons = factory.create_home_player_buttons(self, self.layout.BOTTOM, listeners)
        self.home_button = buttons[0]
        self.player_button = buttons[1]

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.genre_menu.add_menu_observers(update_observer, redraw_observer, release=False)
        self.genre_menu.add_move_listener(redraw_observer)
        
        self.add_button_observers(self.home_button, update_observer, redraw_observer, release=False)   
        self.add_button_observers(self.player_button, update_observer, redraw_observer, release=False)
