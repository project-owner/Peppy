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

import ssl

from html.parser import HTMLParser
from urllib import request
from threading import RLock

TOTAL_PAGES = "total_pages"
TOTAL_TIME = "total_time"
BOOK_SUMMARIES = "book_summaries"
HTTPS = "https"
HTTP = "http"
HTTPSS = HTTP + "://"
HTTPSSS = HTTPS + "://"
GET = "GET"
POST = "POST"
TBODY = "tbody"
TD = "td"
HREF = "href"
A = "a"
P = "p"
AUTHOR_URL = "author_url"
AUTHOR_NAME = "author_name"
AUTHOR_BOOKS = "author_books"
FILE_NAME = "file_name"
TITLE = "title"
ARTICLE = "article"
IMG = "img"
IMG_URL = "image_thumbnail_url"
SRC = "src"
HEADER = "header"
H3 = "h3"
BOOK_URL = "book_url"
GENRE_URL = "genre_url"
GENRE_NAME = "genre_name"
DIV = "div"
PERFORMER_URL = "performer_url"
PERFORMER_NAME = "performer_name"
I = "i"
B = "b"
UL = "ul"
BOOK_TITLE = "book_title"
ANNOTATION = "annotation"
MP3 = "mp3"
TABLE = "table"
RATING = "rating"
ID = "id"

class SiteParser(HTMLParser):
    """ Base class for all screen scrapers """
    
    lock = RLock()
    
    def __init__(self, base_url, url=None):
        """ Initializer
        
        :param base_url: site base url
        :param url: current url
        """
        HTMLParser.__init__(self)
        self.cache = {}
        self.items = []
        self.pages = {}
        self.total_pages = 0
        self.base_url = base_url
        self.url = self.base_url 
        self.site_total_pages = 0
        self.CACHE_SIZE = 500      
        if url:
            self.url = url

    def is_in_cache(self, url):
        """ Check if page defined by url is in cache
        
        :param url: page url
        :return: True - page in cache, False - page is not in cache
        """
        try:
            self.cache[url]
        except:
            return False
        return True

    def parse(self):
        """ Return page if in cache, start parsing if not in cache """
        
        self.items = self.get_from_cache()
        if self.items: return           
        
        page = self.get_page()
        
        with self.lock:
            self.feed(page)
            
        self.prepare_cache()
   
    def get_page(self):
        """ Read page from current url
        
        :return: html page
        """
        req = request.Request(self.url)
        site = request.urlopen(req)        
        charset = site.info().get_content_charset()
        html = site.read()
        response = None
        try:
            response = html.decode(charset)
        except:
            pass    
        return response
    
    def prepare_cache(self):
        """ Place pages in cache """
                    
        if self.items:
            self.cache[self.url] = self.items
            
    def get_from_cache(self):
        """ Get page defined by current url from cache
        
        :return: page object
        """
        i = []
        try:
            i = self.cache[self.url]
        except:
            pass
        return i

    def is_required_tag(self, required_tag, required_attr, tag, attrs):
        """ Check if tag has defined attribute
        
        :param required_tag: tag to check
        :param required_attr: attribute to find
        :param attrs: list of tag attributes
        :return: True - tag has attribute, False - tag doesn't have attribute
        """
        if tag != required_tag: return
        for attr in attrs:
            if required_attr in str(attr):
                return True
        return False

    def get_url_from_anchor(self, attrs):
        """ Return url attribute from the list of provided attributes
        
        :param attrs: list of attributes
        :return: url attribute
        """
        return self.get_attribute("href", attrs)

    def get_attribute(self, name, attrs):
        """ Return attribute value from the list of provided attributes
        
        :param name: attribute name
        :param attrs: list of attributes
        :return: attribute value
        """
        for n, v in attrs:
            if n == name:
                return v
        return ""
    
    def clean_data(self, d):
        """ Clean data block by removing special characters
        
        :param d: data block
        :return: clean data block
        """        
        data = d.rstrip().lstrip()
        data = "".join(data.split("\n"))
        data = "".join(data.split("\r"))
        data = " ".join(data.split("  "))
        return data 