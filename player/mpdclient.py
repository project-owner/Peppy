# Copyright 2023 Peppy Player peppy.player@gmail.com
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

import os
import threading
import time
import urllib
import logging

from mpd import MPDClient
from player.baseplayer import BasePlayer
from player.player import Player
from util.fileutil import FILE_PLAYLIST, FILE_AUDIO
from util.config import RADIO, AUDIO_FILES, AUDIOBOOKS, CD_PLAYER, STREAM, PODCASTS, ARCHIVE

class Mpdclient(BasePlayer):
    """ This class extends base player and provides communication with MPD process using TCP/IP socket """
        
    def __init__(self):
        """ Initializer. Starts separate thread for listening MPD events """
        
        BasePlayer.__init__(self);  
        self.host = "localhost"
        self.port = 6600  # this is default MPD port. If it was changed in mpd.conf it should be changed here as well
        self.muted = False
        self.playing = True
        self.dont_parse_track_name = False
        self.current_volume_level = "-1"

        self.commander = MPDClient(use_unicode=True)
        self.commander.timeout = 10
        

        self.handlers = {
            RADIO: self.handle_stream_callback,
            STREAM: self.handle_stream_callback,
            CD_PLAYER: self.handle_cdplayer_callback,
            AUDIO_FILES: self.handle_audiofile_callback,
            AUDIOBOOKS: self.handle_file_stream_callback,
            PODCASTS: self.handle_file_stream_callback,
            ARCHIVE: self.handle_file_stream_callback
        }
    
    def set_proxy(self, proxy_process, proxy=None):
        """ mpd client doesn't use proxy """
        
        pass
    
    def start_client(self):
        """ Start client thread """
        
        self.commander.connect(self.host, self.port)
        
        # self.commander.update()
        event_thread = threading.Thread(target=self.mpd_event_listener)
        event_thread.start()
        ping_thread = threading.Thread(target=self.ping)
        ping_thread.start()

    def stop_client(self):
        """ Stop thread """

        with self.lock:
            self.playing = False
            self.commander.close()
            self.event_handler.close()
            self.commander.disconnect()
            self.event_handler.disconnect()

    def ping(self):
        """ Keeps mpd server alive """

        while self.playing:
            with self.lock:
                try:
                    self.commander.ping()
                except:
                    pass
            time.sleep(20)
       
    def mpd_event_listener(self):
        """ Starts the loop for listening MPD events """
        
        while self.playing:
            try:
                event_handler = MPDClient(use_unicode=True)
                event_handler.connect(self.host, self.port)
                # blocking line, disables timeout
                lines = event_handler.idle("player", "mixer", "playlist")
                logging.debug("-------------------------------------------------" + str(lines))
                if lines and "mixer" in lines:
                    volume = self.get_volume()
                    self.notify_volume_listeners(volume)
                else:
                    if len(lines) == 1:
                        self.handlers[self.player_mode](lines[0])
                    else:
                        for c in lines:
                            self.handlers[self.player_mode](c)
                event_handler.close()
                event_handler.disconnect()
            except Exception as e:
                logging.debug(e)
                
    def handle_stream_callback(self, line):
        """ Radio callback handler """
        
        current_title = status = None

        with self.lock:
            current_song = self.commander.currentsong()
            current_title = current_song.get("title")
            status = self.status()

        if current_title == None:
            return
        
        current_title = current_title.strip()
        status["current_title"] = current_title
        status["state"] = status.get("state", None)
        status["source"] = "player"

        self.notify_player_listeners(status)        

    def handle_audiofile_callback(self, line):
        """ Audiofiles callback handler """
        time.sleep(2)
        current = self.commander.currentsong()

        if current == None:
            return
        
        current_file = current.get("file", None)
        current_title = current.get("title", None)
        current["current_track_id"] = current.get("track", None)

        if not current_title:
            try:
                if not self.dont_parse_track_name:
                    current_title = current_file
                    tokens = current_title.split("/")
                    current_title = tokens[len(tokens) - 1]
            except:
                pass
            
        if current_title == None and current_file == None:
            self.notify_end_of_track_listeners()
            return
        elif current_title:
            status = self.commander.status()
            current_title = current_title.strip()
            current["current_title"] = current_title
            current["Time"] = current.get("duration", 0)
            current["state"] = status.get("state")
            current["source"] = "player"
            track_time = status.get("time")
            if track_time:
                current["seek_time"] = track_time.replace(":", ".")

            self.notify_player_listeners(current)
    
    def handle_file_stream_callback(self, line):
        """ File stream handler
        
        :line: line from idle command
        """
        status = self.status()
        current = self.commander.currentsong()

        current_file = current.get("file", None)
        current_title = current.get("title", None)
 
        if current_title == None and current_file == None and "player" in line:
            self.notify_end_of_track_listeners()
            return
         

        current["current_track_id"] = current.get("track", None)
        current["Time"] = status.get("duration", None)
        current["current_title"] = current_file
        t = status["time"]
        if t:
            track_time = t.replace(":", ".")
            current["seek_time"] = track_time
        current["state"] = status.get("state", None)
        current["source"] = "player"
        if current_file:
            current_title = current.get("file", None)
            tokens = current_file.split("/")
            current_title = tokens[len(tokens) - 1]
            ct = urllib.parse.unquote(current_title)
            current["file_name"] = ct        
        
        self.notify_player_listeners(current)
        
    def handle_cdplayer_callback(self, line):
        """ CD player callback handler
        
        :line: line from idle command
        """
        current = self.commander.currentsong()
        status = self.status()
        current_file = current_title = current_track_id = None
        
        current_title = current["title"]
        current_file = current["file"]
        current_track_id = current["track"]
        current["current_track_id"] = current_track_id
        current["Time"] = status["duration"]
        current["state"] = status["state"]
        current["source"] = "player"
        
        if "playlist" in line and current_title == None:
            return
            
        if current_title == None and current_file == None:
            self.notify_end_of_track_listeners()
            return
        
        current["cd_track_id"] = self.cd_track_id
        current["file_name"] = "cdrom"
        if self.cd_tracks:
            current["current_title"] = self.cd_tracks[int(self.cd_track_id) - 1].name
        else:
            current["current_title"] = self.cd_drive_name + self.cd_track_title + " " + self.cd_track_id                               
            
        try:                    
            track_time = status["time"].replace(":", ".")
            current["seek_time"] = track_time
        except:
            pass

        self.notify_player_listeners(current)
           
    def play(self, state):
        """ Start playing specified track/station. First it cleans the playlist 
        then adds new track/station to the list and then starts playback
        
        :param state: button state which contains the track/station info
        """
        self.state = state
        s = getattr(state, "playback_mode", None)
        track_time = self.get_track_time(state)

        if s and s == FILE_PLAYLIST:
            track_number = str(state.playlist_track_number)
            self.commander.play(track_number)

            self.seek(track_time)
            self.mode = FILE_PLAYLIST
            return 
        
        self.mode = FILE_AUDIO
        url = getattr(state, "url", None)
        
        if url == None: 
            return

        file_name = getattr(state, "file_name", None)

        if file_name and getattr(state, "folder", None) and not url.startswith("http"):
            self.dont_parse_track_name = False
            url = self.get_url(state)
            url = url.replace("\\", "/").replace("\"", "")
        else:
            self.dont_parse_track_name = True
        
        v = getattr(state, "volume", None)
        if v and v != self.current_volume_level:
            self.current_volume_level = v
            self.set_volume(v)
        
        if url.startswith("http") or url.startswith("https"):
            url = self.encode_url(url)
        elif url.startswith("cdda://"):
            if file_name:
                parts = file_name.split()
                self.cd_track_id = parts[1].split("=")[1]                
                self.cd_drive_name = parts[0][len("cdda:///"):]
                url = parts[0].replace("////", "///") + os.sep + self.cd_track_id
            
        self.current_url = url

        with self.lock:
            self.commander.command_list_ok_begin() 
            self.commander.clear()
            self.commander.add(url)
            self.commander.play()
            self.commander.command_list_end()
        
        if file_name:
            logging.debug("fiiiiiiiiiiiiiile: " + file_name)

        logging.debug("traaaaaaaaack: " + str(track_time))
        if file_name and track_time != "0" and track_time != "0.0":
            logging.debug("seeeeeeeeeeeeeek")
            self.seek(track_time)

        if getattr(state, "pause", None):
            self.pause()
            
    def get_track_time(self, state):
        """ Return track seek time
        
        :param state: state object
        :return: track seek time
        """
        track_time = getattr(state, "track_time", None)
        if track_time != None:
            track_time = str(track_time)
            if ":" in track_time:
                track_time = track_time.replace(":", ".")
        else:
            track_time = "0"
            
        return track_time
    
    def stop(self, state=None):
        """ Stop playback """
        
        with self.lock:
            try:
                self.commander.clear()
                # self.commander.stop()
            except Exception as e:
                logging.debug(e)
    
    def seek(self, time):
        """ Jump to the specified position in the track
        
        :param time: time position in track
        """
        with self.lock:
            self.commander.seekcur(time)
    
    def pause(self):
        """ Pause playback """

        with self.lock:
            self.commander.pause()
    
    def play_pause(self, pause_flag=None):
        """ Play/Pause playback 
        
        :param pause_flag: play/pause flag
        """
        with self.lock:
            self.commander.pause()
    
    def set_volume(self, level):
        """ Set volume level
        
        :param level: new volume level
        """
        try:
            with self.lock:
                self.commander.setvol(level)
        except:
            pass
                    
    def get_volume(self):
        """  Return current volume level 
        
        :return: volume level or -1 if not available
        """
        with self.lock:
            status = self.status()
            volume = '-1'
            
            if "volume" in status:
                volume = status["volume"]
            
            if volume == "-1":
                with self.lock:
                    volume = self.current_volume_level
            
            return int(volume)
    
    def mute(self):
        """ Mute """

        self.muted = not self.muted
            
        if self.muted:
            v = self.get_volume()
            if v != 0:                
                self.current_volume_level = v 
            self.set_volume(0)
        else:
            self.set_volume(self.current_volume_level)
    
    def status(self):
        """ Return the result of the STATUS command """

        with self.lock:
            return self.commander.status()

    def shutdown(self):
        """ Shutdown the player """
        
        with self.lock:
            self.playing = False
            self.commander.close()
            self.event_handler.close()
            self.commander.disconnect()
            self.event_handler.disconnect()
        
    def get_current_track_time(self):
        """  Return current track time
        
        :return: current track time
        """
        s = self.status()
        t = None
        try:
            t = s[Player.DURATION]
        except:
            pass
        return t
    
    def get_current_playlist(self):
        """  Return current playlist
        
        :return: current playlist
        """
        with self.lock:
            d = self.commander.playlist()
            playlist = []
            for n in d:
                filename = n[6:]
                playlist.append(filename)
            return playlist
        
    def load_playlist(self, state):
        """  Load new playlist
        
        :param state: state object defining playlist location
        :return: new playlist
        """
        with self.lock:
            self.commander.clear()
            try:
                url = self.get_url(state)
                url = url.replace("\"", "")
                self.commander.load(url)
                return self.get_current_playlist()
            except Exception as e:
                logging.debug(e)
    
    def notify_end_of_track_listeners(self):
        """  Notify end of track listeners. """
        
        for listener in self.end_of_track_listeners:
            listener()
