# Copyright 2020 Peppy Player peppy.player@gmail.com
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

import logging
import mpv
import json

from player.client.baseplayer import BasePlayer
from util.fileutil import FILE_PLAYLIST, FILE_AUDIO

class Mpvclient(BasePlayer):
    """ This class provides communication with MPV player using Python binding for 'libmpv' library """
        
    def __init__(self):
        """ Initializer """
        
        self.RADIO_MODE = "radio"
        BasePlayer.__init__(self)
        self.mode = self.RADIO_MODE
        self.player = None
        self.current_track = ""
        self.current_file = ""
        self.seek_time = "0"
        self.stopped = False
        
    def set_proxy(self, proxy_process, proxy=None):
        """ Set proxy """
        
        self.instance = proxy_process
        self.proxy = proxy

    def start_client(self):
        """ Create player, set callbacks """
        
        config = {}
        try:
            config = json.loads(self.proxy.start_command)  
        except Exception as e:
            logging.debug(e)

        self.player = mpv.MPV(**config)

        @self.player.event_callback(mpv.MpvEventID.END_FILE)
        def handle_end_file(_):
            """ End of track handler """

            if self.mode == self.RADIO_MODE or self.stopped:
                return

            player_filename = ""
            try:
                player_filename = self.player.filename
            except Exception as e:
                logging.debug(e)

            if player_filename == None:
                player_filename = ""

            if player_filename and player_filename != self.current_file:
                return
            else:
                self.notify_end_of_track_listeners()

        @self.player.event_callback(mpv.MpvEventID.METADATA_UPDATE)
        def handle_metadata(_):
            """ Metadata change handler """

            if self.stopped:
                return

            if self.mode == self.RADIO_MODE:
                t = self.player.metadata["icy-title"]
                if t and t != self.current_track and self.enabled:
                    self.current_track = t
                    self.notify_player_listeners({"current_title": t})
            else:
                self.track_changed()

        # @self.player.property_observer('time-pos')
        # def time_observer(_, value):
        #     logging.debug(f"{value}")
                    
    def track_changed(self):
        """ Handle track change event """

        if not self.enabled:
            return
        
        if self.mode == self.RADIO_MODE: 
            return

        current = {"source": "player"}
        current["state"] = "playing"
        current["file_name"] = self.get_string(self.player.filename)
        self.current_file = current["file_name"]

        try:
            t = self.player.filtered_metadata["Title"]
            current["current_title"] = self.get_string(t)
        except Exception as e:
            current["current_title"] = " "
            logging.debug(e)

        current["Time"] = str(self.player.duration)
        
        if not self.seek_time:
            self.seek_time = "0"
        current["seek_time"] = self.seek_time

        if self.seek_time != "0" and self.seek_time != "0.0":
            self.player.time_pos = float(self.seek_time)

        self.notify_player_listeners(current)
    
    def get_string(self, n):
        """ Convert binary to string

        :param n: input object

        :return: string object
        """
        if isinstance(n, str):
            return n

        s = None

        try:
            s = n.decode('utf-8', 'ignore')
        except:
            pass

        if s == None:
            try:
                s = n.decode('ascii', 'ignore')
            except:
                pass

        if s == None:
            s = " "

        return s

    def play(self, state):
        """ Start playing specified track/station.
        
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
        
        if url.startswith("http") and self.mode != self.RADIO_MODE:
            url = self.encode_url(url)
        
        try:
            self.stopped = False
            self.player.play(url)
        except Exception as e:
            logging.debug(e)

        if getattr(state, "volume", None):
            self.player.volume = float(state.volume)
            
    def stop(self, state=None):
        """ Stop playback """

        self.stopped = True
        self.player.command("stop")

    def seek(self, time):
        """ Jump to the specified position in the track
        
        :param time: time position in track
        """
        
        if ":" in time:
            self.seek_time = self.get_seconds_from_string(time)
        else:
            self.seek_time = time
        
        self.player.time_pos = float(self.seek_time)

    def play_pause(self, pause_flag=None):
        """ Play/Pause playback 
        
        :param pause_flag: play/pause flag
        """ 
        with self.lock:
            if not self.player.playback_abort:
                self.seek_time = self.player.time_pos
                self.player.pause = not self.player.pause
                if not self.player.pause:
                    self.track_changed()
    
    def set_volume(self, level):
        """ Set volume.
        
        :param level: new volume level
        """
        self.player.volume = float(level)
        
    def get_volume(self):
        """  Return current volume level 
        
        :return: volume level or -1 if not available
        """
        with self.lock:
            return self.player.volume
    
    def mute(self):
        """ Mute """
        
        with self.lock:
            self.player.mute = not self.player.mute
        
    def current(self):
        """ Return the current song """
        pass

    def shutdown(self):
        """ Shutdown the player """

        pass
        
    def get_current_track_time(self):
        """  Return current track time
        
        :return: current track time
        """
        t = self.player.time_pos
        return str(t)
    
    def get_current_playlist(self):
        """  Return current playlist
        
        :return: current playlist
        """
        return self.playlist
