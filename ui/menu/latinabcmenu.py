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

from ui.menu.menu import Menu
from ui.factory import Factory
from ui.state import State
from util.config import COLOR_DARK, COLORS, COLOR_BRIGHT, COLOR_CONTRAST, COLOR_MEDIUM, \
    BACKGROUND, MENU_BGR_COLOR
from util.keys import KEY_ABC
from ui.button.button import Button

ROWS = 4
COLUMNS = 7
ABC = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", 
    "R", "S", "T", "U", "foo", "V", "W", "X", "Y", "Z", "bar"]
FONT_HEIGHT = 40

class LatinAbcMenu(Menu):
    """ Latin Alphabet menu """
    
    def __init__(self, util, callback, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param callback: callback method
        :param bgr: menu background
        :param bounding_box: bounding box
        """        
        self.factory = Factory(util)
        self.util = util
        self.config = util.config
        self.current_ch = ABC[0]
        
        m = self.create_latin_abc_menu_button
        font_size = int(((bounding_box.h / ROWS) / 100) * FONT_HEIGHT)
        Menu.__init__(self, util, bgr, bounding_box, ROWS, COLUMNS, create_item_method=m, font_size=font_size)
        self.config = util.config
        self.callback = callback      
        self.chars = self.load_menu()         
        self.set_items(self.chars, 0, self.abc_action, False)
        self.make_blank("foo")
        self.make_blank("bar")

        self.select_by_index(0)
    
    def create_latin_abc_menu_button(self, s, constr, action, scale, font_size):
        """ Create Latin ABC Menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param show_img: True - show image, False - don't show image
        :param show_label: True - show label, False - don't show label

        :return: menu button
        """
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = False
        s.show_label = True
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = self.config[COLORS][COLOR_CONTRAST]
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        s.bgr = self.config[BACKGROUND][MENU_BGR_COLOR]
        s.fixed_height = font_size

        button = Button(self.util, s)
        button.add_release_listener(action)

        return button

    def load_menu(self):
        """ Load menu items 
        
        :return: dictionary of the items
        """
        items = {}
        i = 0
        
        for a in ABC:
            state = State()
            state.name = a
            state.l_name = state.name
            state.bgr = self.config[COLORS][COLOR_DARK]
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = True
            state.show_img = False
            state.show_label = True
            state.comparator_item = state.name
            if a == "foo": 
                state.index = 20.5
            elif a == "bar": 
                state.index = 40
            else:
                state.index = i
                i += 1
            items[state.name] = state
            
        return items
    
    def make_blank(self, label):
        """ Make blank side buttons in the last row

        :param label: button label - foo or bar
        """
        b = self.buttons[label]
        b.release_listeners = []
        b.components[1] = None
        b.components[2] = None
        b.state.enabled = False
        b.show_label = False

    def abc_action(self, state):
        """ Menu action handler 
        
        :param state: menu button state
        """        
        self.select_by_index(state.index)
        state.source = KEY_ABC
        self.callback(state)
