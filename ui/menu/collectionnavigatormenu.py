# Copyright 2020 Peppy Player peppy.player@gmail.com
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
from util.keys import KEY_PLAYER, KEY_PLAY_PAUSE, KEY_HOME, KEY_BACK

class CollectionNavigatorMenu(Container):
    """ Collection Navigator Menu class """
    
    def __init__(self, util, listeners, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param listeners: menu listeners
        :param bgr: menu background
        :param bounding_box: bounding box
        """   
        Container.__init__(self, util)
        self.factory = Factory(util)
        self.name = "collection.navigator"
        self.content = self.bounding_box = bounding_box
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.menu_buttons = []

        layout = GridLayout(bounding_box)
        layout.set_pixel_constraints(1, 3, 1, 0)
        layout.current_constraints = 0
        size = 64 # button image size in percent

        constr = layout.get_next_constraints()
        self.home_button = self.factory.create_button(KEY_HOME, KEY_HOME, constr, listeners[KEY_HOME], bgr, size)
        self.add_component(self.home_button)
        self.menu_buttons.append(self.home_button)

        constr = layout.get_next_constraints()
        self.back_button = self.factory.create_button(KEY_BACK, KEY_BACK, constr, listeners[KEY_BACK], bgr, size)
        self.add_component(self.back_button)
        self.menu_buttons.append(self.back_button)
        
        constr = layout.get_next_constraints()
        self.player_button = self.factory.create_button(KEY_PLAYER, KEY_PLAY_PAUSE, constr, listeners[KEY_PLAYER], bgr, size)
        self.add_component(self.player_button)
        self.menu_buttons.append(self.player_button)
