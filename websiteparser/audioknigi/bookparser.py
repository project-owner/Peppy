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
import urllib

from websiteparser.siteparser import SiteParser, TITLE, MP3, HTTPSS, HTTPSSS, POST, FILE_NAME
from websiteparser.audioknigi.constants import BASE_URL, BOOK_URL, PREVIEW_URL, COOKIE, \
    HASH, SEC_KEY, AITEMS
from urllib import request

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
        
        self.found_img_div = False        

    def parse(self):
        """ Start book page parsing """
        
        page = self.get_response(self.url)
        lines = page.splitlines()
        self.img_url = self.get_image_url(lines)
        self.book_id = self.get_book_id(lines)
        if self.book_id:
            self.playlist = self.get_playlist(self.book_id)

    def get_response(self, url):
        """ Return http response for defined url
        
        :param url: current url
        :return: http response
        """
        h = {"Cookie": COOKIE}
         
        values = {}
        values["bid"] = self.book_id
        values["hash"] = HASH
        values["security_ls_key"] = SEC_KEY 
             
        d = urllib.parse.urlencode(values)
        d = d.encode('ascii')
        req = request.Request(url, headers=h, method=POST, data=d)
        with self.lock:
            response = request.urlopen(req).read()
        return response.decode('utf-8')

    def get_playlist(self, book_id):
        """ Return book playlist
        
        :param book_id: book id
        :return: book playlist
        """
        url = BOOK_URL + book_id
        self.book_id = book_id
        msg = self.get_response(url)
        j = json.loads(msg)
        items_str = j[AITEMS]
        items = json.loads(items_str)
        for t in items:
            if HTTPSSS in t[MP3]:
                n = t[MP3].replace(HTTPSSS, HTTPSS)
                t[MP3] = n
                t[TITLE] = n[n.rfind("/") + 1:]
                t[FILE_NAME] = t[TITLE]
        return items
        
    def get_book_id(self, lines):
        """ Retrieve book id from provided lines
        
        :param lines: text lines
        :return: book id
        """
        c = "$(document).audioPlayer("
        for v in lines:
            i = v.find(c)
            if i != -1:
                return v[i + len(c) : v.find(",")]
        return None
        
    def get_image_url(self, lines):
        """ Get cover image url from provided lines
        
        :param lines: text lines
        :return: book cover image url
        """
        p = "<img src=\""
        u = PREVIEW_URL
        c = p + u
        a = "\" alt"
        for v in lines:
            i = v.find(c)
            if i != -1:
                s = v[i + len(c) : v.find(a)]
                return u + s
        return None
