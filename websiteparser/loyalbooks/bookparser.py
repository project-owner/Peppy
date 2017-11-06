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

import json

from websiteparser.siteparser import SiteParser, MP3, FILE_NAME
from websiteparser.loyalbooks.constants import BASE_URL, DEFAULT_IMAGE

class BookParser(SiteParser):
    """ Parser for book page """
    
    def __init__(self, url=None):
        """ Initializer
        
        :param url: current url
        """
        SiteParser.__init__(self, BASE_URL, url)
        self.book_id = None
        self.img_url = None
        self.playlist = None
        
    def parse(self):
        """ Start book page parsing """
        
        page = self.get_page()
        lines = page.splitlines()
        
        self.book_id = self.url
        self.img_url = self.get_image_url(lines)
        self.playlist = self.get_playlist(lines)
        
    def get_playlist(self, lines):
        """ Return book playlist
        
        :param lines: text lines
        :return: book playlist
        """
        playlist = []
        s = "{name:\""
        for line in lines:
            if not line.startswith(s): continue
            n = line[0:-1].replace("name:", "\"name\":").replace("mp3:", "\"mp3\":").replace("free:", "\"free\":")
            m = json.loads(n)
            d = {}
            d["title"] = m["name"]
            mp3 = m[MP3]
            d[FILE_NAME] = mp3[mp3.rfind("/") + 1:]
            d[MP3] = m[MP3]
            playlist.append(d)
        return playlist
    
    def get_image_url(self, lines):
        """ Get cover image url from provided lines
        
        :param lines: text lines
        :return: book cover image url or default if not found
        """
        s = "<img itemprop=\"image\" class=\"cover\" src=\""
        for line in lines:
            if not line.startswith(s): continue
            n = line[len(s) + 1:]
            return self.base_url + n[0 : n.find("\"")]
        return DEFAULT_IMAGE
            
        
