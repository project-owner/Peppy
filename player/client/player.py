# Copyright 2016-2023 Peppy Player peppy.player@gmail.com
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

from abc import ABCMeta, abstractmethod

class Player(metaclass=ABCMeta):
    """ Serve as interface and establish common API for different audio player implementations.
    So that all players (mpd etc.) would be controlled using the same API.
    """    
    STATE = "state"
    STOPPED = "stopped"
    PAUSED = "paused"
    PLAYING = "playing"
    VOLUME = "volume"
    TRACK = "track"
    TIME = "time"
    DURATION = "duration"

    FILENAME = "filename"
    FILESIZE = "filesize"
    CURRENT_TITLE = "current_title"
    CHANNELS = "channels"
    SAMPLE_RATE = "sample_rate"
    CODEC = "codec"
    GENRE = "genre"
    STATION = "station"
    BITS_PER_SAMPLE = "bits_per_sample"
    BITRATE = "bitrate"
    
    def __init__(self):
        """ Initialize player """
        
        pass               
    
    @abstractmethod
    def set_volume(self, volume):
        """ Volume setter 
                
        :param volume: volume to set
        """        
        pass
    
    @abstractmethod
    def get_volume(self):
        """ Volume getter """
        
        pass
        
    @abstractmethod
    def play(self):
        """ Start playback """
                
        pass
    
    @abstractmethod
    def pause(self):
        """ Pause playback """
        
        pass
    
    @abstractmethod
    def play_pause(self, pause_flag=None):
        """ Play/Pause playback 
        
        :param pause_flag: play/pause flag
        """
        pass
    
    @abstractmethod
    def mute(self):
        """ Mute """
                
        pass
    
    @abstractmethod
    def stop(self):
        """ Stop playback """
                
        pass
    
    @abstractmethod
    def add_volume_listener(self, listener):
        """ Add volume listener to the player
                
        :param listener: listener to add
        """
        pass
    
    @abstractmethod
    def remove_volume_listener(self, listener):
        """ Remove volume listener from the player
                 
        :param listener: listener to remove
        """
        pass

    @abstractmethod
    def notify_volume_listeners(self, volume):
        """ Notify volume listeners

        :param volume: volume level for notification
        """
        pass
    
    @abstractmethod
    def add_player_listener(self, listener):
        """ Add playback listener 
                
        :param listener: listener to add
        """
        pass
    
    @abstractmethod
    def remove_player_listener(self, listener):
        """ Remove playback listener
                 
        :param listener: listener to remove
        """
        pass
    
    @abstractmethod
    def notify_player_listeners(self, status):
        """ Notify playback listeners

        :param status: current player status for notification
        """
        pass

    @abstractmethod
    def add_title_listener(self, listener):
        """ Add metadata listener
                
        :param listener: listener to add
        """
        pass
    
    @abstractmethod
    def remove_title_listener(self, listener):
        """ Remove title listener
                 
        :param listener: listener to remove
        """
        pass

    @abstractmethod
    def notify_title_listeners(self, title):
        """ Notify title listeners

        :param title: current title
        """
        pass

    @abstractmethod
    def add_metadata_listener(self, listener):
        """ Add metadata listener

        :param listener: listener to add
        """
        pass

    @abstractmethod
    def remove_metadata_listener(self, listener):
        """ Remove metadata listener

        :param listener: listener to remove
        """
        pass

    @abstractmethod
    def notify_metadata_listeners(self, status):
        """ Notify metadata listeners

        :param status: current metadata for notification
        """
        pass
    
    @abstractmethod
    def shutdown(self):
        """ Shutdown the player gracefully """
                
        pass
    
    def set_platform(self, linux):
        """ Set platform flag 
        
        :param linux: True - current platform is Linux, False - Current platform is Windows
        """        
        self.linux = linux
        
    def set_player_mode(self, mode):
        """ Set playback mode 
        
        :param mode: mode identifier
        """        
        self.player_mode = mode

    @abstractmethod
    def get_current_track_time(self):
        """ Current track time getter """
        
        pass
    
    @abstractmethod
    def seek(self, time):
        """ Jump to the specified position in track
        
        :param time: time position in track
        """
        pass

    @abstractmethod
    def load_playlist(self, playlist):
        """ Load new playlist
        
        :param playlist: new playlist
        """
        pass

    @abstractmethod
    def get_current_playlist(self):
        """  Return current playlist
        
        :return: current playlist
        """
        pass

    @abstractmethod
    def add_end_of_track_listener(self, listener):
        """ Add end of track listener
        
        :param listener: end of track listener
        """
        pass
    
    @abstractmethod
    def remove_end_of_track_listener(self, listener):
        """ Remove end of track listener
        
        :param listener: end of track listener
        """
        pass
    
    @abstractmethod
    def notify_end_of_track_listeners(self, args=None):
        """ Notify end of track listeners 
        
        :param args: arguments
        """        
        pass

    @abstractmethod
    def resume_playback(self):
        """ Resume stopped playback """
        
        pass

    @abstractmethod
    def start_client(self):
        """ Start player client """

        pass

    @abstractmethod
    def stop_client(self):
        """ Stop player client """

        pass
