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

from threading import RLock

class Cache(object):
    """ Image cache """
    
    lock = RLock()
    
    def __init__(self, util):
        """ Initializer 
        
        :param util: utility object 
        """
        self.util = util
        self.cached_images_hashes = []
        self.image_cache = {}
    
    def get_image(self, url):
        """ Get image from cache by specified url 
        
        :param url: image url 
        :return: image if in cache, None if not in cache
        """
        with self.lock:
            try:
                return self.image_cache[url]
            except:
                return None
        
    def cache_image(self, img, url):
        """ Save image in cache 
        
        :param img: image to cache
        :param url: image url 
        """
        with self.lock:
            new_url = url.encode("utf-8")
            h = self.util.get_hash(new_url)
            if h in self.cached_images_hashes:
                return
            self.image_cache[url] = img
            self.cached_images_hashes.append(h)
            
