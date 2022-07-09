# Copyright 2022 PeppyMeter peppy.player@gmail.com
# 
# This file is part of PeppyMeter.
# 
# PeppyMeter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PeppyMeter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PeppyMeter. If not, see <http://www.gnu.org/licenses/>.

import pygame
from PIL import Image

class SpectrumUtil(object):
    """ Utility class """
    
    def __init__(self):
        """ Initializer """

        self.image_cache = {}
    
    def load_pygame_image(self, path):
        """ Check if image is in the cache.
         
        If yes, return the image from the cache.
        If not load image file and place it in the cache.
        
        :param path: image path
        
        :return: pygame image
        """
        image = None
        try:
            i = self.image_cache[path]            
            return (path, i)
        except KeyError:
            pass
            
        try:            
            image = pygame.image.load(path).convert_alpha()
        except:
            pass
            
        if image:
            self.image_cache[path] = image
            return (path, image)
        else:
            return None

    def scale_image(self, image, ratio):
        """ Scale image using specified ratio
        
        :param image: image to scale
        :param ratio: scaling ratio
              
        :return: scaled image
        """
        if image == None:
            return None
        s = pygame.Surface(ratio, flags=pygame.SRCALPHA)
        if isinstance(image, tuple):
            image = image[1]

        d = pygame.image.tostring(image, "RGBA", False)
        img = Image.frombytes("RGBA", image.get_size(), d)
        i = img.resize(ratio)
        d = pygame.image.fromstring(i.tobytes(), i.size, i.mode)
        s.blit(d, (0, 0))

        return s
