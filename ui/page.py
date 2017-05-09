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

""" Page module """

class Page(object):
    """ Keep the info about current list, current item etc """
    
    def __init__(self, items, rows=3, columns=3):
        """ Initializer
        
        :param items: list items
        :param rows: number of rows in menu
        :param columns: number of columns in menu
        """
        self.rows = rows
        self.columns = columns
        self.items_per_page = rows * columns
        self.items = items
        self.current_page_index = 0
        self.current_item_index = 0
        self.current_item_page_index = 0
        self.current_item_index_in_page = 0 
        self.current_item = None
        self.length = 0
        if self.items: self.length = len(self.items)
        self.total_pages = 0
        self.grid_size = 0
        self.start_listeners = list()        
        self.grid_size = 3
        self.total_pages = int(self.length/self.items_per_page)
        if(self.length % self.items_per_page):
            self.total_pages += 1
            
    def set_current_item(self, index):
        """ Set the current item by its index
        
        :param index: the item index 
        """
        if index > self.length - 1:
            index = self.length - 1
        
        if index == -1:
            return
         
        self.current_item_index = index
        self.current_item_index_in_page = index % self.items_per_page
        self.current_page_index = int(index/self.items_per_page)
        self.current_item_page_index = self.current_page_index
        page = self.get_current_page()
        index_in_page = index % self.items_per_page
        self.current_item = page[index_in_page]    
    
    def set_current_item_by_url(self, url):
        """ Set the current item by its URL
        
        :param url: item URL
        """ 
        if self.items == None: return
        
        index = None
        if url.startswith("\"") and url.endswith("\""):
            url = url[1:-1]
        for item in self.items:
            if item.url == url:
                index = item.index
                break
            
        if index:
            self.set_current_item(index)
    
    def get_current_page(self):
        """ Get the current page for the current item
         
        :return: list of the items representing the page where the current item belongs to
        """
        if self.items == None: return None
                
        start = self.current_page_index * self.items_per_page
        stop = start + self.items_per_page
        if len(self.items) > stop:
            return self.items[start:stop]            
        else: 
            return self.items[start:]
    
    def next_page(self):
        """ Move to the next page of items. Move to the first page if the current page is the last one.
        
        :return: list of the items representing the next page
        """
        if self.current_page_index + 1 == self.total_pages:
            self.current_page_index = 0
        else:
            self.current_page_index += 1
        return self.get_current_page()
    
    def previous_page(self):
        """ Move to the previous page of items. Move to the last page if the current page is the first one.
        
        :return: list of items representing the previous page
        """        
        if self.current_page_index == 0:
            self.current_page_index = self.total_pages - 1
        else:
            self.current_page_index -= 1
        return self.get_current_page()
    
    def get_left_items_number(self):
        """ Return number of items on the left side from the current item
        
        :return: number of left items
        """
        return self.current_page_index * self.items_per_page
    
    def get_right_items_number(self):
        """ Return number of items on the right side from the current item
        
        :return: number of right items
        """
        n = self.length -((self.current_page_index + 1) * self.items_per_page)
        if n < 0:
            return  0
        else:
            return n  
        
