# Copyright 2016-2022 Peppy Player peppy.player@gmail.com
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
import logging

from websiteparser.siteparser import SiteParser, TITLE, MP3, HTTPSS, HTTPSSS, POST, FILE_NAME, \
    DURATION, START_TIME, END_TIME
from websiteparser.audioknigi.constants import BASE_URL, BOOK_URL, PREVIEW_URL, COOKIE, \
    HASH, SEC_KEY, AITEMS, USER_AGENT
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

    def parse(self, img_url):
        """ Start book page parsing """
        
        self.img_url = img_url
        self.book_id = self.url[self.url.rfind("/") + 1:]
        page = self.get_response(self.url, self.book_id)
        self.playlist = []

        j = json.loads(page)
        try:
            items = json.loads(j["items"])
            key = j["key"]
        except:
            return

        server = j["srv"]
        title = j["title"]

        file_num = -1

        for t in items:
            i = {}
            if file_num == t["file"]:
                continue
            file_num = t["file"]
            i[TITLE] = "0" + str(file_num) + ". " + title + ".mp3"
            i[MP3] = server + "b/" + self.book_id + "/" + key + "/" + i[TITLE]
            i[FILE_NAME] = i[TITLE]
            i[DURATION] = t[DURATION]
            i[START_TIME] = t[START_TIME]
            i[END_TIME] = t[END_TIME]
            self.playlist.append(i)

    def get_response(self, url, bid):
        """ Return http response for defined url
        
        :param url: current url
        :return: http response
        """
        h = {"User-Agent": USER_AGENT, "Cookie": COOKIE}
         
        values = {}
        values["bid"] = bid
        values["hash"] = HASH
        values["security_ls_key"] = SEC_KEY 
             
        d = urllib.parse.urlencode(values)
        d = d.encode('ascii')
        req = request.Request(url, headers=h, method=POST, data=d)
        with self.lock:
            response = request.urlopen(req).read()
        return response.decode('utf-8-sig')
