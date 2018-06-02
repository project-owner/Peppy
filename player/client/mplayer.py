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

import codecs

from player.client.baseplayer import BasePlayer
from player.client.mplayercommands import ICY_INFO, ANS_FILENAME, ANS_LENGTH, ANS_TIME_POSITION, EOF, \
    ANS_VOLUME, STARTING_PLAYBACK, GET_FILENAME, GET_LENGTH, GET_VOLUME, VOLUME, VOLUME_KEY, \
    MUTE, LOAD_FILE, PAUSE, STOP, QUIT, GET_TRACK_TIME, SET_TRACK_TIME, POSITION
from queue import Queue
from threading import Thread

class Mplayer(BasePlayer):
    """ This class extends abstract Player and implements its methods. 
    It serves as a wrapper for 'mplayer' process 
    """    
    def __init__(self):
        """ Initializer """
        
        BasePlayer.__init__(self);
        self.proxy = None
        self.muted = False
        self.file_playback = False
        self.current_title = None
        self.notification_queue = Queue()
        self.UTF8 = "UTF-8"
        self.current_track_time = None
        self.current_track_length = None
    
    def set_proxy(self, proxy):
        """ Set proxy process. 
        
        :param proxy: reference to the proxy process
        """
        self.proxy = proxy 
    
    def start_client(self):
        """ This method starts reader and notification threads """
        
        notifications = Thread(target = self.notification_queue_reader)
        notifications.start()
                
        reader = Thread(target = self.stdout_reader)
        reader.start()
    
    def stdout_reader(self):
        """ Read mplayer output, prepare message and put it into the notification queue """
        
        self.proxy.stdout = codecs.getwriter(self.UTF8)(self.proxy.stdout.detach())
        
        while self.playing:
            msg = ()
            line = ""
            try:
                line = self.proxy.stdout.readline().decode(self.UTF8).rstrip() # blocking line
            except:
                pass
            
            if STARTING_PLAYBACK in line:
                msg = (STARTING_PLAYBACK, "")
            elif ICY_INFO in line:
                current_title = line.split("'")[1]
                msg = (ICY_INFO, current_title)    
            elif ANS_FILENAME in line:
                current_title = line.split("=")[1]
                msg = (ANS_FILENAME, current_title)
            elif ANS_LENGTH in line:
                duration = line.split("=")[1]
                msg = (ANS_LENGTH, duration)
            elif ANS_TIME_POSITION in line:
                seek_time = line.split("=")[1]
                msg = (ANS_TIME_POSITION, seek_time)
            elif POSITION in line:
                seek_time = line.split(":")[1].split("%")[0].lstrip().rstrip()
                msg = (POSITION, seek_time)
            elif EOF in line:
                msg = (EOF, "")
            elif ANS_VOLUME in line:
                volume = float(line.split("=")[1])
                msg = (ANS_VOLUME, volume)
            elif VOLUME_KEY in line:
                volume = int(line.split(" ")[1])
                msg = (ANS_VOLUME, volume)                
            
            if len(msg) == 0: continue
            
            self.notification_queue.put(msg)
    
    def read_starting_block(self, buffer):
        """ Read mplayer output block which starts with keyword 'Playing'
        and stops with keyword 'Starting playback'
        
        :param buffer: for for string lines
        """
        line = ""
        while STARTING_PLAYBACK not in line:
            try:
                line = self.proxy.stdout.readline().decode(self.UTF8).rstrip() # blocking line
                buffer.append(line)
            except:
                pass           
    
    def notification_queue_reader(self):
        """ Read messages from the notification queue and call corresponding callbacks """
        
        while self.playing:
            msg = self.notification_queue.get() # blocking line
            key = msg[0]
            value = msg[1]

            if ICY_INFO == key or ANS_FILENAME == key and value and len(value) > 0:
                if ANS_FILENAME == key:
                    v = int(float(self.current_track_time))
                    if self.current_track_time != None and v != 0:
                        self.seek(self.current_track_time)
                        self.current_track_time = None
                    self.get_current_track_time()                    
                if ANS_FILENAME == key and self.cd_tracks:
                    value = self.cd_tracks[int(value) - 1].name
                self.current_title = value
                self.notify_player_listeners(value)                   
            elif EOF == key:
                self.notify_end_of_track_listeners()
            elif ANS_VOLUME == key:
                self.notify_volume_listeners(value)
            elif ANS_TIME_POSITION == key or key.startswith(POSITION):
                if key.startswith(POSITION):
                    perecent_position = int(value)
                    track_length = int(float(self.current_track_length))
                    value = str((track_length * perecent_position) / 100)
                state = {}
                state["state"] = "playing"
                state["seek_time"] = value
                state["current_title"] = self.current_title
                self.notify_player_listeners(state)                
            elif ANS_LENGTH == key:
                if not value: continue                
                state = {}
                state["Time"] = value
                state["state"] = "playing"
                state["current_title"] = self.current_title
                self.current_track_length = value
                self.notify_player_listeners(state)
            elif STARTING_PLAYBACK == key:
                with self.lock:
                    if self.file_playback:
                        self.call(GET_FILENAME)
                        self.call(GET_LENGTH)
                    if self.muted:
                        self.mute()
                        self.muted = True  
        
    def command_method(self, cmd):
        """ Write command to mplayer's stdin
        
        :param cmd: command
        """        
        with self.lock:
            self.proxy.stdin.write(cmd + "\n")
            self.proxy.stdin.flush()
    
    def call(self, cmd):
        """ Start thread which will call mplayer with specified command
        
        :param cmd: command
        """
        ct = Thread(target=self.command_method, args=[cmd])
        ct.start()
        ct.join(0.5)
    
    def get_volume(self):
        """  Issue 'get_property volume' command. 
        The result will be handled in the notification thread """
        
        self.call(GET_VOLUME)
        
    def set_volume(self, level):
        """ Set volume level
        
        :param level: new volume level
        """
        self.call(VOLUME + str(level) + " 100")
    
    def mute(self):
        """ Mute """
        
        with self.lock:
            self.muted = not self.muted
        self.call(MUTE)
        
    def play(self, state):
        """ Play
        
        :param state: state object defining playback options
        """
        s = state.url
        filename = getattr(state, "file_name", None)
        
        if filename:
            s = s.replace('\\', '/')
            if not s.startswith("\"") and not s.endswith("\""):
                s = "\"" + s + "\""

        if s.startswith("http") or s.startswith("https"):
            s = self.encode_url(s)
        elif s[1:].startswith("cdda://"):
            track_id = s.split("=")[1]
            s = "\"cdda://" + track_id
        
        command = LOAD_FILE + s
        self.call(command)
        
        if filename:
            with self.lock:
                self.file_playback = True
            self.current_track_time = getattr(state, "track_time", None)
            if self.current_track_time != None:
                self.current_track_time = str(self.current_track_time)
                if ":" in self.current_track_time:
                    self.current_track_time = self.current_track_time.replace(":", ".")
            else:
                self.current_track_time = "0.0" 
        else:
            with self.lock:
                self.file_playback = False
    
    def pause(self):
        """ Pause playback if playing. Resume playback if paused already """

        self.call(PAUSE)
    
    def play_pause(self, pause_flag=None):
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
        """ Start getting current track time command
        
        :return: track time in seconds
        """
        return self.call(GET_TRACK_TIME)
    
    def seek(self, time):
        """ Set current track time
        
        :param time: new track time in seconds
        """
        self.call(SET_TRACK_TIME + time)

    def get_current_playlist(self):
        """  Return current playlist
        
        :return: current playlist
        """
        return self.playlist
