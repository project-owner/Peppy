# Copyright 2016-2018 Peppy Player peppy.player@gmail.com
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

KEY_RADIO = "radio"
KEY_AUDIO_FILES = "audio-files"
KEY_STREAM = "stream"
KEY_AUDIOBOOKS = "audiobooks"

KEY_PLAY_FILE = "play.file"
KEY_PLAY_SITE = "play.site"
KEY_GENRES = "genres"
KEY_STATIONS = "stations"
KEY_BOOK_SCREEN = "book.screen"
KEY_LANGUAGE = "language"
KEY_SCREENSAVER = "screensaver"
KEY_MODE = "mode"
KEY_ABOUT = "about"
KEY_SEEK = "seek"
KEY_SHUTDOWN = "shutdown"
KEY_PLAY_PAUSE = "play.pause"
KEY_SET_VOLUME = "set.volume"
KEY_SET_CONFIG_VOLUME = "set.config.volume"
KEY_SET_SAVER_VOLUME = "set.saver.volume"
KEY_WAITING_FOR_COMMAND = "waiting.for.command"
KEY_VA_COMMAND = "voice.command"
LABELS = "labels"
CURRENT = "current"
ICON_SIZE_FOLDER = "icon.size.folder"
FONT_KEY = "font.name"
PLAYER_SETTINGS = "player.settings"
FILE_PLAYBACK = "file.playback"
KEY_SCREENSAVER = "screensaver"
KEY_SCREENSAVER_DELAY = "delay"
KEY_SCREENSAVER_DELAY_1 = "delay.1"
KEY_SCREENSAVER_DELAY_3 = "delay.3"
KEY_SCREENSAVER_DELAY_OFF = "delay.off"
SCREEN_INFO = "screen.info"
PYGAME_SCREEN = "pygame.screen"
WIDTH = "width"
HEIGHT = "height"
DEPTH = "depth"
FRAME_RATE = "frame.rate"
HDMI = "hdmi"
NO_FRAME = "no.frame"
SCREEN_RECT = "screen.rect"
COLOR_WEB_BGR = "color.web.bgr" 
COLORS = "colors"
COLOR_DARK = "color.dark"
COLOR_DARK_LIGHT = "color.dark.light"
COLOR_MEDIUM = "color.medium"
COLOR_BRIGHT = "color.bright"
COLOR_CONTRAST = "color.contrast"
COLOR_LOGO = "color.logo"
LINUX_PLATFORM = "linux"
WINDOWS_PLATFORM = "windows"
H_ALIGN_LEFT = 0
H_ALIGN_CENTER = 1
H_ALIGN_RIGHT = 2
V_ALIGN_TOP = 3
V_ALIGN_CENTER = 4
V_ALIGN_BOTTOM = 5
STATION = "station"
STREAM = "stream.server"
PREVIOUS_STATIONS = "previous.stations"
RADIO_PLAYLIST = "radio.playlist"
VOLUME = "volume"
MUTE = "mute"
PAUSE = "pause"
ORDER_GENRE_MENU = "order.genre.menu"
ORDER_HOME_MENU = "order.home.menu"
ORDER_HOME_NAVIGATOR_MENU = "order.home.navigator.menu"
ORDER_LANGUAGE_MENU = "order.language.menu"
ORDER_SCREENSAVER_MENU = "order.screensaver.menu"
ORDER_SCREENSAVER_DELAY_MENU = "order.screensaver.delay.menu"
MODE = "mode"
GENRE = "genre"
NAME = "name"
WEB_SERVER = "web.server"
HTTP_PORT = "http.port"
STREAM_SERVER_PORT = "stream.server.port"

