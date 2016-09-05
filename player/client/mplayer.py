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
import threading
import logging
import codecs

class Mplayer(Player):
    """ This class extends abstract Player and implements its methods. 
    It serves as a wrapper for 'mplayer' process 
    """    
    lock = threading.RLock()
    use_shell = True
    
    def __init__(self):
        """ Initializer. Starts new thread which listens to the player events """
                        
        self.items = None
        self.current_track = None
        self.volume = None
        self.volume_listeners = [] 
        self.player_listeners = []
        self.current_url = None
        self.playing = True
        self.proxy = None       
    
    def set_platform(self, linux):
        """ Set platform flag
        
        :param linux: True - current platform is Linux, False - Current platform is Windows
        """        
        self.linux = linux
        
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
        while self.playing:
            try:       
                line = self.proxy.stdout.readline().decode("UTF-8").rstrip()
                logging.debug(str(line))
                try:
                    if self.volume_listeners:
                        self.get_volume()
                except:
                    pass
                
                if "ICY Info:" in line:
                    current_title = line.split("'")[1]
                    if current_title:
                        self.notify_player_listeners(current_title)
                elif "ANS_volume" in line:
                    volume = float(line.split("=")[1])
                    self.notify_volume_listeners(volume)
            except Exception as e:
                logging.debug(str(e))
    
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
        """ Call mplayer process with specified arguments
        
        :param args: arguments for call
        """        
        try:
            self.proxy.stdin.write(arg + "\n")
            self.proxy.stdin.flush()
        except Exception as e:
            logging.debug(str(e))        
        
    def get_volume(self):
        """  Issues 'get_property volume' command. The result will be handled in the player thread """
        
        self.call("get_property volume")
        
    def set_volume(self, level):
        """ Set volume level
        
        :param level: new volume level
        """
        self.call("volume " + str(level) + " 100")
        pass
    
    def mute(self):
        """ Mute """
        
        self.call("mute")
    
    def play(self, state):
        """ Start playing specified station. 
        
        :param state: button state which contains station url
        """
        self.stop()
        self.current_url = state.url
        logging.debug("load: " + state.url)
        self.call("loadfile " + state.url)
    
    def pause(self):
        """ Pause playback if playing. Resume playback if paused already """
           
        self.call("pause")
    
    def play_pause(self):
        """ Play/pause playback """
        
        self.call("pause")
    
    def stop(self):
        """ Stop playback """
        
        self.call("stop")

    def shutdown(self):
        """ Shutdown the player and client """
        
        self.playing = False
        self.call("quit")
        
