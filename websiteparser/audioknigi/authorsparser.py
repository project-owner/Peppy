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

from websiteparser.siteparser import SiteParser, HTTPS, HTTP, GET, TBODY, TD, HREF, A, P, \
    AUTHOR_URL, AUTHOR_NAME, AUTHOR_BOOKS
from websiteparser.audioknigi.constants import BASE_URL, COOKIE
from urllib import request, parse

class AuthorsParser(SiteParser):
    """ Parser for authors page """
    
    def __init__(self):
        """ Initializer """
        
        SiteParser.__init__(self, BASE_URL)
        self.author = {}                
        self.found_tbody = False
        self.found_name_td = False
        self.found_name_a = False
        self.found_name_p = False
    
    def parse(self):
        """ Start authors page parsing if page is not in cache """
        
        self.items = self.get_from_cache()
        if self.items: return
        
        self.url.replace(HTTPS, HTTP)
        h = {"Cookie": COOKIE}
        req = request.Request(self.url, headers=h, method=GET)
        response = request.urlopen(req).read()
        page = response.decode('utf8')
        j = json.loads(page)
        txt = j["sText"]
        self.feed(txt)
        
        if self.items:
            self.cache[self.url] = self.items

    def handle_starttag(self, tag, attrs):
        """ Handle starting html tag
        
        :param tag: tag name
        :param attrs: tag attributes
        """
        if tag == TBODY:
            self.found_tbody = True            
        elif tag == TD and self.found_tbody and self.is_required_tag(TD, "cell-name", tag, attrs):
            self.found_name_td = True
            self.author = {}
        elif tag == A and self.found_name_td:    
            self.author[AUTHOR_URL] = self.get_attribute(HREF, attrs)
            self.found_name_a = True
        elif tag == P and self.found_name_td:    
            self.found_name_p = True

    def handle_endtag(self, tag):
        """ Handle ending html tag
        
        :param tag: tag name
        """
        if tag == TBODY and self.found_tbody:
            self.found_tbody = False
        elif tag == TD and self.found_name_td:
            self.found_name_td = False
            self.items.append(self.author)
        elif tag == A and self.found_name_a:
            self.found_name_a = False
        elif tag == P and self.found_name_td:    
            self.found_name_p = False
    
    def handle_data(self, data):
        """ Handle tag data block
        
        :param data: tag data string
        """
        if len(data) == 0: return
 
        if self.found_name_a:
            self.author[AUTHOR_NAME] = data
            n = parse.quote(data.encode('utf-8'))
            s = self.author[AUTHOR_URL]
            self.author[AUTHOR_URL] = s.replace(data, n)            
        elif self.found_name_p:
            s = data.split(" ")
            self.author[AUTHOR_BOOKS] = s[0]
        
    def get_authors(self, author_filter=None):
        """ Return the filtered list of authors
        
        :param author_filter: filter character
        """
        if author_filter == None and len(self.items) > 0:
            return self.items
        
        filtered_authors = []
        for a in self.items:
            if author_filter and a[AUTHOR_NAME].startswith(author_filter):
                filtered_authors.append(a)
        return filtered_authors
    
