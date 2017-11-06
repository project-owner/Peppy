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

from ui.menu.menu import Menu
from ui.factory import Factory
from ui.state import State
from websiteparser.audioknigi.constants import ABC_RU, FILTERS_RU, INITIAL_CHAR
from util.config import COLOR_DARK, COLORS

CHAR_ROWS = 5
CHAR_COLUMNS = 10

class CyrillicMenu(Menu):
    """ Cyrillic Menu class. Extends base Menu class """
    
    def __init__(self, util, show_authors, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param show_authors: callback method
        :param bgr: menu background
        :param bounding_box: bounding box
        """        
        self.factory = Factory(util)
        self.util = util
        self.config = util.config
        self.current_ch = INITIAL_CHAR
        
        m = self.factory.create_cyrillic_menu_button    
        Menu.__init__(self, util, bgr, bounding_box, CHAR_ROWS, CHAR_COLUMNS, create_item_method=m)
        self.config = util.config
        self.show_authors = show_authors      
        self.chars = self.load_menu()         
        self.set_items(self.chars, 0, self.abc_action, False)
        i = self.get_index_by_name(self.current_ch)
        self.select_by_index(i)
    
    def load_menu(self):
        """ Load menu items """
        
        items = {}
        i = 0
        
        for a in ABC_RU:
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
            state.index = i
            items[state.name] = state
            i += 1
            
        sub = FILTERS_RU[INITIAL_CHAR]
        for a in sub:
            state = State()
            state.name = a
            state.l_name = state.name
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = False
            state.show_img = False
            state.show_label = True
            state.comparator_item = state.name
            state.index = i
            items[state.name] = state
            i += 1         
                    
        return items
    
    def abc_action(self, state):
        """ Menu action handler 
        
        :param state: menu button state
        """        
        ch = state.name
        if ch in ABC_RU:
            if self.current_ch == None:
                self.handle_single_click(ch)
            else:
                if ch == self.current_ch:
                    self.handle_double_click(ch, None)
                else:
                    self.handle_single_click(ch)            
        else:
            self.handle_double_click(self.current_ch, ch)
        self.select_by_index(state.index)
    
    def get_index_by_name(self, name):
        """ Get button index by name
        
        :param name: menu button name
        """
        for b in self.chars.values():
            if b.name == name:
                return b.index
        return 0        
    
    def handle_single_click(self, ch):
        """ Single mouse click handler
        
        :param ch: selected character
        """
        self.current_ch = ch
        self.change_submenu(ch)
        
    def handle_double_click(self, ch, f):
        """ Double mouse click handler
        
        :param ch: selected character
        :param f: selected filter
        """
        self.show_authors(ch, f)
        
    def change_submenu(self, ch):
        """ Change bottom submenu
        
        :param ch: selected character
        """        
        sub = []
        try:
            sub = FILTERS_RU[ch]
        except:
            pass
        items = {}
        cp = self.buttons.copy()
        backup = {}
        for ch in ABC_RU:
            backup[ch] = cp[ch].state
        
        i = len(ABC_RU)
        for a in sub:
            state = State()
            state.name = a
            state.l_name = state.name
            state.img_x = None
            state.img_y = None
            state.auto_update = True
            state.show_bgr = False
            state.show_img = False
            state.show_label = True
            state.comparator_item = state.name
            state.index = i
            items[state.name] = state
            i += 1     

        items.update(backup)
        self.set_items(items, 0, self.abc_action, False)
        self.clean_draw_update()
