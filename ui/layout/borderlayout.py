# Copyright 2016-2021 Peppy Player peppy.player@gmail.com
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

import pygame

class BorderLayout(object):
    """ Prepares the list of bounding boxes for placing components on Top, Bottom, Left, Right and Center """
    
    def __init__(self, bb):
        """ Initializer
        
        :param bb: bounding box for the whole component
        """
        self.x, self.y = bb.x, bb.y
        self.w, self.h = bb.width, bb.height
        self.TOP = self.BOTTOM = self.LEFT = self.RIGHT = self.CENTER = None 
        self.constraints = [self.TOP, self.BOTTOM, self.LEFT, self.RIGHT, self.CENTER]
        self.current_constraints = 0
    
    def get_next_constraints(self):
        """ Return bounding box for the next layout component 
        
        :return: next bounding box
        """
        const = self.constraints[self.current_constraints]
        if self.current_constraints + 1 < len(self.constraints):
            self.current_constraints += 1
        else:
            self.current_constraints = 0
        return const
    
    def set_percent_constraints(self, top_percent, bottom_percent, left_percent, right_percent):
        """ Create bounding boxes for each screen part (TOP, BOTTOM, LEFT, RIGHT, CENTER).        
        The parameters define constraints in percents. The center component is always using remaining space
        
        :param top_percent: percentage for top component
        :param bottom_percent:  percentage for bottom component
        :param left_percent:  percentage for left component
        :param right_percent:  percentage for right component
        """
        top_height = bottom_height = left_width = right_width = 0
        center_height = self.h
        
        if top_percent != 0:
            top_height = int((self.h/100.0) * top_percent)
            self.TOP = pygame.Rect(self.x, self.y, self.w, top_height)
        
        if bottom_percent != 0:
            bottom_height = int((self.h/100.0) * bottom_percent)
            self.BOTTOM = pygame.Rect(self.x, self.h - bottom_height + self.y, self.w, bottom_height)
        
        if left_percent != 0:
            left_width = int((self.w/100.0) * left_percent)
            left_height = int(self.h - top_height - bottom_height)
            self.LEFT = pygame.Rect(self.x, self.y + top_height, left_width, left_height)
        
        if right_percent != 0:
            right_width = int((self.w/100.0) * right_percent)
            right_height = int(self.h - top_height - bottom_height)
            self.RIGHT = pygame.Rect(self.x + self.w - right_width, self.y + top_height, right_width, right_height)

        center_y = self.y
        if top_height > 0:
            center_height -= (top_height)
            center_y = self.y + top_height
            if bottom_height == 0:
                center_height += 1
        if bottom_height > 0:
            center_height -= (bottom_height)
        
        center_width = self.w - left_width - right_width        
        self.CENTER = pygame.Rect(left_width + self.x, center_y, center_width, center_height)
        
        if self.BOTTOM:
            bottom_edge = center_y + center_height
            self.BOTTOM.y = bottom_edge + 1
            self.BOTTOM.h = self.y + self.h - self.BOTTOM.y - 1
        
    def set_pixel_constraints(self, top_pixels, bottom_pixels, left_pixels, right_pixels):
        """ Create bounding boxes for each screen part (TOP, BOTTOM, LEFT, RIGHT, CENTER).        
        The parameters define constraints in pixels. The center component is always using remaining space
        
        :param top_pixels: pixels for top component
        :param bottom_pixels:  pixels for bottom component
        :param left_pixels:  pixels for left component
        :param right_pixels:  pixels for right component
        """
        if top_pixels != 0:
            self.TOP = pygame.Rect(self.x, self.y, self.w, top_pixels)
        
        if bottom_pixels != 0:
            self.BOTTOM = pygame.Rect(self.x, self.h - bottom_pixels + self.y, self.w, bottom_pixels)
        
        if left_pixels != 0:
            left_height = self.h - top_pixels - bottom_pixels
            self.LEFT = pygame.Rect(self.x, top_pixels, left_pixels, left_height)
        
        if right_pixels != 0:
            left_height = self.h - top_pixels - bottom_pixels
            self.RIGHT = pygame.Rect(self.w - right_pixels, top_pixels, right_pixels, left_height)
        
        self.CENTER = pygame.Rect(left_pixels + self.x, top_pixels + self.y, self.w - left_pixels - right_pixels - 1, self.h - top_pixels - bottom_pixels)
        