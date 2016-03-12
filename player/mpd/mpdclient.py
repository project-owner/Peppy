# Copyright 2016 Peppy Player peppy.player@gmail.com
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

import threading

from player.mpd.mpdconnection import MpdConnection
from player.mpd.mpdproxy import CLEAR, ADD, PLAY, STOP, PAUSE, RESUME, \
    SET_VOLUME_2, GET_VOLUME, MUTE_2, STATUS, CURRENT_SONG, IDLE
from player.player import Player

class MpdClient(Player):
    """
    Communicate with MPD process directly using TCP/IP socket.
    Due to some weird timeout issue it's not used right now.
    """    
    lock = threading.RLock()
    def __init__(self, host, port):
        """ Initializer. Starts separate thread for listening MPD events.
        :param host: host where MPD process is running
        :param port: port to which MPD process is listening to
        """
        self.host = host
        self.port = port
        self.conn = MpdConnection(host, port)
        self.mute_flag = False
        self.volume_listeners = [] 
        self.player_listeners = []
        self.playing = True        
        thread = threading.Thread(target = self.mpd_event_listener)
        thread.start()
    
    def mpd_event_listener(self):
        """ Starts the loop for listening MPD events """
                
        while self.playing:
            c = MpdConnection(self.host, self.port, reader_flags='r', encoding=None)
            c.connect()
            if not c.writer:
                continue
            c.writer.write(IDLE + "\n")
            c.writer.flush()
            line = None
            try:        
                line = c.reader.readline() # blocking line
            except:
                break
            if "player" in line:
                volume = self.get_volume()
                self.notify_volume_listeners(volume)
                current = self.current()
                current_title = None
                try:
                    current_title = current["Title"]
                except:
                    pass
                if current_title:
                    self.notify_player_listeners(current_title)                
    
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
        """ Notify player listeners about player status change
        :param volume: new player status 
        """
        for listener in self.player_listeners:
            listener(status)
    
    def play(self, state):
        """ Start playing specified station. First it cleans the playlist 
        then adds new station to the list and then starts playing that station
        :param state: button state which cantains the station to play
        """
        self.conn.command(CLEAR)
        self.conn.command(ADD + state.url)
        self.conn.command(PLAY + '0')
        
    def stop(self):
        """ Stop playback """
        
        self.conn.command(STOP)
    
    def play_pause(self):
        """ Play/pause playback """
        status = self.status()
        state = status.get(Player.STATE)
        
        if state is not Player.PAUSED:
            self.conn.command(PAUSE)
        else:
            self.conn.command(RESUME) 
    
    def set_volume(self, level):
        """ Set volume level
        :param level: new volume level
        """
        self.conn.command(SET_VOLUME_2 + str(level))        
        if self.mute_flag:
            self.mute_flag = False
    
    def get_volume(self):
        """  Return current volume level 
        :return: volume level or -1 if not available
        """
        with self.lock:
            st = self.status()
            volume = '-1'
            
            try:
                volume = st[GET_VOLUME]
            except KeyError:
                pass
            
            return int(volume)
    
    def mute(self):
        """ Mute """
        
        self.mute_flag = not self.mute_flag
        
        if self.mute_flag:
            self.current_volume_level = self.get_volume() 
            self.conn.command(MUTE_2)
        else:
            self.conn.command(SET_VOLUME_2 + " " + str(self.current_volume_level))
        
    def status(self):
        """ Return the result of the STATUS command """
        
        with self.lock:
            return self.conn.read_dictionary(STATUS)
        
    def current(self):
        """ Return the current song """
        
        with self.lock:
            return self.conn.read_dictionary(CURRENT_SONG)

    def shutdown(self):
        """ Shutdoen the player """
        
        self.playing = False