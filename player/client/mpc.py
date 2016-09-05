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

from player.client.player import Player
import subprocess
from subprocess import Popen, PIPE
import os
from player.client.mpdcommands import MPC, CLEAR, ADD, PLAY, STOP, PAUSE, RESUME, CURRENT,\
    SET_VOLUME_1, GET_VOLUME, MUTE_1, STATUS, IDLELOOP, PLAYER
import threading
import logging
import time

class Mpc(Player):
    """ This class extends abstract Player and implements its methods. 
    It serves as a wrapper for MPC process 
    """    
    lock = threading.RLock()
    use_shell = True
    
    def __init__(self):
        """ Initializer. Starts new thread which listens to the player events """ 
                       
        self.items = None
        self.current_track = None
        self.volume = None
        self.mute_flag = False
        self.volume_listeners = [] 
        self.player_listeners = []
        self.current_url = None
        self.playing = True       
    
    def set_platform(self, linux):
        """ Set platform flag 
        
        :param linux: True - current platform is Linux, False - Current platform is Windows
        """        
        self.linux = linux
    
    def set_proxy(self, proxy):
        """ mpc client doesn't use proxy """
        
        pass
    
    def start_client(self):
        """ This method starts new thread for listening MPC events """
                
        thread = threading.Thread(target = self.mpd_event_listener)
        thread.start()
    
    def mpd_event_listener(self):
        """ The communication with MPC process done through the pipe.
        Empty pipe causes thread blocking. New message in the pipe unblocks the thread.
        The message should contain 'player'. All other events are ignored. 
        Upon new message all corresponding listeners will be notified.
        There are two types of listeners which will be notified:
        - volume listeners - notified when volume changes
        - player listeners - notified when player status changes (e.g. song title changes)
        """                
        self.mpc_process = None
        while self.playing:
            if not self.mpc_process:
                try:
                    self.mpc_process = Popen([MPC.strip(), IDLELOOP], stdout=PIPE, universal_newlines=True)
                    time.sleep(0.2)                    
                except Exception as e:
                    logging.error(str(e))
            
            if not self.mpc_process:
                continue
            
            try:
                line1 = self.mpc_process.stdout.readline() # blocking line
                line2 = self.mpc_process.stdout.readline()
                if (line1 and (PLAYER in line1)) or (line2 and (PLAYER in line2)):
                    volume = self.get_volume()
                    self.notify_volume_listeners(volume)
                    current_title = self.current()
                    if current_title:
                        self.notify_player_listeners(current_title)
            except:
                self.mpc_process = None
    
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
    
    def call(self, arg):
        """ Call MPC process with specified arguments
        
        :param args: arguments for call
        """        
        try:
            subprocess.call(MPC + arg, shell=self.use_shell, stdout=subprocess.PIPE)
        except:
            pass
        
    def call_return(self, arg):
        """ Call MPC process with specified arguments, decode and return the output string
        
        :param args: arguments for call
        :return: string returned from MPC call
        """
        val = None
        try:
            val = subprocess.check_output(MPC + arg, shell=self.use_shell)
        except:
            pass
        
        if val:
            return val.decode(encoding='utf-8')
        else:
            return None
    
    def status(self):
        """ Call 'mpc status' command and parse the output
        
        :return: dictionary representing MPC status
        """        
        s = self.call_return(STATUS)
        
        if s == None:
            return None
        
        lines = s.split(os.linesep)
        d = {}
        line = lines[1]
        
        if line.startswith("ERROR"):
            return d
        
        if len(line) == 0:
            d[Player.STATE] = Player.STOPPED
            return d
        
        if Player.PAUSED in line:
            d[Player.STATE] = Player.PAUSED 
        elif Player.PLAYING in line:
            d[Player.STATE] = Player.PLAYING
        else:
            d[Player.STATE] = None
            
        d[Player.TRACK] = int(line[line.find("#") + 1 : line.find("/")])
        
        line = lines[2]
        v = line[8 : 10]
        if 'n/' not in v:
            d[Player.VOLUME] = int(v)
        
        return d  
        
    def current(self):
        """ Return info about current track
        
        :return: result of the command
        """
        s = self.call_return(CURRENT)
        if s and "http" not in s:
            if ": " in s:
                return s[s.find(": ") + 2:].rstrip()
            else:
                return s.rstrip()
        else:
            return None
    
    def get_volume(self):
        """  Return current volume level
         
        :return: volume level or -1 if not available
        """
        volume = self.call_return(GET_VOLUME)
        
        if volume:
            volume = volume[7:].strip()
            if volume == 'n/a':
                volume = -1
            else:
                volume = volume[:-1]
        return volume
    
    def set_volume(self, level):
        """ Set volume level
        
        :param level: new volume level
        """
        self.call(SET_VOLUME_1 + str(level))
        if self.mute_flag:
            self.mute_flag = False
    
    def mute(self):
        """ Mute """
                
        self.mute_flag = not self.mute_flag
        
        if self.mute_flag:
            self.current_volume_level = self.get_volume() 
            self.call(MUTE_1)
        else:
            if self.current_volume_level != None:
                self.call(SET_VOLUME_1 + " " + self.current_volume_level)
    
    def play(self, state):
        """ Start playing specified station. First it cleans the playlist 
        then adds new station to the list and then starts playing that station
        
        :param state: button state which contains the station to play
        """
        self.call(CLEAR)
        self.current_url = state.url
        self.call(ADD + state.url)
        self.call(PLAY + '1')
    
    def pause(self):
        """ Pause playback if playing. Resume playback if paused already """
                
        status = self.status()
        state = status.get(Player.STATE)
        
        if state is not Player.PAUSED:
            self.call(PAUSE)
        else:
            self.call(RESUME) 
    
    def play_pause(self):
        """ Play/pause playback """
                
        status = self.status()
        state = status.get(Player.STATE)
        
        if state is not Player.PAUSED:
            self.pause()
        else:
            self.call(PLAY) 
    
    def stop(self):
        """ Stop playback """
                
        self.call(STOP)

    def shutdown(self):
        """ Shutdown the player """
                
        if not self.linux:
            subprocess.Popen("taskkill /F /T /PID {pid}".format(pid=self.mpc_process.pid))
        self.playing = False
