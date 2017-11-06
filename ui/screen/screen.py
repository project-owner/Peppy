# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
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
from ui.factory import Factory
from ui.layout.borderlayout import BorderLayout
from util.util import LABELS
from util.config import SCREEN_RECT, COLORS, COLOR_DARK_LIGHT, COLOR_CONTRAST 

PERCENT_TOP_HEIGHT = 14.00
PERCENT_TITLE_FONT = 54.00

class Screen(Container):
    """ Base class for all screens. Extends Container class """
    
    def __init__(self, util, title_key, percent_bottom_height=0):
        """ Initializer
        
        :param util: utility object
        :param title_key: the resource bundle key for the screen title
        """
        Container.__init__(self, util)
        self.util = util
        factory = Factory(util)
        self.config = util.config
        self.bounding_box = self.config[SCREEN_RECT]
        self.bgr = (0, 0, 0)
        self.layout = BorderLayout(self.config[SCREEN_RECT])
        self.layout.set_percent_constraints(PERCENT_TOP_HEIGHT, percent_bottom_height, 0, 0)

        font_size = (self.layout.TOP.h * PERCENT_TITLE_FONT)/100.0
        d = self.config[COLORS][COLOR_DARK_LIGHT]
        c = self.config[COLORS][COLOR_CONTRAST]
        self.screen_title = factory.create_output_text("screen_title", self.layout.TOP, d, c, int(font_size))
        label = self.config[LABELS][title_key]
        self.screen_title.set_text(label) 
        self.add_component(self.screen_title)
        self.player_screen = False
        
    def add_menu(self, menu):
        """ Add menu to the screen
        
        :param menu: the menu to add
        """
        self.menu = menu
        self.add_component(menu)
    
    def enable_player_screen(self, flag):
        """ Enable player screen
        
        :param flag: enable/disable flag
        """
        pass
    
    def exit_screen(self):
        """ Complete actions required to save screen state """
        
        self.set_visible(False)
