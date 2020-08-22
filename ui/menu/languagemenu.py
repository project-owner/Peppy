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

from ui.factory import Factory
from ui.menu.menu import Menu
from util.keys import KEY_LANGUAGES
from util.config import USAGE, USE_VOICE_ASSISTANT, CURRENT, LANGUAGE, NAME
from ui.layout.buttonlayout import TOP

ICON_LOCATION = TOP
BUTTON_PADDING = 5
ICON_AREA = 70
ICON_SIZE = 70
FONT_HEIGHT = 48

class LanguageMenu(Menu):
    """ Language Menu class. Extends base Menu class """
    
    def __init__(self, util, bgr=None, bounding_box=None):
        """ Initializer
        
        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """
        self.util = util
        self.factory = Factory(util)

        m = self.create_language_menu_button
        Menu.__init__(self, util, bgr, bounding_box, None, None, create_item_method=m)
        self.config = self.util.config
        language = self.config[CURRENT][LANGUAGE] 
        
        languages = self.config[KEY_LANGUAGES]
        layout = self.get_layout(languages)        
        button_rect = layout.constraints[0]
        image_box = self.factory.get_icon_bounding_box(button_rect, ICON_LOCATION, ICON_AREA, ICON_SIZE, BUTTON_PADDING)
        self.languages = self.util.load_languages_menu(image_box)

        label_area = (button_rect.h / 100) * (100 - ICON_AREA)
        self.font_size = int((label_area / 100) * FONT_HEIGHT)

        self.set_items(self.languages, 0, self.change_language, False)
        self.current_language = self.languages[language]
        self.item_selected(self.current_language)

    def create_language_menu_button(self, s, constr, action, scale, font_size):
        """ Create Language Menu button

        :param s: button state
        :param constr: scaling constraints
        :param action: button event listener
        :param scale: True - scale images, False - don't scale images

        :return: language menu button
        """
        s.padding = BUTTON_PADDING
        s.image_area_percent = ICON_AREA

        return self.factory.create_menu_button(s, constr, action, scale, font_size=font_size)

    def set_voice_commands(self, language):
        """ Set menu voice commands

        :param language: new language
        """
        if not self.config[USAGE][USE_VOICE_ASSISTANT]:
            return

        va_commands = self.util.get_va_language_commands()
        for k, v in self.languages.items():
            v.voice_commands = va_commands[k]
    
    def change_language(self, state):
        """ Change language event listener
        
        :param state: button state
        """
        if not self.visible:
            return
        self.set_voice_commands(state.name)      
        self.notify_listeners(state)