USER_EVENT_TYPE = pygame.USEREVENT + 1
VOICE_EVENT_TYPE = pygame.USEREVENT + 2
SUB_TYPE_KEYBOARD = 0
KEY_SUB_TYPE = "sub_type"
KEY_ACTION = "action"
KEY_KEYBOARD_KEY = "keyboard_key"
KEY_LIRC_CODE = "lirc_code"
KEY_VOLUME_UP = "volume-up"
KEY_VOLUME_DOWN = "volume-down"
KEY_MUTE = "mute"
KEY_LEFT = "left"
KEY_RIGHT = "right"
KEY_UP = "up"
KEY_DOWN = "down"
KEY_PAGE_UP = "page-up"
KEY_PAGE_DOWN = "page-down"
KEY_SELECT = "select"
KEY_END = "end"
KEY_HOME = "home"
KEY_MENU = "menu"
KEY_BACK = "back"
KEY_PLAY = "play"
KEY_SETUP = "setup"
KEY_ROOT = "root"
KEY_PARENT = "parent"
KEY_USER_HOME = "user-home"
KEY_PLAYER = "player"
KEY_0 = "0"
KEY_1 = "1"
KEY_2 = "2"
KEY_3 = "3"
KEY_4 = "4"
KEY_5 = "5"
KEY_6 = "6"
KEY_7 = "7"
KEY_8 = "8"
KEY_9 = "9"
KEY_VA_START = "va start"
KEY_VA_STOP = "va stop"
KEY_VOICE_COMMAND = "voice_command"
KEY_AUDIO = "audio"

GO_LEFT_PAGE = "go left page"
GO_RIGHT_PAGE = "go right page"
GO_USER_HOME = "go user home"
GO_ROOT = "go root"
GO_TO_PARENT = "go to parent"
GO_PLAYER = "go player"
GO_BACK = "go back"

KEY_CHOOSE_TRACK = "choose.track"
KEY_CHOOSE_AUTHOR = "choose.author"
KEY_CHOOSE_GENRE = "choose.genre"
KEY_AUTHORS = "authors"
KEY_NEW_BOOKS = "new.books"
KEY_LOADING = "loading"

LOYALBOOKS = "Loyal Books"
AUDIOKNIGI = "AudioKnigi.Club"

TRACK_MENU = "track.menu"
BOOK_MENU = "book.menu"
BOOK_NAVIGATOR_BACK = "book.back"
BOOK_NAVIGATOR = "book.navigator"
HOME_NAVIGATOR = "home.navigator"
ARROW_BUTTON = "arror.button"
INIT = "init"
RESUME = "resume"

kbd_keys = {KEY_MENU : pygame.K_m,
            KEY_END : pygame.K_END,
            KEY_HOME : pygame.K_HOME,
            KEY_PLAY_PAUSE : pygame.K_SPACE,
            KEY_SELECT : pygame.K_RETURN,
            KEY_LEFT : pygame.K_LEFT,
            KEY_RIGHT : pygame.K_RIGHT,
            KEY_UP : pygame.K_UP,
            KEY_DOWN : pygame.K_DOWN,
            KEY_PAGE_UP : pygame.K_PAGEUP,
            KEY_PAGE_DOWN : pygame.K_PAGEDOWN,
            KEY_VOLUME_UP : pygame.K_KP_PLUS,
            KEY_VOLUME_DOWN : pygame.K_KP_MINUS,
            KEY_MUTE : pygame.K_x,
            KEY_BACK: pygame.K_ESCAPE,
            KEY_SETUP: pygame.K_s,
            KEY_ROOT: pygame.K_r,
            KEY_PARENT: pygame.K_p,
            KEY_AUDIO: pygame.K_a,
            KEY_0: pygame.K_0,
            KEY_1: pygame.K_1,
            KEY_2: pygame.K_2,
            KEY_3: pygame.K_3,
            KEY_4: pygame.K_4,
            KEY_5: pygame.K_5,
            KEY_6: pygame.K_6,
            KEY_7: pygame.K_7,
            KEY_8: pygame.K_8,
            KEY_9: pygame.K_9}

kbd_num_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, \
                pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
