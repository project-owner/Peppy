# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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

import os, string
import platform
import re
import codecs
import logging

from re import compile, split
from ui.state import State
from os.path import expanduser
from util.config import AUDIO_FILE_EXTENSIONS, PLAYLIST_FILE_EXTENSIONS, FOLDER_IMAGES, CURRENT_FOLDER, \
    AUDIO, MUSIC_FOLDER, COVER_ART_FOLDERS, CURRENT_FILE, CLIENT_NAME, MPLAYER, VLC, FILE_PLAYBACK

FOLDER = "folder"
FOLDER_WITH_ICON = "folder with icon"
FILE_AUDIO = "file"
FILE_PLAYLIST = "playlist"
FILE_CD_DRIVE = "cd-player"
FILE_IMAGE = "image"

WINDOWS = "windows"
WINDOWS_DISK_SUFFIX = ":\\"
HIDDEN_FOLDER_PREFIXES = [".", "$", "System Volume Information"]
RE_HIDDEN_FOLDER_PREFIXES = "|".join(re.escape(p) for p in HIDDEN_FOLDER_PREFIXES)

class FileUtil(object):
    """ Utility class containing methods necessary for file playback """
    
    def __init__(self, config):
        """ Initializer 
        
        :param config: configuration object 
        """
        self.config = config
        self.platform = platform.system().lower()
        self.ROOT = os.path.abspath(os.sep)
        if WINDOWS in self.platform:
            self.ROOT = "\\"
            
        if self.config[AUDIO][MUSIC_FOLDER]:
            self.USER_HOME = self.config[AUDIO][MUSIC_FOLDER]
        else:
            self.USER_HOME = expanduser("~")
            
        self.current_folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER] or self.USER_HOME
        self.cre = compile(r'(\d+)') # compiled regular expression
    
    def get_windows_disks(self):
        """ Return disks available on Windows machine
        
        :return: list of characters representing available disks
        """        
        disks = list()
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32')
        SEM_FAILCRITICALERRORS = 1
        SEM_NOOPENFILEERRORBOX = 0x8000
        SEM_FAIL = SEM_NOOPENFILEERRORBOX | SEM_FAILCRITICALERRORS
        oldmode = ctypes.c_uint()
        kernel32.SetThreadErrorMode(SEM_FAIL, ctypes.byref(oldmode))
        
        for s in string.ascii_uppercase:
            n = s + WINDOWS_DISK_SUFFIX
            if os.path.exists(n):
                disks.append(n)

        kernel32.SetThreadErrorMode(oldmode, ctypes.byref(oldmode))
        
        return disks
    
    def is_audio_file(self, filename):
        """ Check if specified file is audio file 
        
        :param filename: file name
        :return:  
        """
        for e in self.config[AUDIO_FILE_EXTENSIONS]:
            if filename.lower().endswith(e):
                return True
        return False
    
    def is_playlist_file(self, filename):
        """ Check if specified file is playlist file 
        
        :param filename: file name
        :return:  
        """
        for e in self.config[PLAYLIST_FILE_EXTENSIONS]:
            if filename.lower().endswith(e):
                return True
        return False
    
    def get_folder_content(self, folder_name):
        """ Return the list representing folder content 
        
        :param folder_name: folder name
        :return:  
        """
        files = []
                
        if not os.path.exists(folder_name):
            return
        
        if folder_name.endswith(":") and WINDOWS in self.platform:
            folder_name += "\\"
        
        self.current_folder = folder_name
        
        if folder_name == self.ROOT and WINDOWS in self.platform:
            disks = self.get_windows_disks()
            for d in disks:                
                state = State()
                state.folder = self.current_folder
                state.file_type = FOLDER
                state.file_name = d
                state.url = d
                files.append(state)
            return files
        
        for f in os.listdir(folder_name):
            file_path = os.path.join(folder_name, f)
            real_path = os.path.realpath(file_path)
            
            state = State()
            state.folder = self.current_folder
            state.file_type = FOLDER
            state.file_name = f
            state.url = real_path
            
            if os.path.isdir(file_path) and not re.match(RE_HIDDEN_FOLDER_PREFIXES, f): # folder
                try:
                    folder_image_path = self.get_folder_image_path(real_path)
                    if folder_image_path:
                        state.file_type = FOLDER_WITH_ICON
                        state.file_image_path = folder_image_path
                    files.append(state)
                except PermissionError:
                    pass
            elif os.path.isfile(file_path) and not f.startswith("."): # file
                if self.is_audio_file(f):
                    state.file_type = FILE_AUDIO
                    files.append(state)
                elif self.is_playlist_file(f):
                    # had issues with mplayer and cue files:
                    # https://en.wikipedia.org/wiki/Talk%3ACue_sheet_(computing)#mplayer_have_more_faults
                    # had also issues using cue playlists and vlc python binding
                    p = self.config[AUDIO][CLIENT_NAME]
                    if (p == MPLAYER or p == VLC) and f.endswith(".cue"): 
                        continue
                    state.file_type = FILE_PLAYLIST
                    files.append(state)
        files.sort(key=lambda x: [int(n) if n.isdigit() else n.lower() for n in split(self.cre, x.file_name)])
        
        for n, f in enumerate(files):
            f.comparator_item = n
        
        return files
    
    def get_folder_image_path(self, folder):
        """ Return the path to image representing folder 
        
        :param folder_name: folder name
        :return: path to image file
        """
        if not folder: return None
        
        if not os.path.isdir(folder):
            self.config[FILE_PLAYBACK][CURRENT_FOLDER] = ""
            self.config[FILE_PLAYBACK][CURRENT_FILE] = "" 
            return None
        
        for f in os.listdir(folder):
            if f.lower() in self.config[FOLDER_IMAGES]:
                file_path = os.path.join(folder, f)
                real_path = os.path.realpath(file_path)
                return real_path
        return None
 
    def get_cover_art_folder(self, folder):
        """ Return the path to cover art folder 
        
        :param folder: folder name
        :return: path to folder
        """
        paths = []
        try:
            paths = os.listdir(folder)
        except:
            pass
        
        for f in paths:
            if f.lower() in self.config[COVER_ART_FOLDERS]:
                file_path = os.path.join(folder, f)
                real_path = os.path.realpath(file_path)
                return real_path
        return None
    
    def get_m3u_playlist(self, path):
        """ Return the content of m3u playlist 
        
        :param path: path to playlist
        :return: list of tracks from m3u playlist
        """
        tracks = []
        try:
            lines = codecs.open(path, "r", "utf-8-sig").read().split("\n")
            for t in lines:
                t = t.rstrip()
                if t and t.startswith("#"):
                    continue
                if t: tracks.append(t)
        except Exception as e:
            logging.error(str(e))
        return tracks
