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
import time
import urllib

from player.client.baseplayer import BasePlayer
from vlc import Meta
from vlc import EventType
from queue import Queue
from util.fileutil import FILE_PLAYLIST, FILE_AUDIO

class Vlcclient(BasePlayer):
    """ This class extends base player and provides communication with VLC player 
    using Python binding for 'libvlc' library """
        
    def __init__(self):
        """ Initializer. Starts separate threads for handling VLC events """
        
        self.RADIO_MODE = "radio"
        BasePlayer.__init__(self)
        self.mode = self.RADIO_MODE
        self.instance = None
        self.player = None
        self.media = None
        self.current_track = ""
        self.seek_time = "0"
        self.cd_track_id = None
        self.cd_drive_name = None
        thread = threading.Thread(target = self.radio_stream_event_listener)
        thread.start()
        self.END_REACHED = "end reached"
        self.TRACK_CHANGED = "track changed"
        self.PAUSED = "paused"
        self.player_queue = Queue()
        thread1 = threading.Thread(target = self.handle_event_queue)
        thread1.start()
        
    def set_proxy(self, proxy):
        """ Create new VLC player """
        
        self.instance = proxy
        self.player = self.instance.media_player_new()
        player_mgr = self.player.event_manager()
        player_mgr.event_attach(EventType.MediaPlayerEndReached, self.player_callback, [self.END_REACHED])
        player_mgr.event_attach(EventType.MediaPlayerPlaying, self.player_callback, [self.TRACK_CHANGED])
    
    def player_callback(self, event, data):
        """ Player callback method 
        
        :param event: event to handle
        :param data: event data
        """
        
        if data:
            self.player_queue.put(data[0])
    
    def handle_event_queue(self):
        """ Handling player event queue """
        
        while True:
            d = self.player_queue.get() # blocking line
            if d  == self.END_REACHED:
                self.notify_end_of_track_listeners()
                self.player_queue.task_done()
            elif d  == self.TRACK_CHANGED:
                self.track_changed()
                self.player_queue.task_done()
                
    def track_changed(self):
        """ Handle track change event """
        
        if self.mode == self.RADIO_MODE: 
            return
        
        current = {"source": "player"}
        current["state"] = "playing"
        t = self.media.get_meta(Meta.Title)
        if t == ".":
            return
        if self.cd_track_id and t.startswith("cdda:"):
            current["cd_track_id"] = self.cd_track_id
            if self.cd_tracks:
                t = self.cd_tracks[int(self.cd_track_id) - 1].name
            else:
                t = self.cd_drive_name + self.cd_track_title + " " + self.cd_track_id
                
        m = self.media.get_mrl()
        m = m[m.rfind("/") + 1:]
        m = urllib.parse.unquote(m)
        current["file_name"] = m
        current["current_title"] = t
        current["Time"] = str(self.player.get_length()/1000)
        
        if not self.seek_time:
            self.seek_time = "0"
        current["seek_time"] = self.seek_time
        self.notify_player_listeners(current)

    def start_client(self):
        """ There is no separate VLC client. """
        
        pass
    
    def radio_stream_event_listener(self):
        """ Starts the loop for listening VLC events for radio track change """
        
        while True:
            with self.lock:
                if self.media and self.mode == self.RADIO_MODE:
                    t = self.media.get_meta(Meta.NowPlaying)
                    if t and t != self.current_track:
                        self.current_track = t
                        self.notify_player_listeners({"current_title": t})
            time.sleep(1)
                        
    def play(self, state):
        """ Start playing specified track/station. First it cleans the playlist 
        then adds new track/station to the list and then starts playback
        syntax for CD:
        self.media = self.instance.media_new("cdda:///E:/", (":cdda-track=7"))
        
        :param state: button state which contains the track/station info
        """
        self.state = state
        url = getattr(state, "url", None)
        if url == None: 
            return        
        url = url.replace("\\", "/").replace("\"", "")
        track_time = getattr(state, "track_time", None)
        if track_time == None:
            track_time = "0"
        else:
            track_time = str(track_time)
            if ":" in track_time:
                track_time = track_time.replace(":", ".")
        self.seek_time = track_time
            
        s = getattr(state, "playback_mode", None)
        
        if s and s == FILE_PLAYLIST:
            self.stop()            
            self.mode = FILE_PLAYLIST
        elif s and s == FILE_AUDIO:
            self.mode = FILE_AUDIO
        else:
            self.mode = self.RADIO_MODE
        
        if url.startswith("http"):
            url = self.encode_url(url)
        
        with self.lock:
            file_name = getattr(state, "file_name", None)
            if file_name and file_name.startswith("cdda://"):
                parts = file_name.split()
                self.cd_track_id = parts[1].split("=")[1]                
                self.cd_drive_name = parts[0][len("cdda:///"):]
                self.media = self.instance.media_new(parts[0], parts[1])
            else:            
                self.media = self.instance.media_new(url)
            self.player.set_media(self.media)            
            
            self.player.play()            
            self.player.set_time(int(float(self.seek_time)) * 1000)
            
            if getattr(state, "volume", None):
                self.set_volume(int(state.volume))
            
    def stop(self, state=None):
        """ Stop playback """
        
        with self.lock:
            self.player.stop()
    
    def seek(self, time):
        """ Jump to the specified position in the track
        
        :param time: time position in track
        """
        
        if ":" in time:
            self.seek_time = self.get_seconds_from_string(time)
        else:
            self.seek_time = time
        
        with self.lock:            
            v = self.get_volume()
            msec = int(float(self.seek_time) * 1000)
            self.player.set_time(msec)
            self.set_volume(v)           
    
    def play_pause(self, pause_flag=None):
        """ Play/Pause playback 
        
        :param pause_flag: play/pause flag
        """ 
        with self.lock:
            self.seek_time = self.get_current_track_time()
            self.player.pause()
    
    def set_volume(self, level):
        """ Set volume.
        
        :param level: new volume level
        """
        self.player.audio_set_volume(int(level))
        if self.get_volume() != int(level): # usually initial volume setting
            t = threading.Thread(target=self.set_volume_level, args=[level])
            t.start()
    
    def set_volume_level(self, level):
        """ Set volume level in separate thread
        
        :param level: volume level
        """
        n = 0
        max_n = 20
        vol = -2
        
        while n < max_n and level != vol:
            self.player.audio_set_volume(int(level))
            time.sleep(0.2)
            vol = self.get_volume()
            n += 1
    
    def get_volume(self):
        """  Return current volume level 
        
        :return: volume level or -1 if not available
        """
        with self.lock:
            return self.player.audio_get_volume()
    
    def mute(self):
        """ Mute """
        
        with self.lock:
            self.player.audio_toggle_mute()
        
    def current(self):
        """ Return the current song """
        pass

    def shutdown(self):
        """ Shutdown the player """
        with self.lock:
            self.player.stop()
        
    def get_current_track_time(self):
        """  Return current track time
        
        :return: current track time
        """
        t = self.player.get_time()/1000
        return str(t)
    
    def get_current_playlist(self):
        """  Return current playlist
        
        :return: current playlist
        """
        return self.playlist
