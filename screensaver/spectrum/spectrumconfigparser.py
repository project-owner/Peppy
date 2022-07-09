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

import os
import sys
import re
import logging

from configparser import ConfigParser

PACKAGE_SCREENSAVER = "screensaver"
SCREEN_INFO = "screen.info"
WIDTH = "width"
HEIGHT = "height"
DEPTH = "depth"
FRAME_RATE = "frame.rate"
FILE_CONFIG = "config.txt"
FILE_SPECTRUM_CONFIG = "spectrum.txt"
SPECTRUM = "spectrum"
EXIT_ON_TOUCH = "exit.on.touch"
USE_LOGGING = "use.logging"
USE_TEST_DATA = "use.test.data"

SCREEN_SIZE = "screen.size"
SMALL = "small"
MEDIUM = "medium"
LARGE = "large"
WIDE = "wide"
WIDE_WIDTH = 1280
WIDE_HEIGHT = 400
LARGE_WIDTH = 800
LARGE_HEIGHT = 480
MEDIUM_WIDTH = 480
MEDIUM_HEIGHT = 320
SMALL_WIDTH = 320
SMALL_HEIGHT = 240
DEFAULT_DEPTH = 32
DEFAULT_FRAME_RATE = 30

CURRENT = "current"
UPDATE_PERIOD = "update.period"
MAX_VALUE = "max.value"
PIPE_NAME = "pipe.name"
SIZE = "size"
UPDATE_UI_INTERVAL = "update.ui.interval"

SDL_ENV = "sdl.env"
FRAMEBUFFER_DEVICE = "framebuffer.device"
MOUSE_DEVICE = "mouse.device"
MOUSE_DRIVER = "mouse.driver"
MOUSE_ENABLED = "mouse.enabled"
VIDEO_DRIVER = "video.driver"
VIDEO_DISPLAY = "video.display"
DOUBLE_BUFFER = "double.buffer"
NO_FRAME = "no.frame"

ORIGIN_X = "origin.x"
ORIGIN_Y = "origin.y"
SPECTRUM_X = "spectrum.x"
SPECTRUM_Y = "spectrum.y"
BGR_TYPE = "bgr.type"
BGR_COLOR = "bgr.color"
BGR_GRADIENT = "bgr.gradient"
BGR_FILENAME = "bgr.filename"
REFLECTION_TYPE = "reflection.type"
REFLECTION_COLOR = "reflection.color"
REFLECTION_GRADIENT = "reflection.gradient"
REFLECTION_FILENAME = "reflection.filename"
REFLECTION_GAP = "reflection.gap"
BAR_TYPE = "bar.type"
BAR_COLOR = "bar.color"
BAR_GRADIENT = "bar.gradient"
BAR_FILENAME = "bar.filename"
BAR_WIDTH = "bar.width"
BAR_HEIGHT = "bar.height"
BAR_GAP = "bar.gap"
STEPS = "steps"

AVAILABLE_SPECTRUM_NAMES = "available.spectrum.names"
SCREEN_SIZE = "screen.size"
PIPE_BUFFER_SIZE = "pipe.buffer.size"
PIPE_POLLING_INTERVAL = "pipe_polling_inerval"
PIPE_SIZE = "pipe_size"
SCREEN_WIDTH = "screen.width"
SCREEN_HEIGHT = "screen.height"

TEST_DATA = {
    "test1": [98, 76, 84, 56, 64, 45, 78, 54, 37, 48, 53, 34, 66, 48, 24, 39, 58, 46, 34, 43, 25, 46, 62, 53, 36, 48, 87, 52, 36, 44],
    "test2": [42, 65, 34, 84, 56, 27, 48, 76, 53, 33, 24, 45, 64, 37, 28, 43, 65, 82, 74, 58, 26, 48, 62, 45, 18, 35, 53, 28, 36, 56],
    "test3": [63, 47, 78, 54, 32, 18, 42, 62, 68, 55, 34, 57, 74, 74, 61, 42, 24, 46, 68, 44, 48, 79, 69, 46, 27, 54, 33, 65, 86, 58]
}

