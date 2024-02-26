# Copyright 2018-2022 Peppy Player peppy.player@gmail.com
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

import time

from threading import Thread
from random import shuffle
from screensaver.screensaver import Screensaver, PLUGIN_CONFIGURATION
from util.config import CLOCK, LOGO, SLIDESHOW, VUMETER, WEATHER, SPECTRUM, LYRICS, RANDOM, PEXELS, MONITOR, STOCK, HOROSCOPE

class Random(Screensaver):
    """ Random screensaver plug-in. 
    Loads all savers defined in configuration file and starts them in random order
    The update period in seconds can be defined in the configuration file. 
    """    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """
        self.name = RANDOM
        self.util = util
        plugin_folder = type(self).__name__.lower() 
        Screensaver.__init__(self, self.name, util, plugin_folder)
        self.config = util.config
        
        self.current_image = None
        self.current_image_folder = None
        self.current_volume = None
        self.current_song_info = None

        s = self.plugin_config_file.get(PLUGIN_CONFIGURATION, "savers")
        if s == None or len(s.strip()) == 0:
            self.saver_names = [CLOCK, LOGO, SLIDESHOW, VUMETER, WEATHER, SPECTRUM, LYRICS, PEXELS, MONITOR, STOCK, HOROSCOPE]
        else:
            self.saver_names = s.split(",")
            self.saver_names = list(map(str.strip, self.saver_names))
        
        shuffle(self.saver_names)
        self.savers = {}
        for name in self.saver_names:
            self.savers[name] = self.util.load_screensaver(name)
        
        self.saver_num = 0
        self.current_saver = None
    
    def start(self):
        """ Start screensaver """
        
        self.run_thread = True
        thread = Thread(target=self.saver_thread)
        thread.start()
        
    def saver_thread(self):
        """ Saver thread """
        
        self.cycle_num = 0
        while self.run_thread:
            if self.current_saver != None:
                if self.cycle_num == self.current_saver_update_period:
                    self.current_saver.refresh()
                    self.cycle_num = 0
                else:
                    self.cycle_num += 1
            time.sleep(1)
    
    def stop(self):
        """ Stop screensaver """
        
        self.run_thread = False
        if self.current_saver != None:
            self.current_saver.stop()
            self.cycle_num = 0
    
    def set_image(self, image):
        """ Set station image. 
        
        :param image: image
        """
        self.current_image = image
        if self.current_saver != None:
            self.current_saver.set_image(self.current_image)
    
    def set_image_folder(self, state):
        """ Set image folder. 
        
        :param: state object defining image folder
        """
        self.current_image_folder = getattr(state, "cover_art_folder", None)
        if self.current_saver != None:
            self.current_saver.set_image_folder(self.current_image)
    
    def set_song_info(self, song_info):
        """ Set song info which consists of artist name and song name 
        
        :param song_info: song info
        """
        self.current_song_info = song_info
        if self.current_saver != None:
            self.current_saver.set_song_info(song_info)
    
    def set_volume(self, volume):
        """ Set volume level. 
        
        :param volume: new volume level
        """
        self.current_volume = volume
        if self.current_saver != None:
            self.current_saver.set_volume(volume)

    def update(self, area=None):
        """  Update screensaver """

        pass

    def refresh(self):
        """ Draw screensaver """
        
        if self.current_saver != None and len(self.saver_names) == 1:
            return

        a = None

        if self.current_saver != None:
            self.current_saver.stop()
        
        self.current_saver_name = self.saver_names[self.saver_num]
        self.current_saver = self.savers[self.current_saver_name]
        self.current_saver_update_period = self.current_saver.update_period
        self.current_saver.start_callback = self.start_callback
        
        try:
            self.current_saver.set_image(self.current_image)
            self.current_saver.set_volume(self.current_volume)
            self.current_saver.set_image_folder(self.current_image_folder)
            self.current_saver.set_song_info(self.current_song_info)
        except:
            pass
        
        self.current_saver.start()
        a = self.current_saver.refresh()
        self.cycle_num = 0

        if self.saver_num == len(self.saver_names) - 1:
            self.saver_num = 0
        else:
            self.saver_num += 1

        return a

    def set_visible(self, flag):
        """ Ignore """
        pass
