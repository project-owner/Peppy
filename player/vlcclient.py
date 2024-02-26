# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
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
import math

from player.baseplayer import BasePlayer
from vlc import Meta, EventType, MediaStats
from queue import Queue
from util.fileutil import FILE_PLAYLIST, FILE_AUDIO
from util.config import RADIO

class Vlcclient(BasePlayer):
    """ This class extends base player and provides communication with VLC player 
    using Python binding for 'libvlc' library """
        
    def __init__(self):
        """ Initializer """
        
        BasePlayer.__init__(self)
        self.mode = RADIO
        self.instance = None
        self.player = None
        self.media = None
        self.current_track = ""
        self.station_metadata = {}
        self.seek_time = "0"
        self.END_REACHED = "end reached"
        self.TRACK_CHANGED = "track changed"
        self.PAUSED = "paused"
        self.player_queue = Queue()
        self.threads_running = False
        self.changing_volume = False

    def start_client(self):
        """ Start threads. """
        
        self.threads_running = True
        radio_handler = threading.Thread(target = self.radio_stream_event_listener)
        radio_handler.start()
        event_handler = threading.Thread(target = self.handle_event_queue)
        event_handler.start()

    def stop_client(self):
        """ Stop threads """

        with self.lock:
            self.threads_running = False

    def set_proxy(self, proxy_process, proxy=None):
        """ Create new VLC player """
        
        self.instance = proxy_process
        self.proxy = proxy
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
    
    def radio_stream_event_listener(self):
        """ Starts the loop for listening VLC events for radio track change """

        while self.threads_running:
            with self.lock:
                if self.media and self.mode == RADIO:
                    metadata = self.get_radio_stream_metadata()
                    title = self.media.get_meta(Meta.NowPlaying)

                    if title and title != self.current_track and self.enabled:
                        self.current_track = title
                        self.notify_player_listeners({self.CURRENT_TITLE: title})
                        self.notify_title_listeners(title)

                    if self.station_metadata != metadata:
                        self.station_metadata = metadata
                        self.notify_metadata_listeners(metadata)

            time.sleep(1)

    def get_radio_stream_metadata(self):
        """ Get radio stream metadata

        :return: metadata dictionary
        """
        metadata = {}
        codec = ""
        rate = channels = None
        media_stats = MediaStats()

        try:
            track_info = self.media.get_tracks_info()
            if track_info and track_info.contents:
                channels = track_info.contents.channels
                if channels:
                    metadata[self.CHANNELS] = channels
                rate = track_info.contents.rate
                if rate:
                    metadata[self.SAMPLE_RATE] = rate
                c = track_info.contents.codec
                while (c > 0):
                    codec += chr(c & 0xff)
                    c = math.floor(c / 256)
                if codec:
                    metadata[self.CODEC] = codec
        except:
            pass

        genre = self.media.get_meta(Meta.Genre)
        if genre:
            metadata[self.GENRE] = genre
        station = self.media.get_meta(Meta.Title)
        if station:
            metadata[self.STATION] = station

        if self.media.get_stats(media_stats):
            bitrate = round(media_stats.demux_bitrate * 8000 * 1000)
            metadata[self.BITRATE] = bitrate

        return metadata

    def handle_event_queue(self):
        """ Handling player event queue """
        
        if not self.enabled:
            return

        while self.threads_running:
            d = self.player_queue.get() # blocking line
            if d  == self.END_REACHED:
                self.notify_end_of_track_listeners()
                self.player_queue.task_done()
            elif d  == self.TRACK_CHANGED:
                self.track_changed()
                self.player_queue.task_done()
                
    def track_changed(self):
        """ Handle track change event """

        if not self.enabled:
            return
        
        if self.mode == RADIO: 
            return
        
        current = {"source": "player"}
        current["state"] = "playing"
        t = self.media.get_meta(Meta.Title)
        if t == ".":
            return
                
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

    def set_player_volume_control(self, flag):
        """ Player Volume Control type setter

        :param volume: True - player volume cotrol type, False - amixer or hardware volume control type
        """
        BasePlayer.set_player_volume_control(self, flag)
        if not self.player_volume_control:
            self.set_volume(100)

    def play(self, state):
        """ Start playing specified track/station. First it cleans the playlist 
        then adds new track/station to the list and then starts playback
        
        :param state: button state which contains the track/station info
        """
        url = None
        self.enabled = True

        if state == None:
            if self.state != None:
                url = getattr(self.state, "url", None)
            else:
                url = None
        else:
            url = getattr(state, "url", None)
            self.state = state    

        if url == None: 
            return      

        url = url.replace("\\", "/").replace("\"", "")
        track_time = getattr(self.state, "track_time", None)
        if track_time == None:
            track_time = "0"
        else:
            track_time = str(track_time)
            if ":" in track_time:
                track_time = track_time.replace(":", ".")
        self.seek_time = track_time
            
        s = getattr(self.state, "playback_mode", None)
        
        if s and s == FILE_PLAYLIST:
            self.stop()            
            self.mode = FILE_PLAYLIST
            self.enabled = True
        elif s and s == FILE_AUDIO:
            self.mode = FILE_AUDIO
        else:
            self.mode = RADIO
        
        if url.startswith("http") and self.mode != RADIO:
            url = self.encode_url(url)
        
        with self.lock:
            if self.proxy.stream_server_parameters == None:
                self.media = self.instance.media_new(url)
                self.player.set_media(self.media)
            else:
                self.player.stop()
                params = [url, self.proxy.stream_server_parameters]
                self.media = self.instance.media_new(*params)
                self.player.set_media(self.media)

            self.player.play()

            try:
                self.player.set_time(int(float(self.seek_time)) * 1000)
            except:
                pass
            
            if self.player_volume_control and getattr(self.state, "volume", None) != None:
                self.set_volume(int(self.state.volume))

    def stop(self, state=None):
        """ Stop playback """
        
        with self.lock:
            self.enabled = False
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
            msec = int(float(self.seek_time) * 1000)
            t = threading.Thread(target=self.seek_method, args=[msec])
            t.start()

    def seek_method(self, msec):
        """ Seek track thread method

        :param msec: milliseconds for new position
        """
        self.player.set_time(msec)
    
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
