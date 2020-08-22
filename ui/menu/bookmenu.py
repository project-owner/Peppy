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
from util.config import COLORS, COLOR_MEDIUM, COLOR_BRIGHT, USAGE, USE_VOICE_ASSISTANT
from util.keys import BOOK_MENU
from ui.button.multilinebutton import MultiLineButton

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
        m = self.create_book_menu_button
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

    def create_book_menu_button(self, s, constr, action, show_img=True, show_label=True, menu_button_layout=None):
        """ Create Menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images

        :return: menu button
        """
        s.bounding_box = constr
        s.img_x = None
        s.img_y = None
        s.auto_update = True
        s.show_bgr = True
        s.show_img = show_img
        s.show_label = show_label
        s.text_color_normal = self.config[COLORS][COLOR_BRIGHT]
        s.text_color_selected = (255,255,255)
        s.text_color_disabled = self.config[COLORS][COLOR_MEDIUM]
        s.text_color_current = s.text_color_normal
        s.bgr_selected = self.config[COLORS][COLOR_MEDIUM]

        menu_button_layout.create_layout(constr)
        s.layout = menu_button_layout
        s.source = BOOK_MENU
        button = MultiLineButton(self.util, s)
        button.add_release_listener(action)
        if not getattr(s, "enabled", True):
            button.set_enabled(False)
        elif getattr(s, "icon_base", False) and not getattr(s, "scaled", False):
            button.components[1].content = s.icon_base

        if self.config[USAGE][USE_VOICE_ASSISTANT]:
            s.voice_commands = [s.name.lower().strip(), s.l_name.lower().strip()]

        return button
