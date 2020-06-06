# Copyright 2016-2020 Peppy Player peppy.player@gmail.com
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
from util.keys import KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, CLASSICAL, \
    JAZZ, POP, ROCK, CONTEMPORARY, FLAT, KEY_HOME, KEY_PLAYER, KEY_PLAY_PAUSE
from util.config import BACKGROUND, FOOTER_BGR_COLOR

class EqualizerNavigator(Container):
    """ Equalizer Navigator Menu class """
    
    def __init__(self, util, home_listener, player_listener, presets_listener, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param listeners: menu listeners
        :param bgr: menu background
        :param bounding_box: bounding box
        """   
        Container.__init__(self, util)
        self.content = None
        self.factory = Factory(util)
        self.name = "equalizer.navigator"
        self.content_x = bounding_box.x
        self.content_y = bounding_box.y
        self.menu_buttons = []

        layout = GridLayout(bounding_box)        
        layout.set_pixel_constraints(1, 8, 1, 0)        
        layout.current_constraints = 0
        size = 64 # button image size in percent
        bgr = util.config[BACKGROUND][FOOTER_BGR_COLOR]
        
        constr = layout.get_next_constraints()
        self.home_button = self.factory.create_button(KEY_HOME, KEY_HOME, constr, home_listener, bgr, size - 0.5)
        self.add_component(self.home_button)
        self.menu_buttons.append(self.home_button)
        
        constr = layout.get_next_constraints()
        self.classical_button = self.factory.create_button(CLASSICAL, KEY_1, constr, presets_listener, bgr, size)
        self.add_component(self.classical_button)
        self.menu_buttons.append(self.classical_button)
        
        constr = layout.get_next_constraints()
        self.jazz_button = self.factory.create_button(JAZZ, KEY_2, constr, presets_listener, bgr, size)
        self.add_component(self.jazz_button)
        self.menu_buttons.append(self.jazz_button)
        
        constr = layout.get_next_constraints()
        self.pop_button = self.factory.create_button(POP, KEY_3, constr, presets_listener, bgr, size)
        self.add_component(self.pop_button)
        self.menu_buttons.append(self.pop_button)
        
        constr = layout.get_next_constraints()
        self.rock_button = self.factory.create_button(ROCK, KEY_4, constr, presets_listener, bgr, size)
        self.add_component(self.rock_button)
        self.menu_buttons.append(self.rock_button)
        
        constr = layout.get_next_constraints()
        self.contemporary_button = self.factory.create_button(CONTEMPORARY, KEY_5, constr, presets_listener, bgr, size)
        self.add_component(self.contemporary_button)
        self.menu_buttons.append(self.contemporary_button)
        
        constr = layout.get_next_constraints()
        self.neutral_button = self.factory.create_button(FLAT, KEY_6, constr, presets_listener, bgr, size)
        self.add_component(self.neutral_button)
        self.menu_buttons.append(self.neutral_button)
        
        constr = layout.get_next_constraints()
        self.player_button = self.factory.create_button(KEY_PLAYER, KEY_PLAY_PAUSE, constr, player_listener, bgr, size)
        self.add_component(self.player_button)
        self.menu_buttons.append(self.player_button)
    
    def set_parent_screen(self, scr):
        """ Add parent screen

        :param scr: parent screen
        """
        for b in self.menu_buttons:
            b.parent_screen = scr