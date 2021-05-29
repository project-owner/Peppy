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

import os
import urllib

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
        self.playlist = None
        self.cd_tracks = None
        self.cd_track_id = None
        self.cd_drive_name = None
        self.player_mode = None
        self.file_util = None
        self.util = None
        self.state = None
        self.enabled = True
        self.player_volume_control = True
    
    def set_util(self, util):
        """ Utility setter 
                
        :param util: reference to utility object
        """ 
        self.util = util
        self.file_util = util.file_util
    
    def set_player_volume_control(self, flag):
        """ Player Volume Control type setter

        :param volume: True - player volume cotrol type, False - amixer or hardware volume control type
        """
        self.player_volume_control = flag

    def set_volume(self, volume):
        """ Volume setter 
                
        :param volume: volume to set
        """        
        pass
    
    def get_url(self, state):
        """ Creates track URL using folder and file name 
        
        :param state: state object
        :return: track URL
        """
        folder = state.folder
        
        if hasattr(state, "music_folder"):
            folder = state.folder[len(state.music_folder):]
            
        if folder:
            folder += os.sep
        url = "\"" + folder + state.file_name + "\""
        return url.replace("\\", "/")
    
    def get_volume(self):
        """ Volume getter """
        
        pass
        
    def play(self, state=None):
        """ Start playback 
        
        :param state: state object
        """
        pass
    
    def pause(self):
        """ Pause playback """
                
        pass
    
    def play_pause(self, pause_flag=None):
        """ Play/Pause playback 
        
        :param pause_flag: play/pause flag
        """    
        pass
    
    def mute(self):
        """ Mute """
                
        pass
    
    def stop(self):
        """ Stop playback """
                
        pass
    
    def load_playlist(self, state):
        """ Load playlist
        
        :param state:
        """
        if state.file_name.endswith(".cue"):
            return
        self.stop()
        url = state.folder + os.sep + state.file_name
        self.playlist_path = url
        self.playlist = self.file_util.get_m3u_playlist(url)
        return self.playlist
    
    def get_seconds_from_string(self, s):
        """ Convert string to seconds
        
        :param s: string in format HH:MM:SS
        """                                                                       
        if s == '0':
            return 0

        nums = s.split(":");
        result = 0;
        
        if len(nums) == 3:
            result = (int(nums[0]) * 3600) + (int(nums[1]) * 60) + (int(nums[2]));
        elif len(nums) == 2:
            result = (int(nums[0]) * 60) + (int(nums[1]));
        
        return result;
    
    def encode_url(self, url):
        """ Encode URL using ascii encoding. If doesn't work use UTF-8 encoding
        
        :param url: input URL
        :return: encoded URL
        """        
        try:
            url.encode('ascii')
            url = url.replace(" ", "%20")
            url = url.replace("_", "%5F")
            return url
        except:
            pass
        
        new_url = url.encode('utf-8')
        new_url = urllib.parse.quote(new_url)
        new_url = new_url.replace("%22", "\"")
        new_url = new_url.replace("%3A", ":")
        new_url = new_url.replace("%25", "%")
        
        return new_url
    
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
        if not self.enabled:
            return

        for listener in self.volume_listeners:
            listener(volume)
             
    def notify_player_listeners(self, status):
        """ Notify player listeners about new player event
        
        :param status: player status 
        """
        if not self.enabled:
            return
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
    
    def notify_end_of_track_listeners(self, args=None):
        """ Notify end of track listeners 
        
        :param args: arguments
        """
        if not self.enabled:
            return

        for listener in self.end_of_track_listeners:
            listener()            

    def resume_playback(self):
        """ Resume stopped playback """

        self.play(None)

    def start_client(self):
        """ Start player client """

        pass

    def stop_client(self):
        """ Stop player client """

        pass
