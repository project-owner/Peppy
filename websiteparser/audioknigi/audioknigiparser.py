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

from websiteparser.audioknigi.newsparser import NewsParser
from websiteparser.audioknigi.bookparser import BookParser
from websiteparser.audioknigi.authorsparser import AuthorsParser
from websiteparser.audioknigi.constants import AUTHOR_URL_PREFIX
from websiteparser.siteparser import TOTAL_PAGES, BOOK_SUMMARIES

class AudioKnigiParser():
    """ Parser for audioknigi.club site """
    
    def __init__(self):
        """ Initializer """
        
        self.news_page_url_prefix = None
        self.news_parser = NewsParser()
        self.book_parser = BookParser()
        self.author_parser = AuthorsParser()
        self.genre_books_parser = NewsParser()

    def get_books(self, page_num):
        """ Return new books
        
        :param page_num: page number
        :return: new books
        """
        self.news_parser.url = self.news_parser.base_url + self.news_parser.page_url_prefix + str(page_num)
        self.news_parser.parse()
        return self.create_books_object(self.news_parser)

    def create_books_object(self, parser):
        """ Prepare books object
        
        :param parser: parser
        :return: book object
        """
        books = dict()
        books[TOTAL_PAGES] = parser.total_pages
        books[BOOK_SUMMARIES] = parser.items
        return books
    
    def get_book_audio_files_by_url(self, url):
        """ Get the list of audio files for defined url
        
        :param url: book url
        :return: list of audio files
        """
        self.book_parser.url = url
        self.book_parser.parse()
        return self.book_parser.playlist

    def get_authors(self):
        """ Get the list of authors
        
        :return: list of authors
        """
        self.author_parser.parse()
        return self.author_parser.items

    def get_author_books(self, author_name, author_url, page_num):
        """ Get the list of author books
        
        :param author_name: author's name
        :param author_url: author's url
        :param page_num: page number
        :return: list of author books
        """
        self.news_parser.base_url = AUTHOR_URL_PREFIX + author_name + "/"
        self.news_parser.url = author_url + self.news_parser.page_url_prefix + str(page_num)
        self.news_parser.total_pages = 0        
        self.news_parser.parse()
        return self.create_books_object(self.news_parser)
        
    def get_books_by_genre(self, genre, page_num):
        """ Get the list of genre books
        
        :param genre: genre name
        :param page_num: page number
        :return: list of genre books
        """
        self.genre_books_parser.base_url = genre
        self.genre_books_parser.url = genre + self.genre_books_parser.page_url_prefix + str(page_num)        
        self.genre_books_parser.parse()
        return self.create_books_object(self.genre_books_parser)
