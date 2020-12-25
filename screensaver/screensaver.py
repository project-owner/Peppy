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

from configparser import ConfigParser
from util.util import PACKAGE_SCREENSAVER
from util.config import BACKGROUND, WEB_BGR_COLOR, SCREEN_BGR_COLOR

PLUGIN_CONFIG_FILENAME = "screensaver-config.txt"
PLUGIN_CONFIGURATION = "Plugin Configuration"
UPDATE_PERIOD = "update.period"

class Screensaver():
    """ Parent class for all screensaver plug-ins """
    
    def __init__(self, name, util, plugin_folder, has_exit_area=False):
        """ Initializer. The default update period = 1 second 
        
        :param name: plugin name
        :param util: utility object
        :param plugin_folder: plugin folder
        :param has_exit_area: if present only clicking in the exit area will close the screensaver
        """
        self.plugin_config_file = ConfigParser()
        path = os.path.join(os.getcwd(), PACKAGE_SCREENSAVER, plugin_folder, PLUGIN_CONFIG_FILENAME)
        self.plugin_config_file.read(path)
        self.update_period = self.plugin_config_file.getint(PLUGIN_CONFIGURATION, UPDATE_PERIOD)
        self.has_exit_area = has_exit_area

        bgr = util.config[BACKGROUND][SCREEN_BGR_COLOR]
        self.bg = util.get_background(name, bgr)
        self.bgr_type = self.bg[0]
        self.bgr = self.bg[1]
        self.bgr_key = self.bg[5]
        
    def get_update_period(self):
        """ Return screensaver update period """
                      
        return self.update_period
    
    def set_image(self, image):
        """ Set station image. The method can be used by plug-ins which use images 
        
        :param image: image
        """
        pass
    
    def set_image_folder(self, state):
        """ Set image folder. 
        
        :param: state object defining image folder
        """
        pass
    
    def set_song_info(self, song_info):
        """ Set song info which consists of artist name and song name 
        
        :param song_info: song info
        """
        pass
    
    def set_volume(self, volume):
        """ Set volume level. The method can be used by plug-ins which use volume level 
        
        :param volume: new volume level
        """
        pass
    
    def refresh(self):
        """ Refresh the screensaver. Used for animation """
        
        pass
    
    def start(self):
        """ Start screensaver """
        
        pass
    
    def stop(self):
        """ Stop screensaver """
        
        pass

    def is_exit_clicked(self):
        """ Check that exit area was clicked """
        
        pass