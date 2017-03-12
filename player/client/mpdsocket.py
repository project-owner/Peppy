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

import threading
import os

from player.client.baseplayer import BasePlayer
from player.client.mpdconnection import MpdConnection
from player.client.mpdcommands import CLEAR, ADD, PLAY, STOP, PAUSE, RESUME, \
    SET_VOLUME, GET_VOLUME, MUTE_2, STATUS, CURRENT_SONG, IDLE, SEEKCUR, LOAD_PLAYLIST, PLAYLIST
from player.client.player import Player
from util.fileutil import FILE_PLAYLIST, FILE_AUDIO

class Mpdsocket(BasePlayer):
    """ This class extends base player and provides communication with MPD process using TCP/IP socket """
        
    def __init__(self):
        """ Initializer. Starts separate thread for listening MPD events """
        
        BasePlayer.__init__(self);  
        self.host = "localhost"
        self.port = 6600
        self.mute_flag = False
        self.volume_listeners = [] 
        self.player_listeners = []
        self.playing = True
        self.conn = None
        self.end_of_track_listeners = []
        self.dont_parse_track_name = False
    
    def set_proxy(self, proxy):
        """ mpd socket client doesn't use proxy """
        
        pass
    
    def start_client(self):
        """ Start client thread """
        
        self.conn = MpdConnection(self.host, self.port)
        self.conn.connect()
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
            
            if not "player" in line:
                continue
                
            volume = self.get_volume()
            self.notify_volume_listeners(volume)
            current = self.current()
            current_title = None
            
            try:
                current_title = current["Title"]
            except:
                pass
                
            if not current_title:
                try:
                    if not self.dont_parse_track_name:
                        current_title = current["file"]
                        tokens = current_title.split("/")
                        current_title = tokens[len(tokens) - 1]
                except:
                    pass
                
            if current_title:
                current_title = current_title.strip()
                current["current_title"] = current_title
                try:                    
                    track_time = self.status()["time"].replace(":", ".")
                    current["seek_time"] = track_time
                except:
                    pass
                status = self.status()
                try:
                    current["state"] = status["state"]
                except:
                    pass
                current["source"] = "player"
                self.notify_player_listeners(current)
            else:
                self.notify_end_of_track_listeners()
            
    def play(self, state):
        """ Start playing specified track/station. First it cleans the playlist 
        then adds new track/station to the list and then starts playback
        
        :param state: button state which contains the track/station info
        """        
        s = getattr(state, "playback_mode", None)
        if s and s == FILE_PLAYLIST:
            self.conn.command(PLAY + str(state.playlist_track_number))
            self.mode = FILE_PLAYLIST
            return 
        
        self.mode = FILE_AUDIO
        url = getattr(state, "url", None)
        if url == None: return

        if getattr(state, "file_name", None):
            self.dont_parse_track_name = False
            url = self.get_url(state)
        else:
            self.dont_parse_track_name = True
        
        self.conn.command(CLEAR)
        self.current_url = url
        self.conn.command(ADD + url) 
        self.conn.command(PLAY + '0')
        track_time = getattr(state, "track_time", "0")        
        
        if getattr(state, "file_name", None) and track_time:
            track_time = track_time.replace(":", ".")
            self.seek(track_time)                    
    
    def get_url(self, state):
        """ Creates track URL using folder and file name 
        
        :param state: state object
        :return: track URL
        """
        folder = state.folder
        
        if state.music_folder:
            folder = state.folder[len(state.music_folder):]
            
        if folder:
            folder += os.sep
        url = "\"" + folder + state.file_name + "\""
        return url.replace("\\", "/")
    
    def stop(self):
        """ Stop playback """
        
        self.conn.command(STOP)
    
    def seek(self, time):
        """ Jump to the specified position in the track
        
        :param time: time position in track
        """
        with self.lock:
            self.conn.command(SEEKCUR + time)
    
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
        with self.lock:
            self.conn.command(SET_VOLUME + str(level))        
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
            self.conn.command(SET_VOLUME + " " + str(self.current_volume_level))
        
    def status(self):
        """ Return the result of the STATUS command """
        
        with self.lock:
            return self.conn.read_dictionary(STATUS)
        
    def current(self):
        """ Return the current song """
        
        with self.lock:
            return self.conn.read_dictionary(CURRENT_SONG)

    def shutdown(self):
        """ Shutdown the player """
        
        self.playing = False
        
    def get_current_track_time(self):
        """  Return current track time
        
        :return: current track time
        """
        s = self.status()
        t = None
        try:
            t = s[Player.TIME]
        except:
            pass
        return t
    
    def get_current_playlist(self):
        """  Return current playlist
        
        :return: current playlist
        """
        d = self.conn.read_dictionary(PLAYLIST)
        d = {int(k):v for k,v in d.items()}
        playlist = []
        for key in sorted(d):
            val = d[key]
            playlist.append(val)
        return playlist
        
    def load_playlist(self, state):
        """  Load new playlist
        
        :param state: state object defining playlist location
        :return: new playlist
        """
        self.conn.command(CLEAR)
        self.conn.command(LOAD_PLAYLIST + self.get_url(state))
        return self.get_current_playlist()
    
    def notify_end_of_track_listeners(self):
        """  Notify end of track listeners. Starts new thread to unblock player loop. """
        
        thread = threading.Thread(target = self.handle_eof)
        thread.start()
            
    def handle_eof(self):
        """  End of track notifier. Runs in separate thread. """ 
        
        for listener in self.end_of_track_listeners:
            listener()
    