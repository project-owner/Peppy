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

import os

from ui.state import State
from ui.factory import Factory
from ui.menu.multipagemenu import MultiPageMenu
from ui.menu.menu import ALIGN_CENTER

class BookMenu(MultiPageMenu):
    """ Book Menu class. Extends base Menu class """
    
    def __init__(self, util, next_page, previous_page, set_title, reset_title, go_to_page, callback, rows, columns, menu_button_layout, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param next_page: next page callback
        :param previous_page: previous page callback
        :param set_title: set title callback
        :param reset_title: reset title callback
        :param go_to_page: go to page callback
        :param callback: 
        :param rows: menu rows
        :param columns: menu columns
        :param menu_button_layout: button layout
        :param bounding_box: bounding box
        """ 
        self.factory = Factory(util)
        self.util = util
        
        self.callback = callback
        self.config = self.util.config
        m = self.factory.create_book_menu_button
        self.bounding_box = bounding_box
        self.menu_button_layout = menu_button_layout        
        
        MultiPageMenu.__init__(self, util, next_page, previous_page, set_title, reset_title, go_to_page, m, rows, 
            columns, menu_button_layout, None, bounding_box, align=ALIGN_CENTER)
        
        self.browsing_history = {}        
        self.left_number_listeners = []
        self.right_number_listeners = []
        self.change_folder_listeners = []
        self.play_file_listeners = []
        self.playlist_size_listeners = []
        self.menu_navigation_listeners = []
        self.page_turned = False
        self.separator = os.sep
        self.selected_index = 0
        self.empty_state = State()
