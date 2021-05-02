# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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

from ui.navigator.navigator import Navigator
from util.util import IMAGE_ABC, IMAGE_NEW_BOOKS, IMAGE_BOOK_GENRE, IMAGE_PLAYER
from util.keys import GO_BACK, GO_LEFT_PAGE, GO_RIGHT_PAGE, GO_ROOT, GO_USER_HOME, GO_TO_PARENT, GO_PLAYER, \
    KEY_HOME, KEY_BACK, KEY_PLAY_FILE, BOOK_NAVIGATOR_BACK, BOOK_NAVIGATOR

class BookNavigator(Navigator):
    """ Book navigator """

    def __init__(self, util, bounding_box, listeners, language_url=None):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        :param language_url: language URL
        """
        items = []
        self.add_button(items, KEY_HOME, None, [listeners[KEY_HOME]])

        if language_url == None:
            self.add_button(items, IMAGE_ABC, None, [listeners[GO_USER_HOME]])

        self.add_button(items, IMAGE_NEW_BOOKS, None, [listeners[GO_ROOT]])

        if language_url == None or language_url == "": # English-USA or Russian
            self.add_button(items, IMAGE_BOOK_GENRE, None, [listeners[GO_TO_PARENT]])

        self.add_button(items, IMAGE_PLAYER, None, [listeners[GO_PLAYER]], source=BOOK_NAVIGATOR)
        self.add_button(items, KEY_BACK, None, [listeners[GO_BACK]], source=BOOK_NAVIGATOR_BACK)
        
        arrow_items = []
        self.add_button(arrow_items, None, None, [listeners[GO_LEFT_PAGE]])
        self.add_button(arrow_items, None, None, [listeners[GO_RIGHT_PAGE]])

        Navigator.__init__(self, util, bounding_box, "book.navigator", items, arrow_items)
        self.back_button = self.get_button_by_name(KEY_BACK)
        try:
            self.back_button.add_release_listener(listeners[KEY_PLAY_FILE])
        except:
            pass


# import os

# from ui.container import Container
# from ui.layout.gridlayout import GridLayout
# from ui.layout.borderlayout import BorderLayout
# from ui.factory import Factory
# from util.util import IMAGE_ABC, IMAGE_NEW_BOOKS, IMAGE_BOOK_GENRE, IMAGE_PLAYER
# from util.keys import GO_BACK, GO_LEFT_PAGE, GO_RIGHT_PAGE, GO_ROOT, GO_USER_HOME, GO_TO_PARENT, GO_PLAYER, KEY_SETUP, \
#     KEY_HOME, KEY_BACK, KEY_MENU, KEY_PLAY_FILE, KEY_ROOT, BOOK_NAVIGATOR_BACK, KEY_PLAY_PAUSE, BOOK_NAVIGATOR
# from websiteparser.loyalbooks.constants import ENGLISH_USA, RUSSIAN, LANGUAGE_PREFIX
# from util.config import BACKGROUND, FOOTER_BGR_COLOR

# PERCENT_ARROW_WIDTH = 17.0

# class BookNavigator(Container):
#     """ Book navigator menu """
    
#     def __init__(self, util, bounding_box, listeners, language_url=None):
#         """ Initializer
        
#         :param util: utility object
#         :param bounding_box: bounding box
#         :param listeners: buttons listeners
#         :param language_url: language constant        
#         """ 
#         Container.__init__(self, util)
#         self.factory = Factory(util)
#         self.name = "navigator"
#         arrow_layout = BorderLayout(bounding_box)
#         arrow_layout.set_percent_constraints(0, 0, PERCENT_ARROW_WIDTH, PERCENT_ARROW_WIDTH)
#         self.menu_buttons = []
        
#         constr = arrow_layout.LEFT
#         self.left_button = self.factory.create_page_down_button(constr, "0", 34, 100)
#         self.left_button.add_release_listener(listeners[GO_LEFT_PAGE])
#         self.add_component(self.left_button)
#         self.menu_buttons.append(self.left_button)
        
