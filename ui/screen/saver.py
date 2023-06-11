# Copyright 2016-2023 Peppy Player peppy.player@gmail.com
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

from ui.menu.savermenu import SaverMenu
from ui.navigator.saver import SaverNavigator
from ui.screen.screen import Screen, PERCENT_TOP_HEIGHT
from util.config import SCREENSAVER, NAME
from util.keys import LABELS

class SaverScreen(Screen):
    """ Screensaver Screen """
    
    def __init__(self, util, listeners):
        """ Initializer
        
        :param util: utility object
        :param listener: screen menu event listener
        """
        Screen.__init__(self, util, "", PERCENT_TOP_HEIGHT)
        self.util = util
        config = util.config
        
        self.saver_menu = SaverMenu(util, None, self.layout.CENTER)
        self.saver_menu.selected = True
        self.saver_menu.add_listener(self.set_title)
        self.add_menu(self.saver_menu)
        
        self.label = config[LABELS][SCREENSAVER]
        name = self.config[SCREENSAVER][NAME]
        l_name = config[LABELS][name]
        txt = self.label + ": " + l_name
        self.screen_title.set_text(txt)
        
        self.navigator = SaverNavigator(util, self.layout.BOTTOM, listeners)
        self.add_navigator(self.navigator)
        self.top_menu_enabled = True
        
        self.link_borders()

    def set_title(self, state):
        txt = self.label + ": " + state.l_genre
        self.screen_title.set_text(txt)
        for b in self.navigator.components:
            b.set_selected(False)
            b.clean_draw_update()

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.saver_menu.add_menu_observers(update_observer, redraw_observer, release=False)
        self.saver_menu.add_move_listener(redraw_observer)
        self.navigator.add_observers(update_observer, redraw_observer)
