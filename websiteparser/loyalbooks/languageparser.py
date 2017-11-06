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

from websiteparser.loyalbooks.newsparser import NewsParser
from websiteparser.loyalbooks.constants import RESULTS_100, PAGE_PREFIX

class LanguageParser(NewsParser):
    """ Parser for book pages in different languages e.g. French etc """
    
    def __init__(self, url=None):
        """ Initializer
        
        :param url: current url
        """
        NewsParser.__init__(self, url)
        self.current_page = 1
        self.language_url = ""

    def parse(self, page_num):
        """ Start page parsing
        
        :param page_num: page number
        """
        if page_num == 1:
            self.url = self.base_url + self.language_url[0 : -1] + RESULTS_100
        else:
            self.url = self.base_url + self.language_url[0 : -1] + RESULTS_100 + PAGE_PREFIX + str(page_num)
        self.items = self.get_from_cache()
        if self.items: return 
        
        self.total_pages = 10
        
        self.url = self.get_url(page_num)
        self.parse_page(p=page_num)                   
    
    def get_url(self, page_num):
        """ Prepare site url from defined page number
        
        :param page_num: page number
        :return: real site url
        """
        self.site_page_num = n = int(page_num / self.page_size)
        if self.site_page_num < self.page_size + 1:
            n += 1
                
        if n == 1:
            u = self.base_url + self.language_url[0 : -1] + RESULTS_100
        else:
            u = self.base_url + self.language_url[0 : -1] + RESULTS_100 + PAGE_PREFIX + str(n)
        
        return u
    
    def is_in_cache(self, url, current_page=None):
        """ Check if page with defined url is in cache
        
        :param url: page url
        :param current_page: current page
        :return: True - page in cache, False - page is not in cache
        """
        u = self.base_url + self.language_url[0 : -1] + RESULTS_100 + PAGE_PREFIX + str(current_page - 1)
        
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
            lang = self.language_url[0 : -1]           
            u = self.base_url + lang + RESULTS_100 + PAGE_PREFIX + str(k)
            start = n * self.page_size 
            self.cache[u] = self.items[start : start + self.page_size]
