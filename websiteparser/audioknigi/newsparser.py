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
import logging

from websiteparser.siteparser import SiteParser, ARTICLE, IMG, IMG_URL, \
    SRC, HEADER, H2, H3, A, HREF, BOOK_URL, GENRE_URL, DIV, AUTHOR_URL, \
    PERFORMER_URL, I, B, UL, BOOK_TITLE, GENRE_NAME, AUTHOR_NAME, \
    PERFORMER_NAME, ANNOTATION, TOTAL_TIME, SPAN, LI
from websiteparser.audioknigi.constants import LAST, V_RAZDELE
from websiteparser.audioknigi.constants import BASE_URL
from websiteparser.audioknigi.constants import BOOK_URL as BOOK_LINK

class NewsParser(SiteParser):
    """ Parser for new books page """
    
    def __init__(self, url=None):
        """ Initializer
        
        :param url: current url
        """
        SiteParser.__init__(self, BASE_URL, url)
        self.page_url_prefix = None       
        self.book = None
        
        self.found_book_section = False
        self.found_genre = False
        self.found_cover = False
        self.found_title = False
        self.found_page_nav = False
        self.found_page_link = False

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
        if tag == DIV and self.is_required_tag(DIV, "content__main__articles--item", tag, attrs):
            self.found_book_section = True
            self.book = {}
            self.book[BOOK_URL] = BOOK_LINK + attrs[1][1]
        elif tag == DIV and self.found_book_section and self.is_required_tag(DIV, "article--cover", tag, attrs):
            self.found_cover = True
        elif tag == A and self.found_book_section and self.is_required_tag(A, "section__title", tag, attrs):
            self.book[GENRE_URL] = attrs[0][1]
            self.found_genre = True
        elif tag == IMG and self.found_cover:
            self.book[IMG_URL] = self.get_attribute(SRC, attrs)
        elif tag == H2 and self.found_book_section and self.is_required_tag(H2, "caption__article-main", tag, attrs):
            self.found_title = True
        elif tag == DIV and self.is_required_tag(DIV, "page__nav", tag, attrs):
            self.found_page_nav = True
            self.page_links = []
        elif tag == A and self.found_page_nav:
            self.found_page_link = True

    def handle_endtag(self, tag):
        """ Handle ending html tag
        
        :param tag: tag name
        """
        if tag == DIV:
            if self.found_book_section and self.found_cover == False:
                author_found = False
                try:
                    self.book[AUTHOR_NAME]
                    author_found = True
                except:
                    pass
                if author_found:
                    self.found_book_section = False
                    self.items.append(self.book)
            elif self.found_cover:
                self.found_cover = False
            elif self.found_page_nav:
                self.found_page_nav = False
                try:
                    self.total_pages = max(self.page_links)
                    self.pages[self.url] = self.total_pages
                except:
                    pass
        elif tag == A:
            if self.found_genre:
                self.found_genre = False
            elif self.found_page_link:
                self.found_page_link = False
        elif tag == H2:
            if self.found_title:
                self.found_title = False

    def handle_data(self, data):
        """ Handle tag data block
        
        :param data: tag data string
        """
        data = self.clean_data(data)
        if len(data) == 0: return

        if self.found_genre:
            self.book[GENRE_NAME] = data
        elif self.found_title:
            s = data.split(" - ")
            if len(s) == 1:
                self.book[BOOK_TITLE] = s[0].rstrip().lstrip()
                self.book[AUTHOR_NAME] = ""
            else:
                self.book[BOOK_TITLE] = s[1].rstrip().lstrip()
                self.book[AUTHOR_NAME] = s[0].rstrip().lstrip()
        elif self.found_page_link:
            try:
                i = int(data)
                self.page_links.append(i)
            except:
                pass
