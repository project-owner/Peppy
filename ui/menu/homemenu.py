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
from player.proxy import MPD
from util.cdutil import CdUtil
from util.keys import LINUX_PLATFORM, V_ALIGN_TOP
from util.config import USAGE, USE_VOICE_ASSISTANT, HOME_MENU, RADIO, AUDIO_FILES, \
    CURRENT, MODE, NAME, AUDIOBOOKS, STREAM, CD_PLAYER, AUDIO, PLAYER_NAME

class HomeMenu(Menu):
    """ Home Menu class. Extends base Menu class """
    
    def __init__(self, util, bgr=None, bounding_box=None, font_size=None):
        """ Initializer
        
        :param util: utility object
        :param bgr: menu background
        :param bounding_box: bounding box
        """   
        self.factory = Factory(util)
        self.config = util.config
        m = self.factory.create_home_menu_button
        Menu.__init__(self, util, bgr, bounding_box, None, None, create_item_method=m, font_size=font_size)
        cdutil = CdUtil(util)
        
        items = []
        disabled_items = []
        
        if self.config[HOME_MENU][RADIO]: 
            items.append(RADIO)
            if not util.is_radio_enabled() or not util.connected_to_internet:
                disabled_items.append(RADIO)
                
        if self.config[HOME_MENU][AUDIO_FILES]: 
            items.append(AUDIO_FILES)
            
        if self.config[HOME_MENU][AUDIOBOOKS]: 
            items.append(AUDIOBOOKS)
            if not util.is_audiobooks_enabled() or not util.connected_to_internet:
                disabled_items.append(AUDIOBOOKS)
                
        if self.config[HOME_MENU][STREAM]:
            items.append(STREAM)
            if not util.connected_to_internet:
                disabled_items.append(STREAM)
                
        if self.config[HOME_MENU][CD_PLAYER]: 
            cd_drives_info = cdutil.get_cd_drives_info()
            player = self.config[AUDIO][PLAYER_NAME]
            if len(cd_drives_info) == 0:
                disabled_items.append(CD_PLAYER)
            items.append(CD_PLAYER)
        
        l = self.get_layout(items)
        bounding_box = l.get_next_constraints()
        self.modes = util.load_menu(items, NAME, disabled_items, V_ALIGN_TOP, bb=bounding_box, scale=0.5)
        va_commands = self.util.get_voice_commands()
        
        if self.config[USAGE][USE_VOICE_ASSISTANT]:
            if self.config[HOME_MENU][RADIO]:
                r = [va_commands["VA_RADIO"].strip(), va_commands["VA_GO_RADIO"].strip()]
                self.modes[RADIO].voice_commands = r            
            if self.config[HOME_MENU][AUDIO_FILES]:
                f = [va_commands["VA_FILES"].strip(), va_commands["VA_GO_FILES"].strip(), va_commands["VA_AUDIO_FILES"].strip()]
                self.modes[AUDIO_FILES].voice_commands = f
            if self.config[HOME_MENU][AUDIOBOOKS]:    
                a = [va_commands["VA_AUDIOBOOKS"].strip(), va_commands["VA_BOOKS"].strip(), va_commands["VA_GO_BOOKS"].strip()]
                self.modes[AUDIOBOOKS].voice_commands = a
            if self.config[HOME_MENU][STREAM]:    
                s = [va_commands["VA_STREAM"].strip(), va_commands["VA_GO_STREAM"].strip()]
                self.modes[STREAM].voice_commands = s
            if self.config[HOME_MENU][CD_PLAYER]:    
                s = [va_commands["VA_CD_PLAYER"].strip()]
                self.modes[STREAM].voice_commands = s
            
        if not items:
            return
        
        if not self.config[CURRENT][MODE]:
            for i in items:
                if i not in disabled_items:            
                    mode = i
                    break            
        else:
            mode = self.config[CURRENT][MODE]
        
        self.set_items(self.modes, 0, self.change_mode, False)
        self.current_mode = self.modes[mode.lower()]
        self.item_selected(self.current_mode) 
    
    def change_mode(self, state):
        """ Change mode event listener
        
        :param state: button state
        """
        if not self.visible:
            return
        state.previous_mode = self.current_mode.name
        self.current_mode = state
        self.config[CURRENT][MODE] = state.name
        self.notify_listeners(state)
