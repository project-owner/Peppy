# Copyright 2018-2021 Peppy Player peppy.player@gmail.com
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

import pygame.cdrom
import subprocess
import logging

from util.keys import *
from ui.state import State
from util.fileutil import FILE_CD_DRIVE, FILE_AUDIO
from util.config import CD_PLAYBACK, CD_DRIVE_NAME, CD_TRACK, COLORS, COLOR_DARK
from urllib import request

class CdUtil(object):
    """ CD Player Utility class """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """
        self.util = util
        self.config = util.config
        self.image_util = util.image_util
        # since 05.31.2020 freedb.org doesn't work anymore, replacing it by gnudb.org
        self.gnudb_server_url = 'http://gnudb.gnudb.org:80/~cddb/cddb.cgi'
        self.user = "peppy"
        self.host = "host"
        self.client = "peppy.player"
        self.client_version = "Vermeer"
        self.protocol = 5
        
    def get_cd_drives_number(self):
        """ Return the number of connected CD drives 
        
        :return: number of connected CD drives
        """
        pygame.cdrom.init()
        n = pygame.cdrom.get_count()
        return n
    
    def eject_cd(self, index):
        """ Eject CD from player
        
        :index: CD drive index
        """
        if not pygame.cdrom.get_init():
            pygame.cdrom.init()
        drive = pygame.cdrom.CD(index)
        try:
            drive.stop()
            if self.config[LINUX_PLATFORM]:
                drive_name = self.get_cd_drive_name_by_id(index)
                subprocess.call("eject " + drive_name, shell=True)
            else:
                drive.eject()
            drive.quit()
        except:
            pass 
    
    def get_cd_drives_info(self):
        """ Returns the names of connected CD drives
        
        :return: list of CD drive names
        """
        num = self.get_cd_drives_number()
        names = []
        
        for d in range(num):
            drive = pygame.cdrom.CD(d)
            id = drive.get_id()
            name = drive.get_name()
            names.append((id, name))
        
        return names
    
    def get_default_cd_drive(self):
        """ Get the default CD drive
        
        :return: the default CD drive
        """
        drives = self.get_cd_drives_info()
        if len(drives) > 0:
            return drives[0]
        else:
            return None        
    
    def get_cd_drive_name_by_id(self, id):
        """ Return CD drive name for provided ID
        
        :param id: CD ID
        
        :return: CD drive name
        """
        info = self.get_cd_drives_info()
        for i in info:
            if i[0] == id:
                return i[1]
        return None
    
    def get_cd_drive_id_by_name(self, name):
        """ Return CD drive ID for provided name
        
        :param id: CD drive name
        
        :return: CD drive ID
        """
        info = self.get_cd_drives_info()
        for i in info:
            if i[1] == name:
                return i[0]
        return None
    
    def get_cd_drives(self, font_size, bb):
        """ Return the list of object representing CD drives
        
        :font_size: font size
        
        :return: list of CD drives info
        """
        content = self.get_cd_drives_info()
        if not content:
            return None
        
        items = {}

        for cd in content:
            s = State()
            s.index = cd[0]
            s.name = cd[1]
            s.l_name = cd[1]
            s.file_type = FILE_CD_DRIVE          
            s.icon_base = self.image_util.get_file_icon(s.file_type, "", icon_bb=bb, scale_factor=0.25)
            s.comparator_item = s.index
            s.bgr = self.config[COLORS][COLOR_DARK]
            s.show_bgr = True
            s.fixed_height = int(font_size * 0.8) 
            items[s.name] = s
            
        return items
    
    def get_cd_track_names(self, drive_id):
        """ Get CD track names for provided CD drive ID
        
        :param drive_id: CD drive ID
        
        :return: the list of CD tracks
        """
        names = []
        
        if drive_id == None:
            return names
        
        if not pygame.cdrom.get_init():
            pygame.cdrom.init()
        
        drive = pygame.cdrom.CD(drive_id)
        drive.init()
        
        names = self.get_freedb_track_names(drive)
        
        if not names:
            names = self.get_default_track_names(drive)
            freedb_url = self.get_freedb_url(drive.get_all())
            self.util.cd_track_names_cache[drive_id] = names
        
        return names
    
    def get_all_tracks_info(self, drive_id):
        """ Return info about all CD tracks
        
        :param drive_id: CD drive ID
        
        :return: list of track info
        """
        drive = pygame.cdrom.CD(drive_id)
        return drive.get_all()
    
    def is_drive_empty(self, drive_name):
        """ Check if CD drive is empty
        
        :param drive_name: CD drive name
        
        :return: 0 - CD drive is empty, 1 - CD drive is not empty
        """
        drive_id = self.get_cd_drive_id_by_name(drive_name)
        drive = pygame.cdrom.CD(drive_id)
        if not drive.get_init():
            drive.init()
        empty = drive.get_empty()
        return empty
    
    def get_default_track_names(self, drive):
        """ Get the list of default track names e.g. Track 1, Track 2, etc.
        
        :param drive:  CD drive info
        
        :return: list of default names
        """
        names = []
        label = self.config[LABELS][CD_TRACK]
        
        if drive.get_empty():
            num = 0 
        else:
            num = drive.get_numtracks()
        
        if num == 0:
            return names
        
        for n in range(num):
            names.append(label + " " + str(n + 1))
        
        return names
    
    def get_cd_tracks_summary(self, cd_drive_name):
        """ Get the list of CD tracks summaries
        
        :param cd_drive_name: CD drive name
        
        :return: CD tracks summaries
        """
        drive_id = self.get_cd_drive_id_by_name(cd_drive_name)
        names = self.get_cd_track_names(drive_id)
        if not names:
            return None
        
        items = []
        for id, cd in enumerate(names):
            s = State()
            s.index = id
            s.playlist_track_number = id
            s.name = cd
            s.l_name = s.name
            s.file_type = FILE_AUDIO
            s.playback_mode = FILE_AUDIO
            s.file_name = self.get_cd_track_url(cd_drive_name, id + 1)
            s.url = s.file_name       
            items.append(s)
            
        return items
    
    def get_cd_tracks(self, rows, cols, fixed_height, cd_drive_name):
        """ Get CD tracks info
        
        :param rows: number of rows in tracks menu
        :param cols: number of columns in tracks menu
        :param fixed_height: text height of the menu item
        :param cd_drive_name: CD drive name
        
        :return: list of CD tracks info
        """
        summaries = self.get_cd_tracks_summary(cd_drive_name)
        if not summaries:
            return None
        
        items_per_page = cols * rows

        for s in summaries:
            s.show_img = False
            s.comparator_item = s.index
            s.bgr = self.config[COLORS][COLOR_DARK]
            s.show_bgr = True
            s.fixed_height = fixed_height
            s.index_in_page = s.index % items_per_page 
        
        return summaries
    
    def get_cd_track_url(self, cd_drive_name, track_id):
        """ Get CD track URL using cdda protocol
        
        :param cd_drive_name: CD drive name
        :param track_id: track ID
        
        :retun: track URL
        """
        return "cdda:///" + cd_drive_name + " :cdda-track=" + str(track_id)
         
    def get_cd_track(self):
        """ Get CD track info for the track defined in the configuration 
        
        :return: track info
        """
        s = State()
        cd_drive = self.config[CD_PLAYBACK][CD_DRIVE_NAME]
        cd_track = self.config[CD_PLAYBACK][CD_TRACK]
        if cd_drive and cd_track:
            s.file_name = self.get_cd_track_url(cd_drive, int(cd_track))
            s.url = s.file_name
            return s
        return None

    def cddb_sum(self, n):
        """ Calculate CDDB sum required for freedb """
        
        ret = 0
        while n > 0:
            ret = ret + (n % 10)
            n = int(n / 10)
        return int(ret)

    def get_freedb_url(self, tracks_info):
        """ Prepare freedb URL
        
        :param tracks_info: CD tracks info
        
        :return: freedb URL
        """
        n = 0
        size = len(tracks_info)
        total_seconds = 0.0
        blocks = []
        
        for i in tracks_info:
            n = n + self.cddb_sum(int(float(i[1])))            
            total_seconds = total_seconds + i[3]
            blocks.append(str(int(float(i[1])) * 75))

        m = int(total_seconds/60)
        sec = int(total_seconds%60)        
        total_seconds = (m * 60) + sec        
        id = (n % 0xff) << 24 | total_seconds << 8 | size
        
        query_str = (('%08lx+%d') % (id, size))

        for i in blocks:
            query_str = query_str + "+" + i
    
        query_str = query_str + ('+%d' % total_seconds)
        url = "%s?cmd=cddb+query+%s&hello=%s+%s+%s+%s&proto=%i" % \
              (self.gnudb_server_url, query_str, self.user, self.host, self.client, self.client_version, self.protocol)
        
        return url
    
    def get_freedb_cd_info(self, url, cd_drive_name):
        """ Get freedb CD info
        
        :param url: freedb CD URL
        :param cd_drive_name: CD drive name
        
        :return: CD info
        """
        req = request.Request(url)
        try:
            response = request.urlopen(req).read()
            res = response.decode('utf8')
        except Exception as e:
            logging.debug(e)
            return None

        lines = res.split("\r\n")        
        status = int(lines[0].split()[0])

        if status == 200: # single match
            line = lines[0]
            tokens = line.split()
            st = tokens[0]
            genre = tokens[1]
            id = tokens[2]
            title = line[len(st + genre + id) + 3:]
        elif status == 210 or status == 211: # multiple matches
            line = lines[1]
            tokens = line.split()
            genre = tokens[0]
            id = tokens[1]
            title = line[len(genre + id) + 2:]            
        else:
            return None

        self.util.cd_titles[cd_drive_name] = title
        return {"genre": genre, "id": id, "title": title}

    def get_freedb_track_names(self, drive):
        """ Get freedb tracks names
        
        :param drive: CD drive
        
        :return: track names from freedb
        """
        names = []
        try:
            names = self.util.cd_track_names_cache[drive.get_id()]
            if names: return names
        except:
            pass
        
        tracks_info = drive.get_all()
        freedb_url = self.get_freedb_url(tracks_info)
        cd_drive_name = drive.get_name()
        cd_info = self.get_freedb_cd_info(freedb_url, cd_drive_name)
        
        if cd_info == None:
            return None
        
        url = "%s?cmd=cddb+read+%s+%s&hello=%s+%s+%s+%s&proto=%i" % \
          (self.gnudb_server_url, cd_info["genre"], cd_info["id"], self.user, self.host, self.client, self.client_version, self.protocol)
        
        req = request.Request(url)
        response = request.urlopen(req).read()
        try:
            res = response.decode('utf8')
        except:
            return None
        lines = res.split("\r\n")        
        status = int(lines[0].split()[0])
        
        if status != 210:        
            return None
        
        id = 1

        for line in lines:
            if line.startswith("TTITLE"):
                v = line.split("=")[1]
                if not v[0].isdigit():
                    v = str(id) + ". " + v
                names.append(v)
                id += 1

        self.util.cd_track_names_cache[drive.get_id()] = names

        return names
