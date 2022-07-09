# Copyright 2018-2022 Peppy Player peppy.player@gmail.com
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
import time
import logging
import sys
import os

from component import Component
from container import Container
from random import randrange
from threading import Thread
from itertools import cycle
from screensaverspectrum import ScreensaverSpectrum
from spectrumutil import SpectrumUtil
from spectrumconfigparser import *

class Spectrum(Container, ScreensaverSpectrum):
    """ Spectrum Analyzer screensaver plug-in. """
        
    def __init__(self, util=None, standalone=False):
        """ Initializer
        
        :param util: the utility functions
        :param standalone: True - run as a standalone program, False - run as a plugin
        """
        self.name = "spectrum"
        self.standalone = standalone
        self.use_test_data = True
        plugin_folder = type(self).__name__.lower()
        ScreensaverSpectrum.__init__(self, self.name, util, plugin_folder)

        if util:
            self.util = util
            self.image_util = util.image_util
        else:
            self.util = SpectrumUtil()
            self.image_util = self.util
        
        self.run_flag = False
        self.run_datasource = False
        self.config_parser = SpectrumConfigParser(self.standalone)
        self.config = self.config_parser.config
        self.update_period = self.config[UPDATE_PERIOD]

        if self.standalone:
            screen_rect = pygame.Rect(0, 0, self.config[SCREEN_WIDTH], self.config[SCREEN_HEIGHT])
            self.init_display()
            Container.__init__(self, self.util, bounding_box=screen_rect)
        else:
            Container.__init__(self, util, bounding_box=util.screen_rect, background=self.bg[1], content=self.bg[2], image_filename=self.bg[3])

        self.pipe = None
        self.spectrum_configs = self.config_parser.spectrum_configs
        self.indexes = cycle(range(len(self.spectrum_configs)))
        self.seconds = 0 

        self.init_spectrums()
        self.init_container()

        if "win" in sys.platform:
            self.windows = True
        else:
            self.windows = False
            thread = Thread(target=self.open_pipe)
            thread.start()

    def init_display(self):
        """ Initialize Pygame display """

        screen_w = self.config[SCREEN_WIDTH]
        screen_h = self.config[SCREEN_HEIGHT]
        depth = self.config[DEPTH]
        
        os.environ["SDL_FBDEV"] = self.config[FRAMEBUFFER_DEVICE]

        if self.config[MOUSE_ENABLED]:
            os.environ["SDL_MOUSEDEV"] = self.config[MOUSE_DEVICE]
            os.environ["SDL_MOUSEDRV"] = self.config[MOUSE_DRIVER]
        else:
            os.environ["SDL_NOMOUSE"] = "1"
        
        if "win" not in sys.platform:
            if not self.config[VIDEO_DRIVER] == "dummy":
                os.environ["SDL_VIDEODRIVER"] = self.config[VIDEO_DRIVER]
                os.environ["DISPLAY"] = self.config[VIDEO_DISPLAY]
            pygame.display.init()
            pygame.mouse.set_visible(False)
        else:            
            pygame.init()
            pygame.display.set_caption("PeppySpectrum")

        pygame.font.init()

        if self.config[DOUBLE_BUFFER]:
            if self.config[NO_FRAME]:
                self.util.pygame_screen = pygame.display.set_mode((screen_w, screen_h), pygame.DOUBLEBUF | pygame.NOFRAME, depth)
            else:
                self.util.pygame_screen = pygame.display.set_mode((screen_w, screen_h), pygame.DOUBLEBUF, depth)
        else:
            if self.config[NO_FRAME]:
                self.util.pygame_screen = pygame.display.set_mode((screen_w, screen_h), pygame.NOFRAME)
            else:
                self.util.pygame_screen = pygame.display.set_mode((screen_w, screen_h))

    def init_container(self):
        """ Initialize container """
        
        c = Component(self.util)
        self.add_component(c)
        for _ in range(self.config[SIZE]):
            c = Component(self.util)
            self.add_component(c)
            c = Component(self.util)
            self.add_component(c)        
    
    def init_spectrums(self):
        """ Initialize lists of images """
        
        self.bgr = self.get_backgrounds()
        self.bar = self.get_bars()
        self.reflection = self.get_reflections()

    def get_color_surface(self, bounding_box, color):
        """ Create surface filled by solid color
        
        :param bounding_box: the bounding box which defines the size of the surface
        :param color: the fill color

        :return: the surface filled by the solid color
        """
        if not bounding_box or not color:
            return None

        b = pygame.Surface(bounding_box, pygame.SRCALPHA, 32)
        b.fill(color)

        return b.convert_alpha()

    def get_gradient_surface(self, bounding_box, gradient):
        """ Create surface filled by the color gradient
        
        :param bounding_box: the bounding box which defines the size of the surface
        :param gradient: the list of gradient colors in format (Red, Green, Blue, Alpha), alpha is optional

        :return: the surface filled by the color gradient
        """
        if not bounding_box or not gradient:
            return None

        size = len(gradient)
        gradient.reverse()
        base_rect = pygame.Surface((2, size), pygame.SRCALPHA, 32)

        for index in range(size):
            pygame.draw.line(base_rect, gradient[index],  (0, index), (1, index))

        gradient_bgr = pygame.transform.smoothscale(base_rect, bounding_box)

        return gradient_bgr.convert_alpha()

    def get_image_surface(self, bounding_box, path):
        """ Create surface with image
        
        :param bounding_box: the bounding box which defines the size of the surface
        :param path: the image path

        :return: the surface with image from file
        """
        if not bounding_box or not path:
            return None

        img = self.image_util.load_pygame_image(path)

        return self.image_util.scale_image(img, bounding_box)

    def get_extended_image_surface(self, bounding_box, path):
        """ Create surface with image by extending input image
        
        :param bounding_box: the bounding box which defines the size of the surface
        :param path: the image path

        :return: the surface with extended image from file
        """
        if not bounding_box or not path:
            return None

        img = self.image_util.load_pygame_image(path)
        image = pygame.transform.smoothscale(img[1], bounding_box)

        return image.convert_alpha()

    def get_backgrounds(self):
        """ Prepare spectrum backgrounds
        
        :return: the list of spectrum backgrounds
        """
        backgrounds = []
        w = self.bounding_box.w
        h = self.bounding_box.h

        for config in self.spectrum_configs:
            if config[BGR_TYPE] == "color":
                backgrounds.append(self.get_color_surface((w, h), config[BGR_COLOR]))
            elif config[BGR_TYPE] == "gradient":
                backgrounds.append(self.get_gradient_surface((w, h), config[BGR_GRADIENT]))
            elif config[BGR_TYPE] == "player.bgr":
                b = pygame.Surface((w, h), pygame.SRCALPHA, 32)
                b = b.convert_alpha()
                backgrounds.append(b)
            elif config[BGR_TYPE] == "image":
                path = self.config_parser.get_path(config[BGR_FILENAME], self.config[SCREEN_SIZE])
                b = self.image_util.load_pygame_image(path)
                backgrounds.append(b[1])
            elif config[BGR_TYPE] == "image.extended":
                path = self.config_parser.get_path(config[BGR_FILENAME], self.config[SCREEN_SIZE])
                backgrounds.append(self.get_extended_image_surface((w, h), path))

        return backgrounds

    def get_bars(self):
        """ Prepare frequency bars
        
        :return: the list of frequency bars
        """
        bars = []

        for config in self.spectrum_configs:
            w = config[BAR_WIDTH]
            h = config[BAR_HEIGHT]

            if config[BAR_TYPE] == "color":
                bars.append(self.get_color_surface((w, h), config[BAR_COLOR]))
            elif config[BAR_TYPE] == "gradient":
                bars.append(self.get_gradient_surface(((w, h)), config[BAR_GRADIENT]))
            elif config[BAR_TYPE] == "image":
                path = self.config_parser.get_path(config[BAR_FILENAME], self.config[SCREEN_SIZE])
                bars.append(self.get_image_surface((w, h), path))
            elif config[BAR_TYPE] == "image.extended":
                path = self.config_parser.get_path(config[BAR_FILENAME], self.config[SCREEN_SIZE])
                bars.append(self.get_extended_image_surface((w, h), path))
        
        return bars

    def get_reflections(self):
        """ Prepare refleactions
        
        :return: the list of reflections
        """
        reflections = []

        for config in self.spectrum_configs:
            if not config[REFLECTION_TYPE]:
                reflections.append(None)
                continue

            w = config[BAR_WIDTH]
            h = config[BAR_HEIGHT]

            if config[REFLECTION_TYPE] == "color":
                reflections.append(self.get_color_surface((w, h), config[REFLECTION_COLOR]))
            elif config[REFLECTION_TYPE] == "gradient":
                reflections.append(self.get_gradient_surface(((w, h)), config[REFLECTION_GRADIENT]))
            elif config[REFLECTION_TYPE] == "image":
                path = self.config_parser.get_path(config[REFLECTION_FILENAME], self.config[SCREEN_SIZE])
                reflections.append(self.get_image_surface((w, h), path))
            elif config[REFLECTION_TYPE] == "image.extended":
                path = self.config_parser.get_path(config[REFLECTION_FILENAME], self.config[SCREEN_SIZE])
                reflections.append(self.get_extended_image_surface((w, h), path))

        return reflections

    def open_pipe(self):
        """ Open named pipe  """
        
        try:            
            self.pipe = os.open(self.config[PIPE_NAME], os.O_RDONLY | os.O_NONBLOCK)
        except Exception as e:
            logging.debug("Cannot open named pipe: " + self.config[PIPE_NAME])
            logging.debug(e)

    def flush_pipe_buffer(self):
        """ Flush data from the pipe """

        if not self.pipe:
            return

        try:
            os.read(self.pipe, self.config[PIPE_BUFFER_SIZE])
        except Exception as e:
            logging.debug(e)

    def start(self):
        """ Start spectrum thread. """ 
        
        self.index = 0
        self.set_background()        
        self.set_bars()
        self.set_reflections()
        
        self.run_flag = True
        self.start_data_source()
        thread = Thread(target=self.update_ui)
        thread.start()
        pygame.event.clear()

        if hasattr(self, "callback_start"):
            self.callback_start(self)
    
    def set_background(self):
        """ Set background image """
        
        c = self.components[0]
        c.content = ("", self.bgr[self.index])

        w = self.config[SCREEN_WIDTH]
        h = self.config[SCREEN_HEIGHT]
        size = c.content[1].get_size()
        
        spectrum_x = self.spectrum_configs[self.index][SPECTRUM_X]
        spectrum_y = self.spectrum_configs[self.index][SPECTRUM_Y]
        c.content_x = int(spectrum_x + ((w - size[0])/2))
        c.content_y = int(spectrum_y + ((h - size[1])/2))
    
    def set_bars(self):
        """ Set spectrum bars  """
        
        width = self.spectrum_configs[self.index][BAR_WIDTH]
        height = self.spectrum_configs[self.index][BAR_HEIGHT]
        bar_gap = self.spectrum_configs[self.index][BAR_GAP]

        for r in range(self.config[SIZE]):
            c = self.components[r + 1]
            origin_x = self.spectrum_configs[self.index][ORIGIN_X]
            spectrum_x = self.spectrum_configs[self.index][SPECTRUM_X]
            c.content_x = origin_x + spectrum_x + (r * (width + bar_gap))
            origin_y = self.spectrum_configs[self.index][ORIGIN_Y]
            spectrum_y = self.spectrum_configs[self.index][SPECTRUM_Y]
            c.content_y = origin_y + spectrum_y - height
            c.content = ("", self.bar[self.index])
            c.bounding_box = pygame.Rect(0, 0, width, height)
            
    def set_reflections(self):
        """ Set reflection bars """
        
        if self.reflection == None:
            return

        width = self.spectrum_configs[self.index][BAR_WIDTH]
        bar_gap = self.spectrum_configs[self.index][BAR_GAP]

        for r in range(self.config[SIZE]):
            c = self.components[r + 1 + self.config[SIZE]]
            origin_x = self.spectrum_configs[self.index][ORIGIN_X]
            spectrum_x = self.spectrum_configs[self.index][SPECTRUM_X]
            c.content_x = origin_x + spectrum_x + (r * (width + bar_gap))
            origin_y = self.spectrum_configs[self.index][ORIGIN_Y]
            spectrum_y = self.spectrum_configs[self.index][SPECTRUM_Y]
            c.content_y = origin_y + spectrum_y
            c.content = ("", self.reflection[self.index])
            c.bounding_box = pygame.Rect(0, 0, width, 0)
    
    def refresh(self):
        """ Update spectrum """
        
        self.index = next(self.indexes)
        self.set_background()        
        self.set_bars()
        self.set_reflections()
            
    def stop(self):
        """ Stop spectrum thread. """ 
        
        self.run_flag = False
        self.run_datasource = False
        self.seconds = 0

        if hasattr(self, "callback_stop"):
            self.callback_stop(self)

        if hasattr(self, "malloc_trim"):
            self.malloc_trim()
    
    def start_data_source(self):
        """ Start data source thread. """

        self.flush_pipe_buffer()
        self.run_datasource = True
        thread = Thread(target=self.get_data)
        thread.start()
        
    def get_data(self):
        """ Data Source Thread method. """ 
               
        while self.run_datasource:
            self.set_values()
            time.sleep(self.config[UPDATE_UI_INTERVAL])
    
    def get_latest_pipe_data(self):
        """ Read from the named pipe until it's empty """

        data = [0] * self.config[PIPE_SIZE]
        while True:
            try:
                tmp_data = os.read(self.pipe, self.config[PIPE_SIZE])
                if len(tmp_data) == self.config[PIPE_SIZE]:
                    data = tmp_data
                time.sleep(self.config[PIPE_POLLING_INTERVAL])
            except:
                break

        return data

    def set_values(self):
        """ Get signal from the named pipe and update spectrum bars. """ 

        data = []

        if self.windows:
            data = []
            mask = 0b11111111

            test_data = None
            if self.config[USE_TEST_DATA]:
                test_data = TEST_DATA[self.config[USE_TEST_DATA]]

            for n in range(self.config[SIZE]):
                if self.config[USE_TEST_DATA]:
                    v = test_data[n]
                else:
                    v = int((randrange(0, int(self.config[MAX_VALUE]))))
                data.append(v & mask)
                data.append((v >> 8) & mask)
                data.append((v >> 16) & mask)
                data.append((v >> 24) & mask)
        else:
            try:
                if self.pipe == None:
                    return
    			
                data = self.get_latest_pipe_data()
            except Exception as e:
                logging.debug(e)
                return

        length = len(data)
        if length == 0:
            return
            
        words = int(length / 4)
        height = self.spectrum_configs[self.index][BAR_HEIGHT]
        step = int(height / self.spectrum_configs[self.index][STEPS])
        origin_y = self.spectrum_configs[self.index][ORIGIN_Y]
        spectrum_y = self.spectrum_configs[self.index][SPECTRUM_Y]
        unit = height / self.config[MAX_VALUE]
        reflection_gap = 0
        try:
            reflection_gap = self.spectrum_configs[self.index][REFLECTION_GAP]
        except:
            pass

        for m in range(words):
            v = data[4 * m] + (data[4 * m + 1] << 8) + (data[4 * m + 2] << 16) + (data[4 * m + 3] << 24)
            v = v * unit

            if v <= 0:
                steps = 0
            elif v % step == 0:
                steps = int(v / step)
            else:
                steps = int(v / step) + 1
            
            h = steps * step
            i = m + 1
            
            comp = self.components[i]
            comp.bounding_box.h = h
            comp.bounding_box.y = height - h
            comp.content_y = int(spectrum_y + origin_y - height + comp.bounding_box.y)

            comp = self.components[i + self.config[SIZE]]
            if comp.content == None:
                continue
            comp.bounding_box.h = h
            comp.bounding_box.y = 0
            comp.content_y = int(spectrum_y + origin_y + reflection_gap)

    def update_ui(self):
        """ Update UI Thread method. """ 
    
        while self.run_flag:
            self.clean_draw_update()            
            time.sleep(self.config[UPDATE_UI_INTERVAL])

    def start_display_output(self):
        """ Start main loop in standalone mode """
        
        pygame.event.clear()
        while self.run_flag:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    keys = pygame.key.get_pressed() 
                    if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and event.key == pygame.K_c:
                        self.exit()
                elif event.type == pygame.MOUSEBUTTONUP and self.config[EXIT_ON_TOUCH]:
                    self.exit()
            if self.seconds >= self.config[UPDATE_PERIOD]:
                self.seconds = 0
                self.refresh()
            self.seconds += 0.1
            time.sleep(0.1)

    def exit(self):
        """ Exit program """
        
        pygame.quit()

        if hasattr(self, "malloc_trim"):
            self.malloc_trim()

        os._exit(0)

if __name__ == "__main__":
    """ This is called by stand-alone PeppySpectrum """

    pm = Spectrum(None, True)
    pm.start()
    pm.refresh()
    pm.start_display_output()
