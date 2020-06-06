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

import math

from websiteparser.loyalbooks.newsparser import NewsParser
from websiteparser.loyalbooks.genreparser import GenreParser
from websiteparser.loyalbooks.languageparser import LanguageParser
from websiteparser.loyalbooks.bookparser import BookParser
from websiteparser.siteparser import TOTAL_PAGES, BOOK_SUMMARIES

from websiteparser.loyalbooks.constants import PAGE_PREFIX, TOP_100, BASE_URL, \
    RESULTS_100, BOOKS_PAGE_SIZE

class LoyalBooksParser():
    """ Parser for loyalbooks site """
    
    def __init__(self):
        """ Initializer """
        
        self.news_parser = NewsParser()
        self.genre_books_parser = GenreParser()
        self.book_parser = BookParser()
        self.language_parser = LanguageParser()

    def get_books(self, page_num, language_url=""): 
        """ Return new books
        
        :param page_num: page number
        :param language_url: language constant
        :return: books
        """ 
        
        if language_url == None or len(language_url.strip()) == 0:
            p = self.news_parser
        else:
            p = self.language_parser
            
        p.parse(page_num - 1)
        books = self.create_books_object(p)
        
        if len(self.language_url) == 0:
            tmp_parser = NewsParser()
        else:
            tmp_parser = LanguageParser()
        
        tmp_parser.page_url_prefix = TOP_100
        num = int(p.total_pages / BOOKS_PAGE_SIZE)
        
        if p.site_total_pages == 0:
            if len(self.language_url) == 0:
                tmp_parser.url = BASE_URL + tmp_parser.page_url_prefix + str(num)
            else:
                tmp_parser.url = BASE_URL + self.language_url[0 : -1] + RESULTS_100 + PAGE_PREFIX + str(num)
                p.total_pages -= 1
            
            tmp_parser.parse_page(cache_books=False)
            self.set_total_pages(p, tmp_parser, books)
            
            p.site_total_pages = books[TOTAL_PAGES]
        else:
            books[TOTAL_PAGES] = p.site_total_pages

        return books

    def create_books_object(self, parser):
        """ Prepare books object
        
        :param parser: parser
        :return: book object
        """
        books = dict()
        books[TOTAL_PAGES] = parser.total_pages
        books[BOOK_SUMMARIES] = parser.items
        return books
    
    def get_book_audio_files_by_url(self, url, img_url):
        """ Get the list of audio files for defined url
        
        :param url: book url
        :return: list of audio files
        """
        self.book_parser.url = url
        self.book_parser.parse()
        return self.book_parser.playlist

    def get_books_by_genre(self, genre, page_num):
        """ Get the list of genre books
        
        :param genre: genre name
        :param page_num: page number
        :return: list of genre books
        """
        p = self.genre_books_parser
        p.parse(page_num - 1, genre)
        books = self.create_books_object(p)        
        num = int(p.total_pages / BOOKS_PAGE_SIZE)       
        tmp_parser = GenreParser()
        
        if p.site_total_pages == 0:
            tmp_parser.url = p.genre_url + RESULTS_100 + PAGE_PREFIX + str(num)
            tmp_parser.parse_page(cache_books=False)
            reminder = tmp_parser.items_num 
            n = (num - 1) * 100 + reminder
            books[TOTAL_PAGES] = (math.ceil(n / BOOKS_PAGE_SIZE))
            p.site_total_pages = books[TOTAL_PAGES]
        else:
            books[TOTAL_PAGES] = p.site_total_pages

        return books
    
    def set_total_pages(self, prev_parser, tmp_parser, books):
        """ Set the real number of pages on books object
        
        :param prev_parser: previous parser
        :param tmp_parser: temporary parser
        :param books: books object
        """
        reminder = tmp_parser.items_num        
        site_num = int(prev_parser.total_pages / BOOKS_PAGE_SIZE)
        total_books = site_num * 100 + reminder
        books[TOTAL_PAGES] = (math.ceil(total_books / BOOKS_PAGE_SIZE))
        
    
