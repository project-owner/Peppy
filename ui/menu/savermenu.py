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
from util.keys import GENRE, V_ALIGN_TOP
from util.config import USAGE, USE_VOICE_ASSISTANT, SCREENSAVER_MENU, CLOCK, LOGO, \
    SLIDESHOW, VUMETER, SCREENSAVER, NAME, WEATHER

class SaverMenu(Menu):
    """ Screensaver Menu class. Extends base Menu class """
    
    def __init__(self, util, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """
        self.factory = Factory(util)
        m = self.factory.create_saver_menu_button
        Menu.__init__(self, util, bgr, bounding_box, 1, None, create_item_method=m)
        self.config = util.config
        
        items = []
        if self.config[SCREENSAVER_MENU][CLOCK]: items.append(CLOCK)
        if self.config[SCREENSAVER_MENU][LOGO]: items.append(LOGO)
        if self.config[SCREENSAVER_MENU][SLIDESHOW]: items.append(SLIDESHOW)
        if self.config[SCREENSAVER_MENU][VUMETER]: items.append(VUMETER)
        if self.config[SCREENSAVER_MENU][WEATHER]: items.append(WEATHER)
        
        current_saver_name = items[0]
        for s in items:
            if s == self.config[SCREENSAVER][NAME]:
                current_saver_name = s
                break
        
        self.savers = util.load_menu(items, GENRE, v_align=V_ALIGN_TOP)
        
        if self.config[USAGE][USE_VOICE_ASSISTANT]:
            voice_commands = util.get_voice_commands()
            self.savers[CLOCK].voice_commands = [voice_commands["VA_CLOCK"].strip()]
            self.savers[LOGO].voice_commands = [voice_commands["VA_LOGO"].strip()]
            self.savers[SLIDESHOW].voice_commands = [voice_commands["VA_SLIDESHOW"].strip()]
            self.savers[VUMETER].voice_commands = [voice_commands["VA_INDICATOR"].strip()]
            self.savers[WEATHER].voice_commands = [voice_commands["VA_WEATHER"].strip()]
        
        self.set_items(self.savers, 0, self.change_saver, False)
        self.current_saver = self.savers[current_saver_name]
        self.item_selected(self.current_saver)
        
    def get_saver_by_index(self, index):
        """ Return screensaver specified by its index
        
        :param index: screensaver index in the map of screensavers
        
        :return: screensaver
        """
        return self.savers[index]

    def change_saver(self, state):
        """ Change screensaver event listener
        
        :param state: button state
        """
        if not self.visible:
            return
        
        self.config[SCREENSAVER][NAME] = state.name        
        self.notify_listeners(state)
        