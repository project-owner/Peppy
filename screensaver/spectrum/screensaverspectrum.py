# Copyright 2022 PeppyMeter peppy.player@gmail.com
# 
# This file is part of PeppyMeter.
# 
# PeppyMeter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PeppyMeter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PeppyMeter. If not, see <http://www.gnu.org/licenses/>.

class ScreensaverSpectrum():
    """ Parent class for spectrum plug-in """
    
    def __init__(self, name, util, plugin_folder):
        """ Initializer """ 

        self.name = name
        self.util = util
        self.plugin_folder = plugin_folder   
        self.update_period = 1
        self.ready = True

        if util != None:
            bgr = util.config["background"]["screen.bgr.color"]
            self.bg = util.get_background(name, bgr)
            self.bgr_type = self.bg[0]
            self.bgr = self.bg[1]
            self.bgr_key = self.bg[5]
        
    def get_update_period(self):
        """ Return screensaver update period """
                      
        return self.update_period
    
    def set_image(self, image):
        """ Set station image. The method can be used by plug-ins which use station logo images 
        
        :param image: station logo image
        """
        pass
    
    def set_image_folder(self, state):
        """ Set image folder. 
        
        :param: state object defining image folder
        """
        pass
    
    def set_volume(self, volume):
        """ Set volume level. The method can be used by plug-ins which use volume level 
        
        :param volume: new volume level
        """
        pass
    
    def set_song_info(self, song_info):
        """ Set song info which consists of artist name and song name 
        
        :param song_info: song info
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

    def is_ready(self):
        """ Check if screensaver is ready """

        return self.ready
