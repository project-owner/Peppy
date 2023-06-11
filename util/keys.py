# Copyright 2016-2023 Peppy Player peppy.player@gmail.com
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

UTF8 = "utf8"
NAME = "name"
TRANSLATIONS = "translations"
KEY_LANGUAGES = "languages"
RADIO_MODE_ENABLED = "radio mode enabled"
AUDIOBOOKS_MODE_ENABLED = "audiobooks mode enabled"
WEATHER_SCREENSAVER_LANGUAGE_CODES = "weather-screensaver-language-codes"

KEY_PLAY_FILE = "play.file"
KEY_PLAY_CD = "play.cd"
KEY_PLAY_COLLECTION = "play.collection"
KEY_PLAY_SITE = "play.site"
KEY_GENRES = "genres"
KEY_STATIONS = "stations"
KEY_FAVORITES = "favorites"
KEY_BOOK_SCREEN = "book.screen"
KEY_BOOK_TRACK_SCREEN = "book.track.screen"
KEY_MODE = "mode"
KEY_ABOUT = "about"
KEY_BLACK = "black"
KEY_SEEK = "seek"
KEY_SHUTDOWN = "shutdown"
KEY_PLAY_PAUSE = "play.pause"
KEY_SET_VOLUME = "set.volume"
KEY_SET_CONFIG_VOLUME = "set.config.volume"
KEY_SET_SAVER_VOLUME = "set.saver.volume"
KEY_WAITING_FOR_COMMAND = "waiting.for.command"
KEY_VA_COMMAND = "voice.command"
KEY_RADIO_BROWSER = "radio.browser"
KEY_STREAM_BROWSER = "stream.browser"
KEY_YA_STREAM_BROWSER = "ya.stream.browser"
KEY_SWITCH = "switch"
KEY_POWER_ON = "power.on"
KEY_INDEX = "index"
LABELS = "labels"
MAXIMUM_FONT_SIZE = "max.font.size"
LYRICS_NOT_FOUND = "lyrics.not.found"
BIT_ADDRESS = "bit.address"
KEY_NAS = "nas"
KEY_IP_ADDRESS = "ip.address"
KEY_FOLDER = "folder"
KEY_FILESYSTEM = "filesystem"
KEY_MOUNT_POINT = "mount.point"
KEY_USERNAME = "username"
KEY_PASSWORD = "password"
KEY_MOUNT_OPTIONS = "mount.options"
KEY_MOUNTED = "mounted"
KEY_IMAGE_VIEWER = "image viewer"
KEY_ARCHIVE_FILES_BROWSER = "archive.files.browser"
KEY_ARCHIVE_ITEMS_BROWSER = "archive.items.browser"
KEY_ARCHIVE_FILES = "archive.files"
KEY_ARCHIVE_ITEMS = "archive.items"
KEY_ARCHIVE_TITLE = "archive.title"

LINUX_PLATFORM = "linux"
WINDOWS_PLATFORM = "windows"
H_ALIGN = "h_align"
H_OFFSET = "h_offset"
H_ALIGN_LEFT = 0
H_ALIGN_CENTER = 1
H_ALIGN_RIGHT = 2
V_ALIGN = "v_align"
V_OFFSET = "v_offset"
V_ALIGN_TOP = 3
V_ALIGN_CENTER = 4
V_ALIGN_BOTTOM = 5

GENRE = "genre"
USER_EVENT_TYPE = pygame.USEREVENT + 1
REST_EVENT_TYPE = pygame.USEREVENT + 2
SELECT_EVENT_TYPE = pygame.USEREVENT + 3
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
KEY_STOP = "stop"
KEY_SETUP = "setup"
KEY_ROOT = "root"
KEY_PARENT = "parent"
KEY_USER_HOME = "user-home"
KEY_PLAYER = "player"
KEY_PODCAST_PLAYER = "podcast.player"
KEY_PODCASTS_MENU = "podcasts-menu"
KEY_EJECT = "eject"
KEY_REFRESH = "refresh"
KEY_CD_DRIVES = "cd.drives"
KEY_CD_PLAYERS = "cd-players"
KEY_CD_TRACKS = "cd-tracks"
KEY_PODCAST_EPISODES = "podcast.episodes"
KEY_CHECK_INTERNET = "check.internet"
KEY_SET_MODES = "set.modes"
KEY_CALLBACK = "callback"
KEY_CALLBACK_VAR = "callback_var"
KEY_CONNECTING = "connecting"
KEY_DISCONNECTING = "disconnecting"
KEY_START_SAVER = "start-saver"
KEY_AIRPLAY_PLAYER = "airplay.player"
KEY_SPOTIFY_CONNECT_PLAYER = "spotify.connect.player"
KEY_BLUETOOTH_SINK_PLAYER = "bluetooth.sink.player"
KEY_YA_STREAM_PLAYER = "ya.stream.player"
KEY_JUKEBOX_BROWSER = "jukebox.browser"
KEY_ARCHIVE_PLAYER = "archive.player"
KEY_ARCHIVE_ITEMS = "archive.items"
KEY_INFO = "info.screen"
KEY_FILE_INFO = "file.info.screen"
KEY_RADIO_INFO = "radio.info.screen"
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
KEY_SUBTITLE = "subtitle"
KEY_DELETE = "delete"
KEY_VIEW = "view"
KEY_DISCONNECT = "disconnect"
KEY_BLUETOOTH_REMOVE = "bluetooth-remove"
KEY_SORT = "sort"
KEY_NETWORK = "network"
KEY_ABC = "abc"
KEY_SOURCE = "source"
KEY_NAME = "name"
KEY_SEARCH = "search"
KEY_AUDIO_FOLDER = "audio-folder"
KEY_FILE = "file"
KEY_LIST = "list"
KEY_DETAIL = "detail"
KEY_NAVIGATOR = "navigator"

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
ARROW_BUTTON = "arrow.button"
INIT = "init"
RESUME = "resume"
FILE_BUTTON = "file.button"

CLASSICAL = "classical"
JAZZ = "jazz"
POP = "pop"
ROCK = "rock"
CONTEMPORARY = "contemporary"
FLAT = "flat"

IMAGE_VIEWER_SCREEN = "image.viewer"

kbd_keys = {
    KEY_MENU : pygame.K_m,
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
    KEY_SUBTITLE: pygame.K_n,
    KEY_0: pygame.K_0,
    KEY_1: pygame.K_1,
    KEY_2: pygame.K_2,
    KEY_3: pygame.K_3,
    KEY_4: pygame.K_4,
    KEY_5: pygame.K_5,
    KEY_6: pygame.K_6,
    KEY_7: pygame.K_7,
    KEY_8: pygame.K_8,
    KEY_9: pygame.K_9
}

kbd_num_keys = {
    pygame.K_0: 0,
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
    pygame.K_5: 5,
    pygame.K_6: 6,
    pygame.K_7: 7,
    pygame.K_8: 8,
    pygame.K_9: 9
}