class SpectrumConfigParser(object):
    """ Configuration file parser """
    
    def __init__(self, standalone):
        self.standalone = standalone
        self.config = self.get_config()
        self.spectrum_configs = self.get_spectrum_configs()

    def get_config(self):
        """ Parse the config.txt file
        
        :return: dictionary with properties from the config.txt
        """
        config_path = self.get_path(FILE_CONFIG)

        if not os.path.exists(config_path):
            print(f"Cannot read file: {config_path}")
            os._exit(0)

        c = ConfigParser()
        c.read(config_path)
        spectrum = c.get(CURRENT, SPECTRUM)
        config = {}
        
        if "," in spectrum:
            names = spectrum.split(",")
            config[AVAILABLE_SPECTRUM_NAMES] = list(map(str.strip, names))
        else:
            if spectrum == None or len(spectrum.strip()) == 0:
                config[AVAILABLE_SPECTRUM_NAMES] = None
            else:    
                config[AVAILABLE_SPECTRUM_NAMES] = [spectrum]

        config[SCREEN_SIZE] = c.get(CURRENT, SCREEN_SIZE)
        config[UPDATE_PERIOD] = c.getint(CURRENT, UPDATE_PERIOD)
        config[PIPE_NAME] = c.get(CURRENT, PIPE_NAME)
        config[PIPE_BUFFER_SIZE] = 1048576 # as defined for Raspberry OS in /proc/sys/fs/pipe-max-size
        config[MAX_VALUE] = c.getint(CURRENT, MAX_VALUE)
        config[SIZE] = c.getint(CURRENT, SIZE)
        config[UPDATE_UI_INTERVAL] = c.getfloat(CURRENT, UPDATE_UI_INTERVAL)
        config[PIPE_POLLING_INTERVAL] = config[UPDATE_UI_INTERVAL] / 10
        config[PIPE_SIZE] = 4 * config[SIZE]
        config[FRAME_RATE] = c.getint(CURRENT, FRAME_RATE)
        config[DEPTH] = c.getint(CURRENT, DEPTH)
        config[EXIT_ON_TOUCH] = c.getboolean(CURRENT, EXIT_ON_TOUCH)
        config[USE_LOGGING] = c.getboolean(CURRENT, USE_LOGGING)
        config[USE_TEST_DATA] = c.get(CURRENT, USE_TEST_DATA)

        config[FRAMEBUFFER_DEVICE] = c.get(SDL_ENV, FRAMEBUFFER_DEVICE)
        config[MOUSE_DEVICE] = c.get(SDL_ENV, MOUSE_DEVICE)
        config[MOUSE_DRIVER] = c.get(SDL_ENV, MOUSE_DRIVER)
        config[MOUSE_ENABLED] = c.getboolean(SDL_ENV, MOUSE_ENABLED)
        config[VIDEO_DRIVER] = c.get(SDL_ENV, VIDEO_DRIVER)
        config[VIDEO_DISPLAY] = c.get(SDL_ENV, VIDEO_DISPLAY)
        config[DOUBLE_BUFFER] = c.getboolean(SDL_ENV, DOUBLE_BUFFER)
        config[NO_FRAME] = c.getboolean(SDL_ENV, NO_FRAME)

        if self.standalone:
            if config[USE_LOGGING]:
                log_handlers = []
                try:
                    log_handlers.append(logging.StreamHandler(sys.stdout))
                    log_handlers.append(logging.FileHandler(filename="peppyspectrum.log", mode='w'))
                    logging.basicConfig(
                        level=logging.NOTSET,
                        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                        handlers=log_handlers
                    )
                except:
                    pass
            else:
                logging.disable(logging.CRITICAL)

        if config[SCREEN_SIZE] == MEDIUM:
            config[SCREEN_WIDTH] = MEDIUM_WIDTH
            config[SCREEN_HEIGHT] = MEDIUM_HEIGHT
        elif config[SCREEN_SIZE] == SMALL:
            config[SCREEN_WIDTH] = SMALL_WIDTH
            config[SCREEN_HEIGHT] = SMALL_HEIGHT
        elif config[SCREEN_SIZE] == LARGE:
            config[SCREEN_WIDTH] = LARGE_WIDTH
            config[SCREEN_HEIGHT] = LARGE_HEIGHT
        elif config[SCREEN_SIZE] == WIDE:
            config[SCREEN_WIDTH] = WIDE_WIDTH
            config[SCREEN_HEIGHT] = WIDE_HEIGHT
        else:
            folder = self.get_path(config[SCREEN_SIZE])
            if not os.path.isdir(folder):
                logging.debug(f"Not supported screen size: {config[SCREEN_SIZE]}")
                os._exit(0)
            try:
                config[SCREEN_WIDTH] = c.getint(CURRENT, SCREEN_WIDTH)
                config[SCREEN_HEIGHT] = c.getint(CURRENT, SCREEN_HEIGHT)
            except:
                pass

        return config

    def get_spectrum_configs(self):
        """ Parse size specific configuration file (spectrum.txt)
        
        :return: dictionary with properties from the spectrum.txt
        """
        spectrum_config_path = self.get_path(FILE_SPECTRUM_CONFIG, self.config[SCREEN_SIZE])
        if not os.path.exists(spectrum_config_path):
            print(f"Cannot read file: {spectrum_config_path}")
            os._exit(0)

        c = ConfigParser()
        c.read(spectrum_config_path)
        config = []
        names = c.sections()
        if self.config[AVAILABLE_SPECTRUM_NAMES] == None:
            sections = names
        else:
            sections =  [v for v in self.config[AVAILABLE_SPECTRUM_NAMES] if v in names]  
        
        for section in sections:
            spectrum = {}
            spectrum[ORIGIN_X] = c.getint(section, ORIGIN_X)
            spectrum[ORIGIN_Y] = c.getint(section, ORIGIN_Y)
            spectrum[SPECTRUM_X] = c.getint(section, SPECTRUM_X)
            spectrum[SPECTRUM_Y] = c.getint(section, SPECTRUM_Y)
            spectrum[BGR_TYPE] = c.get(section, BGR_TYPE)
            spectrum[BGR_COLOR] = self.get_color(c.get(section, BGR_COLOR))
            spectrum[BGR_GRADIENT] = self.get_gradient(c.get(section, BGR_GRADIENT))
            spectrum[BGR_FILENAME] = c.get(section, BGR_FILENAME)
            spectrum[REFLECTION_TYPE] = c.get(section, REFLECTION_TYPE)
            spectrum[REFLECTION_COLOR] = self.get_color(c.get(section, REFLECTION_COLOR))
            spectrum[REFLECTION_GRADIENT] = self.get_gradient(c.get(section, REFLECTION_GRADIENT))
            spectrum[REFLECTION_FILENAME] = c.get(section, REFLECTION_FILENAME)
            spectrum[REFLECTION_GAP] = c.getint(section, REFLECTION_GAP)
            spectrum[BAR_TYPE] = c.get(section, BAR_TYPE)
            spectrum[BAR_COLOR] = self.get_color(c.get(section, BAR_COLOR))
            spectrum[BAR_GRADIENT] = self.get_gradient(c.get(section, BAR_GRADIENT))
            spectrum[BAR_FILENAME] = c.get(section, BAR_FILENAME)
            spectrum[BAR_WIDTH] = c.getint(section, BAR_WIDTH)
            spectrum[BAR_HEIGHT] = c.getint(section, BAR_HEIGHT)
            spectrum[BAR_GAP] = c.getint(section, BAR_GAP)
            spectrum[STEPS] = c.getint(section, STEPS)

            config.append(spectrum)
        
        return config

    def get_color(self, str):
        """ Parse single color section of the configuration file
        
        :param str: single color section e.g. 255, 255, 255

        :return: color tuple
        """
        if len(str.strip()) == 0:
            return None

        a = str.split(",")
        return tuple(int(e) for e in a)

    def get_gradient(self, str):
        """ Parse gradient section of the configuration file
        
        :param str: gradient section e.g. (255,255,255),(0,0,0)

        :return: list of gradient colors
        """
        if len(str.strip()) == 0:
            return None

        gradient = []
        colors_str = re.findall(r'\(.*?\)', str.strip())
        for color in colors_str:
            c = self.get_color(color.strip()[1 : -1])
            gradient.append(c)

        return gradient

    def get_path(self, filename, size=""):
        """ Prepare path
        
        :param filename: the filename
        :param size: the screen size/folder name

        :return: the path composed from screensize and stanalone glag
        """
        if self.standalone:
            return os.path.join(os.getcwd(), size, filename)
        else:
            return os.path.join(os.getcwd(), PACKAGE_SCREENSAVER, SPECTRUM, size, filename)
