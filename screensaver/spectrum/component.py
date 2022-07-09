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

class Component(object):
    """ Represent the lowest UI component level.    
    This is the only class which knows how to draw on Pygame Screen.
    """
    
    def __init__(self, util, c=None, x=0, y=0, bb=None, fgr=(0, 0, 0), bgr=(0, 0, 0), v=True, t=0):
        """ Initializer
        
        :param util: utility object
        :param c: component content
        :param x: component coordinate X on Pygame Screen
        :param y: component coordinate Y on Pygame Screen
        :param bb: component bounding box
        :param fgr: component foreground
        :param bgr: component background
        :param v: visibility flag, True - visible, False - invisible 
        """
        self.screen = None
        self.screen = util.pygame_screen
        self.content = c
        self.content_x = x
        self.content_y = y
        if bb: 
            self.bounding_box = pygame.Rect(bb.x, bb.y, bb.w, bb.h)
        else:
            self.bounding_box = None
        self.fgr = fgr       
        self.bgr = bgr
        self.visible = v
        self.text = None
        self.text_size = None
        self.image_filename = None
        self.parent_screen = None
        self.border_thickness = t

    def clean(self):
        """ Clean component by filling its bounding box by background color """
        
        if not self.visible: 
            return

        if self.parent_screen:
            self.parent_screen.draw_area(self.bounding_box)
        elif self.bgr: 
            self.draw_rect(self.bgr, self.bounding_box, t=self.border_thickness)
    
    def draw(self, bb=None):
        """ Dispatcher drawing method.        
        Distinguishes between Rectangle and Image components.
        Doesn't draw invisible component. 
        """
        if not self.visible or not hasattr(self, "content"): return
        
        if isinstance(self.content, pygame.Rect):
            pass
            if self.bgr:
                if bb:
                    a = bb
                else:
                    a = self.content

                self.draw_rect(self.bgr, r=a, t=self.border_thickness)
        elif isinstance(self.content, pygame.Surface) or isinstance(self.content, tuple):
            if bb:
                self.draw_image(self.content, bb.x, bb.y, bb)
            else:
                self.draw_image(self.content, self.content_x, self.content_y)
    
    def draw_rect(self, f, r, t=0):
        """ Draw Rectangle on Pygame Screen
        
        :param f: outline color
        :param r: rectangle object
        :param t: outline thickness
        """
        if not self.visible: return
        if self.screen:
            if not isinstance(f, tuple):
                f = getattr(f, "bgr", (0,0,0))

            if len(f) == 4:
                s = pygame.Surface((r.w, r.h))
                s.set_alpha(f[3])
                s.fill((f[0], f[1], f[2]))
                self.screen.blit(s, (r.x, r.y))
            else:
                try:
                    if t == 0:
                        pygame.draw.rect(self.screen, f, r, t)
                    else:
                        pygame.draw.line(self.screen, f, (r.x - t/2, r.y - 1), (r.x + r.w, r.y - 1), t)
                        pygame.draw.line(self.screen, f, (r.x - t/2, r.y + r.h - 1), (r.x + r.w, r.y + r.h - 1), t)
                        pygame.draw.line(self.screen, f, (r.x - 1, r.y - 1), (r.x - 1, r.y + r.h - 1), t)
                        pygame.draw.line(self.screen, f, (r.x + r.w - 1, r.y - t/2), (r.x + r.w - 1, r.y + r.h + t/2 -1), t)
                        self.fgr = None
                except:
                    pass                
    
    def draw_image(self, c, x, y, bb=None):
        """ Draw Image on Pygame Screen
        
        :param c: image
        :param x: coordinate X of the image top-left corner on Pygame Screen
        :param y: coordinate Y of the image top-left corner on Pygame Screen
        """
        comp = c
        if isinstance(c, tuple):        
            comp = c[1]

        if comp and self.screen:
            try:
                if self.bounding_box != None:
                    if bb:
                        a = bb
                    else:
                        a = self.bounding_box

                    if isinstance(self.content, tuple):
                        self.screen.blit(self.content[1], (self.content_x, self.content_y), a)
                    else:
                        self.screen.blit(self.content, (x, y), a)
                else:
                    if bb:
                        self.screen.blit(comp, (x, y), bb)
                    else:
                        self.screen.blit(comp, (x, y))
            except:
                pass
 
    def update(self):
        """ Update Pygame Screen """
        
        if not self.visible: return
        pygame.display.update(self.bounding_box)
        
    def update_rectangle(self, r):
        """ Update Pygame Screen """
        
        if not self.visible: return
        pygame.display.update(r)      
        
    def set_visible(self, flag):
        """ Set component visibility 
        
        :param flag: True - component visible, False - component invisible
        """
        self.visible = flag
        
    def refresh(self):
        """ Refresh component. Used for periodical updates  animation. """
        
        pass
