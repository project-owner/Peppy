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

from ui.menu.menu import Menu, ALIGN_LEFT
from util.keys import kbd_keys
    
class MultiPageMenu(Menu):
    """ Multi-page menu class. Extends Menu class. """
    
    def __init__(self, util, next_page, previous_page, set_title, reset_title, go_to_page, create_item, rows, columns, mbl, 
        bgr=None, bounding_box=None, align=ALIGN_LEFT, horizontal=True, font_size=None):
        """ Initializer
        
        :param util: utility object
        :param next_page: next page callback
        :param previous_page: previous page callback
        :param set_title: set title callback
        :param reset_title: reset title callback
        :param go_to_page: go to page callback
        :param create_item: create menu item method
        :param rows: menu rows
        :param columns: menu columns
        :param mbl: multi-line button layout
        :param bgr: menu background
        :param bounding_box: bounding box
        """ 
        self.next_page = next_page
        self.previous_page = previous_page
        self.set_title = set_title
        self.reset_title = reset_title
        self.go_to_page = go_to_page
        self.start_page_num = False
        self.current_page_num = ""
        self.current_page = 1
        self.page_size = rows * columns
        Menu.__init__(self, util, bgr, bounding_box, rows, columns, create_item_method=create_item, menu_button_layout=mbl, font_size=font_size, align=align, horizontal_layout=horizontal)

    def get_num_str(self, key):
        """ Get number string by keyboard key code
        
        :param key: key code
        
        :return: number string
        """
        for k, v in kbd_keys.items():
            if v == key:
                return k
            else:
                continue