#         layout = GridLayout(arrow_layout.CENTER)
#         if language_url == "": # English-USA
#             buttons = 5
#         elif language_url == None: #Russian
#             buttons = 6
#         else:
#             buttons = 4
#         layout.set_pixel_constraints(1, buttons, 1, 0)        
#         layout.current_constraints = 0
#         image_size = 56
#         b = util.config[BACKGROUND][FOOTER_BGR_COLOR]
        
#         constr = layout.get_next_constraints()
#         self.home_button = self.factory.create_button(KEY_HOME, KEY_HOME, constr, listeners[KEY_HOME], b, image_size_percent=image_size)
#         self.add_component(self.home_button)
#         self.menu_buttons.append(self.home_button)
        
#         if language_url == None:
#             constr = layout.get_next_constraints()
#             self.abc_button = self.factory.create_button(IMAGE_ABC, KEY_SETUP, constr, listeners[GO_USER_HOME], b, image_size_percent=image_size)
#             self.add_component(self.abc_button)
#             self.menu_buttons.append(self.abc_button)
        
#         constr = layout.get_next_constraints()
#         self.new_books_button = self.factory.create_button(IMAGE_NEW_BOOKS, KEY_MENU, constr, listeners[GO_ROOT], b, image_size_percent=image_size)
#         self.add_component(self.new_books_button)
#         self.menu_buttons.append(self.new_books_button)

#         if language_url == None or language_url == "": # English-USA or Russian
#             constr = layout.get_next_constraints()
#             self.genre_button = self.factory.create_button(IMAGE_BOOK_GENRE, KEY_ROOT, constr, listeners[GO_TO_PARENT], b, image_size_percent=image_size)
#             self.add_component(self.genre_button)
#             self.menu_buttons.append(self.genre_button)
        
#         constr = layout.get_next_constraints()
#         self.player_button = self.factory.create_button(IMAGE_PLAYER, KEY_PLAY_PAUSE, constr, listeners[GO_PLAYER], b, source=BOOK_NAVIGATOR, image_size_percent=image_size)
#         self.add_component(self.player_button)
#         self.menu_buttons.append(self.player_button)

#         constr = layout.get_next_constraints()
#         self.back_button = self.factory.create_button(KEY_BACK, KEY_BACK, constr, None, b, source=BOOK_NAVIGATOR_BACK, image_size_percent=image_size)
#         self.back_button.add_release_listener(listeners[GO_BACK])
#         try:
#             self.back_button.add_release_listener(listeners[KEY_PLAY_FILE])
#         except:
#             pass
#         self.add_component(self.back_button)
#         self.menu_buttons.append(self.back_button)

#         constr = arrow_layout.RIGHT
#         self.right_button = self.factory.create_page_up_button(constr, "0", 34, 100)
#         self.right_button.add_release_listener(listeners[GO_RIGHT_PAGE])
#         self.add_component(self.right_button)
#         self.menu_buttons.append(self.right_button)

#     def set_parent_screen(self, scr):
#         """ Add parent screen

#         :param scr: parent screen
#         """
#         self.left_button.parent_screen = scr
#         self.right_button.parent_screen = scr
#         self.home_button.parent_screen = scr
#         self.new_books_button.parent_screen = scr
#         self.player_button.parent_screen = scr
#         self.back_button.parent_screen = scr

#         if hasattr(self, "abc_button"):
#             self.abc_button.parent_screen = scr
#         if hasattr(self, "genre_button"):
#             self.genre_button.parent_screen = scr

#     def add_observers(self, update_observer, redraw_observer):
#         """ Add screen observers
        
#         :param update_observer: observer for updating the screen
#         :param redraw_observer: observer to redraw the whole screen
#         """
#         self.add_button_observers(self.left_button, update_observer, redraw_observer)
#         self.add_button_observers(self.right_button, update_observer, redraw_observer)
#         self.add_button_observers(self.home_button, update_observer, redraw_observer, release=False)
#         self.add_button_observers(self.new_books_button, update_observer, redraw_observer)
#         self.add_button_observers(self.player_button, update_observer, redraw_observer)
#         self.add_button_observers(self.back_button, update_observer, redraw_observer, release=False)
                
#         if getattr(self, "abc_button", None):
#             self.add_button_observers(self.abc_button, update_observer, redraw_observer)
            
#         if getattr(self, "genre_button", None):
#             self.add_button_observers(self.genre_button, update_observer, redraw_observer)


