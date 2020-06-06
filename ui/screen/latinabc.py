# Copyright 2019-2020 Peppy Player peppy.player@gmail.com
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
from ui.screen.screen import Screen, PERCENT_TOP_HEIGHT
from ui.menu.latinabcmenu import LatinAbcMenu
from util.util import KEY_HOME, KEY_PLAYER, KEY_PLAY_PAUSE, KEY_BACK, KEY_PARENT
from util.keys import KEY_CALLBACK
from util.config import COLLECTION, BACKGROUND, FOOTER_BGR_COLOR

IMAGE_SIZE_PERCENT = 60

class LatinAbcScreen(Screen):
    """ Ltin Alphabet Screen """
    
    def __init__(self, title, util, listeners, voice_assistant):
        """ Initializer
        
        :param title: screen title
        :param util: utility object
        :param listener: screen menu event listener
        :param voice_assistant: voice assistant
        """
        Screen.__init__(self, util, None, PERCENT_TOP_HEIGHT, voice_assistant)
        self.screen_title.set_text(title)
        self.factory = Factory(util)
        self.abc_menu = LatinAbcMenu(util, listeners[KEY_CALLBACK], (0, 0, 0, 0), self.layout.CENTER)
        self.abc_menu.add_listener(listeners[KEY_CALLBACK]) 
        self.add_menu(self.abc_menu)
        
        layout = GridLayout(self.layout.BOTTOM)
        layout.set_pixel_constraints(1, 4, 1, 0)
        layout.current_constraints = 0
        d = util.config[BACKGROUND][FOOTER_BGR_COLOR]
        
        self.navigator = Container(util)
        self.buttons = []
        self.add_button(KEY_HOME, KEY_HOME, layout, listeners[KEY_HOME], d)
        self.add_button(KEY_BACK, KEY_BACK, layout, listeners[KEY_BACK], d)
        self.add_button(COLLECTION, KEY_PARENT, layout, listeners[COLLECTION], d)
        self.add_button(KEY_PLAYER, KEY_PLAY_PAUSE, layout, listeners[KEY_PLAYER], d)
        self.add_menu(self.navigator)

    def add_button(self, img_name, key, layout, listener, bgr):
        """ Add button to the navigator

        :param img_name: button image name
        :param key: keyboard key
        :param layout: button layout
        :param listener: button listener
        :param bgr: background color
        """
        c = layout.get_next_constraints()
        b = self.factory.create_button(img_name, key, c, listener, bgr, image_size_percent=IMAGE_SIZE_PERCENT)
        b.parent_screen = self
        self.navigator.add_component(b)
        self.buttons.append(b)

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers
        
        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        Screen.add_screen_observers(self, update_observer, redraw_observer)
        
        self.abc_menu.add_menu_observers(update_observer, redraw_observer)
        for b in self.buttons:
            self.add_button_observers(b, update_observer, redraw_observer)
        