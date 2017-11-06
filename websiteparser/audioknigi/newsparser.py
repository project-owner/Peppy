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

import math

from websiteparser.siteparser import SiteParser, ARTICLE, IMG, IMG_URL, \
    SRC, HEADER, H3, A, HREF, BOOK_URL, GENRE_URL, DIV, AUTHOR_URL, \
    PERFORMER_URL, I, B, UL, BOOK_TITLE, GENRE_NAME, AUTHOR_NAME, \
    PERFORMER_NAME, ANNOTATION, TOTAL_TIME
from websiteparser.audioknigi.constants import LAST, V_RAZDELE
from websiteparser.audioknigi.constants import BASE_URL

class NewsParser(SiteParser):
    """ Parser for new books page """
    
    def __init__(self, url=None):
        """ Initializer
        
        :param url: current url
        """
        SiteParser.__init__(self, BASE_URL, url)
        self.page_url_prefix = None       
        self.book = None
        
        self.found_article = False
        self.found_header = False
        self.found_h3 = False
        self.found_a = False
        self.found_topic_blog = False
        self.found_genre_a = False
        self.found_misc_div = False
        self.found_author = False
        self.found_performer = False
        self.found_topic_div = False
        self.found_info_div = False
        self.found_time_i = False        
        self.found_time = False
        self.found_total_books = False
        self.found_total_books_b = False
        self.found_pagination = False
    
    def is_in_cache(self, url, current_page=None):
        """ Doesn't use cache """        
        return False
    
    def get_url(self, p, current_genre):
        """ NA """
        pass
        
    def handle_starttag(self, tag, attrs):
        """ Handle starting html tag
        
        :param tag: tag name
        :param attrs: tag attributes
        """
        if tag == ARTICLE:
            self.found_article = True
            self.book = {}
        elif tag == IMG and self.found_article:
            self.book[IMG_URL] = self.get_attribute(SRC, attrs)
        elif tag == HEADER:
            self.found_header = True
        elif tag == H3 and self.found_header:
            self.found_h3 = True
        elif tag == A and self.found_h3:
            self.book[BOOK_URL] = self.get_attribute(HREF, attrs)
            self.found_a = True
        elif tag == A and self.found_topic_blog:
            self.book[GENRE_URL] = self.get_attribute(HREF, attrs)
            self.found_genre_a = True
        elif tag == DIV and self.found_header and self.is_required_tag(DIV, "topic-blog", tag, attrs):
            self.found_topic_blog = True
        elif tag == DIV and self.is_required_tag(DIV, "topic-content text", tag, attrs):
            self.found_misc_div = True
        elif tag == A and self.found_misc_div and self.is_required_tag(A, "author", tag, attrs):
            self.book[AUTHOR_URL] = self.get_attribute(HREF, attrs)
            self.found_author = True
        elif tag == A and self.found_misc_div and self.is_required_tag(A, "performer", tag, attrs):
            self.book[PERFORMER_URL] = self.get_attribute(HREF, attrs)
            self.found_performer = True
        elif tag == DIV and self.found_misc_div and self.is_required_tag(DIV, "topic-a-info", tag, attrs):
            self.found_topic_div = True
        elif tag == DIV and self.found_topic_div and self.is_required_tag(DIV, "a-info-item", tag, attrs):
            self.found_info_div = True
            self.tmp_div_data = None
        elif tag == I and self.is_required_tag(I, "fa fa-clock-o", tag, attrs):
            self.found_time_i = True
        elif tag == DIV and self.is_required_tag(DIV, "author-desc", tag, attrs):
            self.found_total_books = True
        elif tag == B and self.found_total_books:
            self.found_total_books_b = True
        elif tag == UL and self.is_required_tag(UL, "pagination", tag, attrs):
            self.found_pagination = True
        elif self.found_pagination and tag == A and self.is_required_tag(A, LAST, tag, attrs):
            a = None
            try:
                a = self.pages[self.url]
            except:
                pass
            
            if a != None:
                return            
            a = self.get_attribute(HREF, attrs)
            i = a.find(self.page_url_prefix) + len(self.page_url_prefix)
            self.total_pages = int(a[i : -1])
            self.pages[self.url] = self.total_pages
            
    def handle_endtag(self, tag):
        """ Handle ending html tag
        
        :param tag: tag name
        """
        if tag == ARTICLE and self.found_article:
            self.found_article = False
            self.items.append(self.book)
        elif tag == HEADER and self.found_article:
            self.found_header = False
        elif tag == H3 and self.found_header:
            self.found_h3 = False
        elif tag == A:
            if self.found_h3:
                self.found_a = False
            elif self.found_genre_a:
                self.found_genre_a = False
            elif self.found_author:
                self.found_author = False
            elif self.found_performer:
                self.found_performer = False
        elif tag == DIV:
            if self.found_topic_blog:
                self.found_topic_blog = False
            elif self.found_topic_div:
                self.found_topic_div = False
            elif self.found_misc_div:
                self.found_misc_div = False
            elif self.found_info_div:
                self.found_info_div = False
            elif self.found_header:
                self.found_a = False
        elif tag == I and self.found_time_i:
            self.found_time_i = False
            self.found_time = True
        elif tag == UL and self.found_pagination:
            self.found_pagination = False
        elif tag == B and self.found_total_books_b:
            self.found_total_books_b = False
            self.found_total_books = False
        
    def handle_data(self, data):
        """ Handle tag data block
        
        :param data: tag data string
        """
        data = self.clean_data(data)
        if len(data) == 0: return
 
        if self.found_a:
            s = data.split(" - ")
            if len(s) == 1:
                self.book[BOOK_TITLE] = s[0].rstrip().lstrip()
            else:
                self.book[BOOK_TITLE] = s[1].rstrip().lstrip()             
        elif self.found_genre_a:
            self.book[GENRE_NAME] = data
        elif self.found_author:
            self.book[AUTHOR_NAME] = data
        elif self.found_performer:
            self.book[PERFORMER_NAME] = data
        elif self.found_misc_div and not self.found_topic_div:
            self.book[ANNOTATION] = data
        elif self.found_time:
            self.book[TOTAL_TIME] = data
            self.found_time = False
        elif self.found_total_books:
            if data.startswith(V_RAZDELE):
                return
            else:
                s = data.split(" ")
                if len(s) == 1:
                    return
                self.total_pages = math.ceil(int(s[0])/12)
                self.found_total_books = False            
            self.pages[self.url] = self.total_pages
            
    

    
