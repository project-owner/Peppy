# Copyright 2018-2024 Peppy Player peppy.player@gmail.com
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
from threading import RLock, Thread
from itertools import cycle
from screensaverspectrum import ScreensaverSpectrum
from spectrumutil import SpectrumUtil
from spectrumconfigparser import *

class Spectrum(Container, ScreensaverSpectrum):
    """ Spectrum Analyzer screensaver plug-in. """

    lock = RLock()

    def __init__(self, util=None):
        """ Initializer
        
        :param util: the utility functions
        """
        self.name = "spectrum"
        self.use_test_data = True
        plugin_folder = type(self).__name__.lower()
        ScreensaverSpectrum.__init__(self, self.name, util, plugin_folder)

        if util:
            self.util = util
            self.image_util = util.image_util
            spectrum_folder = str(util.screen_rect.w) + "x" + str(util.screen_rect.h)
        else:
            self.util = SpectrumUtil()
            self.image_util = self.util
            spectrum_folder = None
        
        self.run_datasource = False
        self.config_parser = SpectrumConfigParser(spectrum_folder)
        self.config = self.config_parser.config
        self.update_period = self.config[UPDATE_PERIOD]
        frame_rate = util.config[SCREEN_INFO][FRAME_RATE]
        self.frames_before_switch = self.update_period * frame_rate
        self.frames = 0

        Container.__init__(self, util, bounding_box=util.screen_rect, background=self.bg[1], content=self.bg[2], image_filename=self.bg[3])

        self.pipe = None
        self.spectrum_configs = self.config_parser.spectrum_configs
        self.indexes = cycle(range(len(self.spectrum_configs)))
        self.index = next(self.indexes)
        self.test_iterator = 0
        self.init_spectrums()
        self.init_container()
        self.values = [0] * self.config[SIZE]
        self.update_boxes = [None] * self.config[SIZE]

        if "win" in sys.platform:
            self.windows = True
            self.config[UPDATE_UI_INTERVAL] = 0.1
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
        
        c = Component(self.util) # bgr
        self.add_component(c)
        for _ in range(self.config[SIZE]):
            c = Component(self.util) # bar
            self.add_component(c)
            c = Component(self.util) # reflection
            self.add_component(c)
            c = Component(self.util) # topping
            self.add_component(c)
        c = Component(self.util) # fgr
        self.add_component(c)
    
    def init_spectrums(self):
        """ Initialize lists of images """
        
        self.bgr = self.get_backgrounds()
        self.bar = self.get_bars()
        self.reflection = self.get_reflections()
        self.toppings = self.get_toppings()
        self.fgr = self.get_foregrounds()

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
                path = self.config_parser.get_path(config[BGR_FILENAME], self.config[SPECTRUM_FOLDER])
                b = self.image_util.load_pygame_image(path)
                backgrounds.append(b[1])
            elif config[BGR_TYPE] == "image.extended":
                path = self.config_parser.get_path(config[BGR_FILENAME], self.config[SPECTRUM_FOLDER])
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
                path = self.config_parser.get_path(config[BAR_FILENAME], self.config[SPECTRUM_FOLDER])
                bars.append(self.get_image_surface((w, h), path))
            elif config[BAR_TYPE] == "image.extended":
                path = self.config_parser.get_path(config[BAR_FILENAME], self.config[SPECTRUM_FOLDER])
                bars.append(self.get_extended_image_surface((w, h), path))
        
        return bars

    def get_reflections(self):
        """ Prepare reflections
        
        :return: the list of reflections
        """
        reflections = []

        for config in self.spectrum_configs:
            if not config.get(REFLECTION_TYPE, None):
                reflections.append(None)
                continue

            w = config[BAR_WIDTH]
            h = config[BAR_HEIGHT]

            if config[REFLECTION_TYPE] == "color":
                reflections.append(self.get_color_surface((w, h), config[REFLECTION_COLOR]))
            elif config[REFLECTION_TYPE] == "gradient":
                reflections.append(self.get_gradient_surface(((w, h)), config[REFLECTION_GRADIENT]))
            elif config[REFLECTION_TYPE] == "image":
                path = self.config_parser.get_path(config[REFLECTION_FILENAME], self.config[SPECTRUM_FOLDER])
                reflections.append(self.get_image_surface((w, h), path))
            elif config[REFLECTION_TYPE] == "image.extended":
                path = self.config_parser.get_path(config[REFLECTION_FILENAME], self.config[SPECTRUM_FOLDER])
                reflections.append(self.get_extended_image_surface((w, h), path))

        return reflections

    def get_toppings(self):
        """ Prepare toppings

        :return: the list of frequency bars
        """
        toppings = []

        for i, config in enumerate(self.spectrum_configs):
            if not config.get(TOPPING_HEIGHT, None):
                toppings.append(None)
            else:
                toppings.append(self.bar[i])

        return toppings

    def get_foregrounds(self):
        """ Prepare spectrum foregrounds

        :return: the list of spectrum foregrounds
        """
        foregrounds = []

        for config in self.spectrum_configs:
            if not config.get(FGR_FILENAME):
                foregrounds.append(None)
            else:
                path = self.config_parser.get_path(config[FGR_FILENAME], self.config[SPECTRUM_FOLDER])
                b = self.image_util.load_pygame_image(path)
                if b:
                    foregrounds.append(b[1])

        return foregrounds


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
        """ Start spectrum """ 
        
        self.set_background()
        self.set_bars()
        self.reflection_gap = self.spectrum_configs[self.index].get(REFLECTION_GAP, 0)
        self.set_reflections()
        self.set_toppings()
        self.set_foreground()
        self.redraw_background()
        self.init_variables()
        self.start_data_source()
        pygame.event.clear()

        if hasattr(self, "callback_start"):
            self.callback_start(self)
    
    def set_background(self):
        """ Set background image """
        
        c = self.components[0]
        c.content = ("", self.bgr[self.index])
        c.content_x = self.spectrum_configs[self.index][SPECTRUM_X]
        c.content_y = self.spectrum_configs[self.index][SPECTRUM_Y]
    
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
            c.visible = False

            self.update_boxes[r] = pygame.Rect(c.content_x, c.content_y, width, height)

    def set_reflections(self):
        """ Set reflection bars """
        
        if self.reflection == [None]:
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
            c.visible = False

            self.update_boxes[r].h += bar_gap + self.update_boxes[r].h 

    def set_toppings(self):
        """ Set spectrum toppings  """

        width = self.spectrum_configs[self.index][BAR_WIDTH]
        height = self.spectrum_configs[self.index][BAR_HEIGHT]
        bar_gap = self.spectrum_configs[self.index][BAR_GAP]

        if self.reflection == [None]:
            n = 1
        else:
            n = 2

        for r in range(self.config[SIZE]):
            c = self.components[r + 1 + self.config[SIZE] * n]
            origin_x = self.spectrum_configs[self.index][ORIGIN_X]
            spectrum_x = self.spectrum_configs[self.index][SPECTRUM_X]
            c.content_x = origin_x + spectrum_x + (r * (width + bar_gap))
            origin_y = self.spectrum_configs[self.index][ORIGIN_Y]
            spectrum_y = self.spectrum_configs[self.index][SPECTRUM_Y]
            c.content_y = origin_y + spectrum_y - height
            c.content = ("", self.toppings[self.index])
            c.bounding_box = pygame.Rect(0, 0, width, height)
            c.visible = False
            c.initialized = False

            self.update_boxes[r].y = c.content_y

    def set_foreground(self):
        """ Set foreground image """

        c = self.components[-1]

        if not self.fgr or self.fgr[self.index] == None:
            c.content = None
            return

        c.content = ("", self.fgr[self.index])
        c.content_x = self.spectrum_configs[self.index][SPECTRUM_X]
        c.content_y = self.spectrum_configs[self.index][SPECTRUM_Y]

        self.update_boxes.append(pygame.Rect(c.content_x, c.content_y, c.bounding_box.w, c.bounding_box.h))
    
    def switch_spectrum(self):
        """ Switch to another spectrum """
        
        self.values = [0] * self.config[SIZE]
        self.test_iterator = 0
        self.index = next(self.indexes)
        self.init_variables()
        self.set_background()
        self.set_bars()
        self.set_reflections()
        self.set_toppings()
        self.set_foreground()
        self.redraw_background()

    def redraw_background(self):
        """ Redraw background """

        bgr = self.components[0]
        bgr.draw()
        pygame.display.update(self.bounding_box)

    def init_variables(self):
        """ Init variables for new spectrum """

        self.height = self.spectrum_configs[self.index][BAR_HEIGHT]
        self.step = int(self.height / self.spectrum_configs[self.index][STEPS])
        self.origin_y = self.spectrum_configs[self.index][ORIGIN_Y]
        self.spectrum_y = self.spectrum_configs[self.index][SPECTRUM_Y]
        self.unit = self.height / self.config[MAX_VALUE]
        self.topping_height = self.spectrum_configs[self.index][TOPPING_HEIGHT]
        self.topping_step = self.spectrum_configs[self.index][TOPPING_STEP]
            
    def stop(self):
        """ Stop spectrum thread. """ 
        
        self.run_datasource = False

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
            except:
                break

        return data

    def get_test_data(self):
        """ Get test data

        :return: list of test data
        """
        data = []
        mask = 0b11111111
        test_data = None

        if self.config[USE_TEST_DATA]:
            test_data = TEST_DATA[self.config[USE_TEST_DATA]]

        for n in range(self.config[SIZE]):
            if test_data == None:
                v = int((randrange(0, int(self.config[MAX_VALUE]))))
            else:
                if len(test_data) == 8:
                    v = test_data[self.test_iterator][n]
                else:
                    v = test_data[n]

            data.append(v & mask)
            data.append((v >> 8) & mask)
            data.append((v >> 16) & mask)
            data.append((v >> 24) & mask)

        if test_data and len(test_data) == 8:
            if self.test_iterator == len(test_data) - 1:
                self.test_iterator = 0
            else:
                self.test_iterator += 1

        return data

    def set_values(self):
        """ Get signal from the named pipe and update spectrum bars. """ 

        data = []

        if self.windows:
            data = self.get_test_data()
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

        for m in range(words):
            v = data[4 * m] + (data[4 * m + 1] << 8) + (data[4 * m + 2] << 16) + (data[4 * m + 3] << 24)
            v = v * self.unit

            if v <= 0:
                steps = 0
            elif v % self.step == 0:
                steps = int(v / self.step)
            else:
                steps = int(v / self.step) + 1
            
            new_height = steps * self.step
            i = m + 1

            self.values[m] = new_height
            
    def set_bar_y(self, index, new_height):
        """ Set bar Y coordinate

        :param index: element index
        :param new_height: element new height
        """
        comp = self.components[index]
        comp.bounding_box.h = new_height
        comp.bounding_box.y = self.height - new_height
        comp.content_y = int(self.spectrum_y + self.origin_y - new_height)
        comp.visible = True

    def set_reflection_y(self, index, new_height):
        """ Set reflection Y coordinate

        :param index: element index
        :param new_height: element new height
        """
        if self.reflection == [None]:
            return

        comp = self.components[index + self.config[SIZE]]
        comp.bounding_box.h = new_height
        comp.bounding_box.y = 0
        comp.content_y = int(self.spectrum_y + self.origin_y + self.reflection_gap)
        comp.visible = True

    def set_topping_y(self, index, new_height):
        """ Set topping Y coordinate

        :param index: element index
        :param new_height: element new height
        """
        if self.topping_height == None or self.topping_step == None:
            return

        n = 1
        if self.reflection != [None]:
            n = 2

        m = index + self.config[SIZE] * n
        comp = self.components[m]
        comp.bounding_box.h = self.topping_height
        y_0 = self.spectrum_y + self.origin_y
        c_y = int(y_0 - new_height)
        if c_y >= y_0:
            c_y = y_0

        if not comp.initialized:
            comp.content_y = c_y
            comp.initialized = True
            return

        if c_y > comp.content_y + self.topping_step + self.topping_height:
            comp.content_y += self.topping_step
            comp.bounding_box.y = self.height - (y_0 - comp.content_y) + 1
            comp.visible = True
        else:
            comp.content_y = c_y - self.topping_height - self.topping_step
            comp.visible = False

    def update(self, area=None):
        """  Update screensaver """

        pass

    def refresh(self, init=False):
        """ Screen refresh per frame 

        :param init: initial call        
        """
        if self.frames == self.frames_before_switch:
            self.frames = 0
            self.switch_spectrum()
        else:
            self.frames += 1

        #set values
        for i, v in enumerate(self.values):
            n = i + 1
            self.set_bar_y(n, v)
            self.set_reflection_y(n, v)
            self.set_topping_y(n, v)

        # clean
        for b in self.update_boxes:
            self.screen.blit(self.components[0].content[1], (b.x, b.y), b)

        # draw
        for i, c in enumerate(self.components):
            if i == 0:
                continue
            c = self.components[i]
            if c: c.draw()

        # update
        pygame.display.update(self.update_boxes)

        return None

    def exit(self):
        """ Exit program """

        pygame.quit()

        if hasattr(self, "malloc_trim"):
            self.malloc_trim()

        os._exit(0)
