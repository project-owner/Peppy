# Copyright 2023 Peppy Player peppy.player@gmail.com
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

import logging

from util.keys import *
from internetarchive import search_items, get_item
from ui.state import State
from bs4 import BeautifulSoup as soup

ARCHIVE_BASE_URL = "https://archive.org/services/search/v1/scrape"
FILE_ARCHIVE_PLAYLIST = "internetarchive.m3u"

ITEM_MENU_ROWS = 5
ITEM_MENU_COLUMNS = 1
ITEM_MENU_PAGE_SIZE = ITEM_MENU_ROWS * ITEM_MENU_COLUMNS
CACHE_MULTIPLIER = 10 
QUERY_PAGE_SIZE = ITEM_MENU_PAGE_SIZE * CACHE_MULTIPLIER

class ArchiveUtil(object):

    def __init__(self, util):
        """ Archive utility initializer
        
        :param util: utility object
        """
        self.util = util
        self.config = util.config
        self.image_util = util.image_util
        self.item_cache = {}
        self.current_query = None
        self.current_page = None

    def get_menu_page(self, query=None, menu_page=1):
        """ Get menu page
        
        :param query: query string
        :param menu_page: menu page number

        :return: tuple, where first element is a total number of all items, second - list of elements in page
        """
        items = None
        key = query + "_" + str(menu_page)

        try:
            items = self.item_cache[key]
        except:
            pass

        if items:
            return items
        
        query_page = int(menu_page / CACHE_MULTIPLIER)
        if menu_page % CACHE_MULTIPLIER != 0:
            query_page += 1

        items = self.search_archive(query, query_page)

        if not items:
            return []
        
        if len(items[1]) <= ITEM_MENU_PAGE_SIZE:
            menu_page = []
            menu_page.extend(items[1])
            self.item_cache[key] = (items[0], menu_page)
            return self.item_cache[key]
        
        page = []
        m = menu_page
        k = key

        for n, i in enumerate(items[1]):
            page.append(i)
            if n != 0 and (n + 1) % ITEM_MENU_PAGE_SIZE == 0:
                self.item_cache[k] = (items[0], page)
                page = []
                m += 1
                k = query + "_" + str(m)
            if n == len(items[1]) - 1 and page:
                k = query + "_" + str(m)
                self.item_cache[k] = (items[0], page)   

        return self.item_cache[key]
    
    def search_archive(self, query=None, page=1):
        """ Serach through Internet Archive

        :param query: search query
        :param page: page number (starts from 1)

        :return: tuple where the first element is total number of items found, second list of items
        """
        result = []

        if not query:
            return result
        
        q = f"{query} AND mediatype:audio AND NOT access-restricted-item:true"
        f = ["identifier", "title"]
        s = ["week desc"]
        p = {"rows": QUERY_PAGE_SIZE, "output": "json", "page": page, "mediatype": "audio"}

        try:
            search_result = search_items(query=q, fields=f, sorts=s, params=p)
            num_found = search_result.num_found
            for i, r in enumerate(search_result):
                s = State()
                s.index = i
                s.l_name = r["title"]
                s.identifier = s.name = r["identifier"]
                result.append(s)
        except Exception as e:
            logging.debug(e)
            return (0, [])

        return (num_found, result)
    
    def get_item(self, item_id):
        """ Get item object
        
        :param item_id: item ID

        :return: item object
        """
        item = None

        try:
            item = get_item(item_id)
        except Exception as e:
            logging.debug(e)

        return item

    def get_item_metadata(self, item):
        """ Get item metadata
        
        :param item: item object

        :return: State object
        """
        s = State()
        if not item:
            return s
        
        s.id = item.metadata["identifier"]
        s.collection = item.metadata["collection"]
        s.title = item.metadata["title"]
        s.publication_date = item.metadata["publicdate"]

        return s
    
    def get_item_description(self, item):
        """ Get item description. Not used yet
        
        :param item: item object with description as HTML object

        :return: list of description lines
        """
        content = []
        line = None

        if not item or not item.metadata:
            return content
        
        try:
            d = item.metadata["description"]
            s = soup(d, 'html.parser')
        except:
            return content

        if not s:
            return content
        
        for n, i in enumerate(s):
            if i.name == "span":
                if n == len(s) - 1:
                    line = i.text
                    content.append(line)
                    break
                if not line:
                    line = i.text
                else:
                    line += i.text
            elif i.name == "a":
                if not line:
                    line = i.text
                else:
                    line += i.text
            elif i.name == "p" or i.name == "i" or i.name == "div":
                content.append(i.text)
            elif i.name == "br":
                if line:
                    content.append(line)
                    line = None
            else:
                if i != "\n" and i != "\n\n" and i != ".\n\n":
                    if line:
                        c = line + i
                    else:
                        c = i
                    if c and "\n\n" in c:
                        lines = c.split("\n\n")
                        if lines:
                            for n in lines:
                                content.append(n)
                        else:
                            content.append(c)
                else:
                    if line:
                        content.append(line)
                        line = None

        return content
    
    def get_item_files(self, item):
        """ Get audio files from the provided item
        
        :param item: item object

        :return: list of file objects
        """
        files = []
        n = 0

        for file in item.get_files():
            if not file.name.lower().endswith(".mp3") or file.source != "original":
                continue
            state = State()
            state.url = "https://" + item.d1 + item.dir + "/" + file.name
            state.index = n
            state.item = item.identifier
            state.name = file.name
            state.size_in_bytes = file.size
            state.length_in_seconds = file.length
            title = file.name

            try:
                title = file.title
            except:
                pass

            if not title[0].isdigit():
                state.title = state.l_name = str(n + 1) + ". " + title
            else:
                state.title = state.l_name = title

            files.append(state)
            n += 1

        return files
    
    def get_file(self, id, files):
        """ Get file info by ID
        
        :param id: file ID
        :param files: list of files metadata

        :return: file metadata
        """
        for file in files:
            if file.index == int(id):
                return file
            
        return None

    def get_item_logo_url(self, item):
        """ Get logo image URL from the item object
        
        :param item: item object

        :return: image URL
        """
        logo = None
        image_files = ["jpg", "jpeg", "png"]
            
        for file in item.get_files():
            index = file.name.rfind(".")
            file_extension = file.name[index + 1:]
            if file_extension.lower() not in image_files or file.source != "original":
                continue
            logo = "https://" + item.d1 + item.dir + "/" + file.name
            break

        return logo			
