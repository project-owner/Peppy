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
import logging
import codecs
import time
import os

from player.client.baseplayer import BasePlayer
from player.client.mplayercommands import *

class Mplayer(BasePlayer):
    """ This class extends abstract Player and implements its methods. 
    It serves as a wrapper for 'mplayer' process 
    """    
    def __init__(self):
        """ Initializer. Starts new thread which listens to the player events """
        
        BasePlayer.__init__(self);
        self.items = None
        self.current_track = None
        self.volume = None
        self.current_url = None
        self.proxy = None
        self.seek_time = None
    
    def set_proxy(self, proxy):
        """ Set proxy process. 
        
        :param proxy: reference to the proxy process
        """
        self.proxy = proxy 
    
    def start_client(self):
        """ This method starts new thread for listening mplayer events """
                
        thread = threading.Thread(target = self.mplayer_event_listener)
        thread.start()
    
    def mplayer_event_listener(self):
        """ The communication with mplayer process done through stdin and stdout pipes.
        Commands are sent to stdin pipe and messages are retrieved from the stdout pipe.
        Empty pipe causes thread blocking. New message in the pipe unblock the thread.
        The message should contain either 'ICY Info:' or 'ANS_volume'. All other messages 
        are ignored. Upon new message all corresponding listeners will be notified.
        There are two types of listeners which will be notified:
        - volume listeners - notified when volume changes
        - player listeners - notified when player status changes (e.g. song title changes)
        """               
        self.proxy.stdout = codecs.getwriter("utf-8")(self.proxy.stdout.detach())
        duration = None
        current_title = None
        
        while self.playing:
            try:       
                line = self.proxy.stdout.readline().decode("UTF-8").rstrip()
                logging.debug(str(line))                
                try:
                    if self.volume_listeners:
                        self.get_volume()
                except:
                    pass
                
                if ICY_INFO in line:
                    current_title = line.split("'")[1]
                    if len(current_title) > 0:
                        self.notify_player_listeners(current_title)
                elif ANS_FILENAME in line:
                    current_title = line.split("=")[1]
                elif ANS_LENGTH in line:
                    duration = line.split("=")[1]
                    if duration and self.seek_time:
                        state = {}
                        state["Time"] = duration
                        state["seek_time"] = self.seek_time
                        state["state"] = "playing"
                        state["current_title"] = current_title
                        self.notify_player_listeners(state)
                        self.seek_time = None                        
                elif ANS_TIME_POSITION in line:
                    self.seek_time = line.split("=")[1]
                    state = {}
                    state["state"] = "playing"
                    state["seek_time"] = self.seek_time
                    state["current_title"] = current_title
                    self.notify_player_listeners(state)              
                elif EOF in line:
                    self.notify_end_of_track_listeners()
                elif ANS_VOLUME in line:
                    volume = float(line.split("=")[1])
                    self.notify_volume_listeners(volume)
                elif STARTING_PLAYBACK in line:
                    self.get_current_track_time()
                    self.call(GET_FILENAME)
                    self.call(GET_LENGTH)
                    
            except Exception as e:
                logging.debug(str(e))
    
    def get_track_index(self, track):
        if not self.playlist:
            return -1
        for i, v in enumerate(self.playlist):
            if track == v:
                return i
        return -1
    
    def call(self, arg):
        """ Call mplayer process with specified arguments
        
        :param args: arguments for call
        """        
        try:
            self.proxy.stdin.write(arg)
            self.proxy.stdin.write("\n")
            self.proxy.stdin.flush()
        except Exception as e:
            logging.debug(str(e))        
        
    def get_volume(self):
        """  Issues 'get_property volume' command. The result will be handled in the player thread """
        
        with self.lock:
            self.call(GET_VOLUME)
        
    def set_volume(self, level):
        """ Set volume level
        
        :param level: new volume level
        """
        with self.lock:
            self.call(VOLUME + str(level) + " 100")
    
    def mute(self):
        """ Mute """
        
        self.call(MUTE)
    
    def play(self, state):
        s = state.url
        filename = getattr(state, "file_name", None)
        
        if filename:
            s = s.replace('\\', '/')
            if not s.startswith("\"") and not s.endswith("\""):
                s = "\"" + s + "\""
                
        self.current_url = s
        command = LOAD_FILE + s
        logging.debug(command)
        self.call(command)
        
        if filename:
            track_time = getattr(state, "track_time", None)
            if track_time:
                track_time = track_time.replace(":", ".")
            else:
                track_time = "0.0"
            self.seek(track_time)
            self.call(GET_FILENAME)
            self.call(GET_LENGTH)
    
    def pause(self):
        """ Pause playback if playing. Resume playback if paused already """
           
        self.call(PAUSE)
    
    def play_pause(self):
        """ Play/pause playback """
        
        self.call(PAUSE)
    
    def stop(self, source=None):
        """ Stop playback """
        
        self.call(STOP)

    def shutdown(self):
        """ Shutdown the player and client """
        
        self.playing = False
        self.call(QUIT)
 
    def get_current_track_time(self):
        """ Return current track time
        
        :return: track time in seconds
        """
        self.call(GET_TRACK_TIME)
        time.sleep(0.3)
        return self.seek_time
    
    def seek(self, time):
        """ Set current track time
        
        :param time: new track time in seconds
        """
        with self.lock:
            command = SET_TRACK_TIME + time
            self.call(command)
            self.call(GET_TRACK_TIME)

    def load_playlist(self, state):
        """ Load playlist
        
        :Param state:
        """
        if state.file_name.endswith(".cue"):
            return
        self.stop()
        url = state.folder + os.sep + state.file_name
        self.playlist_path = url
        self.playlist = self.file_util.get_m3u_playlist(url)
        return self.playlist
        
