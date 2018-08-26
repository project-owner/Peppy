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

from ui.container import Container
from ui.layout.gridlayout import GridLayout
from ui.factory import Factory
from util.config import LANGUAGE, SCREENSAVER, EQUALIZER, HOME_MENU
from util.keys import KEY_PLAYER, KEY_ABOUT, KEY_HOME, KEY_BACK, KEY_MENU, \
    KEY_PLAY_PAUSE, KEY_SETUP, KEY_ROOT

class HomeNavigatorMenu(Container):
    """ Home Navigator Menu class. Extends base Menu class """
    
    def __init__(self, util, listeners, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param listeners: menu listeners
        :param bgr: menu background
        :param bounding_box: bounding box
        """   
        Container.__init__(self, util)
        self.factory = Factory(util)
        self.name = "home.navigator"
        self.content = self.bounding_box = bounding_box
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.menu_buttons = []

        layout = GridLayout(bounding_box)
        
        screensaver_available = util.is_screensaver_available()
        if screensaver_available:
            n = 5
        else:
            n = 4
            
        if util.config[HOME_MENU][EQUALIZER]:
            n += 1
        
        layout.set_pixel_constraints(1, n, 1, 0)        
        layout.current_constraints = 0
        size = 64 # button image size in percent
        
        constr = layout.get_next_constraints()
        self.back_button = self.factory.create_button(KEY_BACK, KEY_BACK, constr, listeners[KEY_BACK], bgr, size)
        self.add_component(self.back_button)
        self.menu_buttons.append(self.back_button)
        
        if screensaver_available:
            constr = layout.get_next_constraints()
            self.saver_button = self.factory.create_button(SCREENSAVER, KEY_SETUP, constr, listeners[SCREENSAVER], bgr, size)
            self.add_component(self.saver_button)
            self.menu_buttons.append(self.saver_button)
        
        constr = layout.get_next_constraints()
        self.language_button = self.factory.create_button(LANGUAGE, KEY_MENU, constr, listeners[LANGUAGE], bgr, size)
        self.add_component(self.language_button)
        self.menu_buttons.append(self.language_button)
        
        if util.config[HOME_MENU][EQUALIZER]:
            constr = layout.get_next_constraints()
            self.equalizer_button = self.factory.create_button(EQUALIZER, KEY_ROOT, constr, listeners[EQUALIZER], bgr, size)
            self.add_component(self.equalizer_button)
            self.menu_buttons.append(self.equalizer_button)
        
        constr = layout.get_next_constraints()
        self.player_button = self.factory.create_button(KEY_PLAYER, KEY_PLAY_PAUSE, constr, listeners[KEY_PLAYER], bgr, size)
        self.add_component(self.player_button)
        self.menu_buttons.append(self.player_button)

        constr = layout.get_next_constraints()
        self.about_button = self.factory.create_button(KEY_ABOUT, KEY_HOME, constr, listeners[KEY_ABOUT], bgr, size)
        self.add_component(self.about_button)
        self.menu_buttons.append(self.about_button)
        
