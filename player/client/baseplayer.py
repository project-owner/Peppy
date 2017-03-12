# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
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

from player.client.player import Player
from threading import RLock

class BasePlayer(Player):
    """ This class extends abstract Player class and serves as a parent 
    for all players providing base implementation.  
    """ 
    lock = RLock()
    
    def __init__(self):
        """ Initializer. """ 
        
        self.items = None
        self.current_track = None
        self.linux = None
        self.volume_listeners = [] 
        self.player_listeners = []
        self.end_of_track_listeners = []
        self.playing = True  
    
    def set_file_util(self, file_util):
        """ File utility setter 
                
        :param file_util: reference to file utility
        """ 
        self.file_util = file_util
    
    def set_volume(self, volume):
        """ Volume setter 
                
        :param volume: volume to set
        """        
        pass
    
    def get_volume(self):
        """ Volume getter """
        
        pass
        
    def play(self):
        """ Start playback """
                
        pass
    
    def play_pause(self):
        """ Play/Pause playback """
                
        pass
    
    def mute(self):
        """ Mute """
                
        pass
    
    def stop(self):
        """ Stop playback """
                
        pass
        
    def add_volume_listener(self, listener):
        """ Add volume listener 
        
        :param listener: volume event listener
        """ 
        with self.lock:
            if listener not in self.volume_listeners: 
                self.volume_listeners.append(listener)
     
    def remove_volume_listener(self, listener):
        """ Remove volume listener
        
        :param listener: volume event listener
        """        
        with self.lock:
            if listener in self.volume_listeners: 
                self.volume_listeners.remove(listener)
     
    def add_player_listener(self, listener):
        """ Add player status listener
        
        :param listener: player status listener
        """
        with self.lock:
            if listener not in self.player_listeners: 
                self.player_listeners.append(listener)
     
    def remove_player_listener(self, listener):
        """ Remove player status listener
        
        :param listener: player status listener
        """
        with self.lock:
            if listener in self.player_listeners: 
                self.player_listeners.remove(listener)
     
    def notify_volume_listeners(self, volume):
        """ Notify volume listeners about new volume level
        
        :param volume: new volume level 
        """
        for listener in self.volume_listeners:
            listener(volume)
             
    def notify_player_listeners(self, status):
        """ Notify player listeners about new player event
        
        :param status: player status 
        """
        for listener in self.player_listeners:
            listener(status)

    def add_end_of_track_listener(self, listener):
        """ Add end of track listener 
        
        :param listener: end of track event listener
        """ 
        with self.lock:
            if listener not in self.end_of_track_listeners: 
                self.end_of_track_listeners.append(listener)
                
    def remove_end_of_track_listener(self, listener):
        """ Remove end of track listener
        
        :param listener: end of track listener
        """
        with self.lock:
            if listener in self.end_of_track_listeners: 
                self.end_of_track_listeners.remove(listener)
    
    def notify_end_of_track_listeners(self):
        """ Notify end of track listeners """
        
        for listener in self.end_of_track_listeners:
            listener()


