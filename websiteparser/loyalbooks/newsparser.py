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

from websiteparser.siteparser import SiteParser, TABLE, UL, A, TD, BOOK_URL, HREF, IMG, \
    IMG_URL, SRC, B, DIV, RATING, ID, BOOK_TITLE, AUTHOR_NAME
from websiteparser.loyalbooks.constants import BASE_URL, BOOKS_PAGE_SIZE, DEFAULT_IMAGE

class NewsParser(SiteParser):
    """ Parser for new books pages """
    
    def __init__(self, url=None):
        """ Initializer
        
        :param url: current url
        """
        SiteParser.__init__(self, BASE_URL, url)
        self.book = None
        self.page_url_prefix = None
        self.total_pages = 10
        self.site_page_num = 1
        self.page_size = BOOKS_PAGE_SIZE
        self.cache_base_url = None
        
        self.found_pages_table = False
        self.found_pages_ul = False
        self.found_pages_a = False
        self.found_books_table = False
        self.found_book_td = False
        self.found_book_a = False
        self.found_book_b = False
        
        self.found_books_list_table = False
        self.found_book_list_td = False
        self.found_book_list_div = False
        self.found_book_list_a = False
        self.found_book_title = False
        
        self.items_num = 0
    
    def parse(self, page_num):
        """ Prepare url for parsing
        
        :param page_num: page number
        """
        self.url = BASE_URL + self.page_url_prefix + str(page_num)
        self.items = self.get_from_cache()
        if self.items: return 
        
        self.total_pages = 10
        
        self.url = self.get_url(page_num)
        self.parse_page(p=page_num)           
    
    def parse_page(self, cache_books=True, p=None):
        """ Start page parsing
        
        :param cache_books: flag defining if books should be cached
        :param p: page number
        """
        self.items = []
        page = self.get_page()
        self.feed(page)
        if cache_books:
            self.cache_books()
        self.items_num = len(self.items)
        if p:   
            i = int((str(p)[-1]))           
            s = i * self.page_size
            self.items = self.items[s : s + self.page_size]
        else:
            self.items = self.items[0 : self.page_size]

    def get_url(self, page_num):
        """ Prepare site url from defined page number
        
        :param page_num: page number
        :return: real site url
        """
        self.site_page_num = n = int(page_num / self.page_size)
        if self.site_page_num < self.page_size + 1:
            n += 1
                
        u = BASE_URL + self.page_url_prefix + str(n)
        
        return u
    
    def is_in_cache(self, url, current_page=None):
        """ Check if page with defined url is in cache
        
        :param url: page url
        :param current_page: current page
        :return: True - page in cache, False - page is not in cache
        """
        p = url[url.rfind("/") + 1:]
        n = int(p) - 1
        u = url[0 : url.rfind("/")] + "/" + str(n)
        
        try:
            self.cache[u]
        except:
            return False
        return True

    def cache_books(self):
        """ Cache current books """
        
        pages = math.ceil(len(self.items) / self.page_size)
        
        if len(self.cache) + pages > self.CACHE_SIZE:
            return
        
        for n in range(pages):
            k = self.site_page_num * self.page_size + n            
            u = BASE_URL + self.page_url_prefix + str(k)
            start = n * self.page_size 
            
            self.cache[u] = self.items[start : start + self.page_size]

    def handle_starttag(self, tag, attrs):
        """ Handle starting html tag
        
        :param tag: tag name
        :param attrs: tag attributes
        """
        if tag == TABLE and self.is_required_tag(TABLE, "Title", tag, attrs):
            self.found_pages_table = True
        elif tag == UL and self.found_pages_table:
            self.found_pages_ul = True
        elif tag == A and self.found_pages_ul:
            self.found_pages_a = True
        elif tag == TABLE and self.is_required_tag(TABLE, "Audio books", tag, attrs) and self.is_required_tag(TABLE, "layout2-blue", tag, attrs):
            self.found_books_table = True
        elif tag == TD and self.found_books_table and self.is_required_tag(TD, "25%", tag, attrs):
            self.found_book_td = True
            self.book = {}            
        elif tag == A and self.found_book_td:
            self.found_book_a = True
            self.book[BOOK_URL] = BASE_URL[:-1] + self.get_attribute(HREF, attrs)
        elif tag == IMG and self.found_book_a:
            self.book[IMG_URL] = BASE_URL[:-1] + self.get_attribute(SRC, attrs)
        elif tag == B and self.found_book_a:
            self.found_book_b = True
        elif tag == DIV and self.found_book_a:
            self.book[RATING] = int(self.get_attribute(ID, attrs)[4:])
        elif tag == TABLE and self.is_required_tag(TABLE, "Audio books", tag, attrs) and self.is_required_tag(TABLE, "layout3", tag, attrs):
            self.found_books_list_table = True            
        elif tag == TD and self.found_books_list_table and self.is_required_tag(TD, "50%", tag, attrs):
            self.found_book_list_td = True
            self.book = {}            
        elif tag == DIV and self.found_book_list_td and self.is_required_tag(DIV, "star", tag, attrs):
            self.book[RATING] = int(self.get_attribute(ID, attrs)[4:])
        elif tag == DIV and self.found_book_list_td and self.is_required_tag(DIV, "s-left", tag, attrs):
            self.found_book_list_div = True
        elif tag == A and self.found_book_list_div:
            self.found_book_list_a = True
            self.book[BOOK_URL] = BASE_URL[:-1] + self.get_attribute(HREF, attrs)            
            
    def handle_endtag(self, tag):
        """ Handle ending html tag
        
        :param tag: tag name
        """
        if tag == TABLE and self.found_pages_table:
            self.found_pages_table = False
        elif tag == UL and self.found_pages_ul:
            self.found_pages_ul = False
        elif tag == A and self.found_pages_a:
            self.found_pages_a = False
        elif tag == TABLE and self.found_books_table:
            self.found_books_table = False
        elif tag == TD and self.found_book_td:
            self.found_book_td = False
            self.add_book()
        elif tag == A and self.found_book_a:
            self.found_book_a = False
        elif tag == B and self.found_book_b:
            self.found_book_b = False
        elif tag == TABLE and self.found_books_list_table:
            self.found_books_list_table = False
        elif tag == TD and self.found_book_list_td:
            self.found_book_list_td = False
            self.add_book()
        elif tag == DIV and self.found_book_list_div:
            self.found_book_list_div = False
        elif tag == A and self.found_book_list_a:
            self.found_book_list_a = False
        
    def handle_data(self, data):
        """ Handle tag data block
        
        :param data: tag data string
        """
        data = self.clean_data(data)
        if len(data) == 0: return
  
        if self.found_pages_ul and not self.found_pages_a:
            r = data.split()
            self.total_pages = int(r[3]) * 10
            self.found_pages_ul = False
        elif self.found_book_b:
            self.book[BOOK_TITLE] = data
        elif self.found_book_td:            
            self.book[AUTHOR_NAME] = data
        elif self.found_book_list_div and not self.found_book_title:
            self.book[BOOK_TITLE] = data
            self.found_book_title = True            
        elif self.found_book_list_div and self.found_book_title:
            self.book[AUTHOR_NAME] = data[4:]
            self.found_book_title = False            
    
    def add_book(self):
        """ Add book to the list """
                     
        try:
            self.book[BOOK_TITLE]
        except:
            return
        
        img_url = None
        try:
            img_url = self.book[IMG_URL]
        except:
            pass               
        if img_url == None:
            self.book[IMG_URL] = DEFAULT_IMAGE
        self.items.append(self.book)
        

