# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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
from util.config import USAGE, USE_VOICE_ASSISTANT, SCREENSAVER, DELAY, \
    KEY_SCREENSAVER_DELAY_1, KEY_SCREENSAVER_DELAY_3, KEY_SCREENSAVER_DELAY_OFF

FONT_HEIGHT = 40
ROWS = 1
COLUMNS = 3

class SaverDelayMenu(Menu):
    """ Screensaver Delay Menu class. Extends base Menu class """
    
    def __init__(self, util, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """
        self.factory = Factory(util)
        m = self.create_saver_delay_menu_button
        font_size = int((bounding_box.h / 100) * FONT_HEIGHT)
        Menu.__init__(self, util, bgr, bounding_box, ROWS, COLUMNS, create_item_method=m, font_size=font_size)
        self.config = util.config
        current_delay_name = self.config[SCREENSAVER][DELAY]
        self.delays = util.get_screensaver_delays()
        
        if self.config[USAGE][USE_VOICE_ASSISTANT]:
            voice_commands = util.get_voice_commands()
            self.delays[KEY_SCREENSAVER_DELAY_1].voice_commands = [voice_commands["VA_ONE_MINUTE"].strip()]
            self.delays[KEY_SCREENSAVER_DELAY_3].voice_commands = [voice_commands["VA_THREE_MINUTES"].strip()]
            self.delays[KEY_SCREENSAVER_DELAY_OFF].voice_commands = [voice_commands["VA_OFF"].strip()]
        
        self.set_items(self.delays, 0, self.change_delay, False)
        current_delay = self.delays[current_delay_name]
        self.item_selected(current_delay)

    def create_saver_delay_menu_button(self, s, constr, action, scale, font_size):
        """ Create Screensaver Delay Menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images

        :return: screensaver delay menu button
        """
        s.show_img = False

        return self.factory.create_menu_button(s, constr, action, scale, font_size=font_size)

    def change_delay(self, state):
        """ Change delay event listener
        
        :param state: button state
        """
        self.config[SCREENSAVER][DELAY] = state.name        
        self.notify_listeners(state)
        