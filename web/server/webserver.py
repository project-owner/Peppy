# Copyright 2016-2022 Peppy Player peppy.player@gmail.com
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

import logging
import tornado.httpserver
import tornado.ioloop
import tornado.web
import os
import json
import asyncio

from threading import Thread, RLock
from util.config import WEB_SERVER, HTTP_PORT, HTTPS, SCREENSAVER, NAME
from util.keys import KEY_ABOUT
from web.server.jsonfactory import JsonFactory
from screensaver.screensaverdispatcher import WEB_SAVERS
from tornado.web import StaticFileHandler, Application
from tornado.httpserver import HTTPServer
from web.server.handlers.websockethandler import WebSocketHandler
from web.server.handlers.parametershandler import ParametersHandler
from web.server.handlers.playershandler import PlayersHandler
from web.server.handlers.screensavershandler import ScreensaversHandler
from web.server.handlers.podcastshandler import PodcastsHandler
from web.server.handlers.playlistshandler import PlaylistsHandler
from web.server.handlers.labelshandler import LabelsHandler
from web.server.handlers.commandhandler import CommandHandler
from web.server.handlers.streamshandler import StreamsHandler
from web.server.handlers.uploadhandler import UploadHandler
from web.server.handlers.bgrhandler import BgrHandler
from web.server.handlers.fontshandler import FontsHandler
from web.server.handlers.defaultshandler import DefaultsHandler
from web.server.handlers.timezonehandler import TimezoneHandler
from web.server.handlers.diskmanager import DiskManager
from web.server.handlers.nasmanager import NasManager
from web.server.handlers.sharefolder import ShareFolder
from web.server.handlers.loghandler import LogHandler
from web.server.handlers.playlisthandler import PlaylistHandler as PlaylistDownLoader
from web.server.handlers.yastreamshandler import YaStreamsHandler
# REST API
from web.server.restapihandlers.about import AboutHandler
from web.server.restapihandlers.newrelease import NewReleaseHandler
from web.server.restapihandlers.screensaver import ScreensaverHandler
from web.server.restapihandlers.language import LanguageHandler
from web.server.restapihandlers.equalizer import EqualizerHandler
from web.server.restapihandlers.volume import VolumeHandler
from web.server.restapihandlers.mute import MuteHandler
from web.server.restapihandlers.shutdown import ShutdownHandler
from web.server.restapihandlers.playpause import PlayPauseHandler
from web.server.restapihandlers.next import NextHandler
from web.server.restapihandlers.previous import PreviousHandler
from web.server.restapihandlers.modes import ModesHandler
from web.server.restapihandlers.mode import ModeHandler
from web.server.restapihandlers.title import TitleHandler
from web.server.restapihandlers.orders import OrdersHandler
from web.server.restapihandlers.order import OrderHandler
from web.server.restapihandlers.info import InfoHandler
from web.server.restapihandlers.timer import TimerHandler
from web.server.restapihandlers.sleep import SleepHandler
from web.server.restapihandlers.wakeup import WakeUpHandler
from web.server.restapihandlers.network import NetworkHandler
from web.server.restapihandlers.wifi import WiFiHandler
from web.server.restapihandlers.image import ImageHandler
from web.server.restapihandlers.time import TimeHandler
from web.server.restapihandlers.fileplayer import FilePlayerHandler
from web.server.restapihandlers.files import FilesHandler
from web.server.restapihandlers.playlist import PlaylistHandler
from web.server.restapihandlers.genres import GenresHandler
from web.server.restapihandlers.genre import GenreHandler
from web.server.restapihandlers.radioplayer import RadioPlayerHandler
from web.server.restapihandlers.podcast import PodcastHandler

class WebServer(object):
    """ Starts Tornado web server in a separate thread """
    
    def __init__(self, util, peppy):
        """ Initializer. Start web server in separate thread
        
        :param util: utility object contains configuration settings
        :param peppy: the reference to the root object
        """
        self.util = util
        self.lock = RLock()
        self.config = util.config
        self.config_class = util.config_class
        self.peppy = peppy
        self.web_clients = []
        self.player_listeners = []
        self.json_factory = JsonFactory(util, peppy)
        self.instance = None
        thread = Thread(target=self.start_web_server)
        thread.daemon = True        
        thread.start()
     
    def start_web_server(self):
        """ Prepare request handlers and start server """
        
        root = os.getcwd()
        app = Application([
            (r"/()", StaticFileHandler, {"path": root, "default_filename": "index.html"}),
            (r"/web/client/(.*)", StaticFileHandler, {"path": root + "/web/client"}),
            (r"/font/(.*)", StaticFileHandler, {"path": root + "/font"}),
            (r"/icon/(.*)", StaticFileHandler, {"path": root + "/icons"}),
            (r"/flag/(.*)", StaticFileHandler, {"path": root + "/languages"}),
            (r"/backgrounds/(.*)", StaticFileHandler, {"path": root + "/backgrounds"}),
            (r"/ws", WebSocketHandler, {"redraw_web_ui": self.redraw_web_ui, "web_clients": self.web_clients}),
            (r"/config/()", StaticFileHandler, {"path": root + "/web/client/config", "default_filename": "index.html"}),
            (r"/config/icon/(.*)", StaticFileHandler, {"path": root + "/languages"}),
            (r"/config/default/(.*)", StaticFileHandler, {"path": root + "/icons"}),
            (r"/static/js/(.*)", StaticFileHandler, {"path": root + "/web/client/config/static/js"}),
            (r"/static/css/(.*)", StaticFileHandler, {"path": root + "/web/client/config/static/css"}),
            (r"/static/media/(.*)", StaticFileHandler, {"path": root + "/web/client/config/static/media"}),
            (r"/parameters", ParametersHandler, {"config_class": self.config_class}),
            (r"/players", PlayersHandler, {"config_class": self.config_class}),
            (r"/savers", ScreensaversHandler, {"config": self.config}),
            (r"/podcasts", PodcastsHandler, {"util": self.util}),
            (r"/streams", StreamsHandler, {"util": self.util}),
            (r"/yastreams", YaStreamsHandler, {"util": self.util}),
            (r"/streamimage/(.*)", StaticFileHandler, {"path": root + "/streams"}),
            (r"/playlists", PlaylistsHandler, {"util": self.util}),
            (r"/labels", LabelsHandler, {"util": self.util}),
            (r"/command/(.*)", CommandHandler, {"peppy": self.peppy}),
            (r"/upload", UploadHandler, {"path": root}),
            (r"/bgr", BgrHandler, {"config_class": self.config_class}),
            (r"/fonts", FontsHandler, {"util": self.util}),
            (r"/defaults", DefaultsHandler, {"config": self.config_class}),
            (r"/timezone", TimezoneHandler, {"util": self.util}),
            (r"/diskmanager/(.*)", DiskManager, {"peppy": self.peppy}),
            (r"/nasmanager/(.*)", NasManager, {"peppy": self.peppy, "config_class": self.config_class}),
            (r"/sharefolder/(.*)", ShareFolder, {"peppy": self.peppy}),
            (r"/log", LogHandler, {"util": self.util}),
            (r"/playlist", PlaylistDownLoader, {"root": root}),
            # Public REST API
            ("/api/about", AboutHandler, {"peppy": self.peppy}),
            ("/api/newrelease", NewReleaseHandler, {"peppy": self.peppy}),
            ("/api/screensaver", ScreensaverHandler, {"peppy": self.peppy}),
            ("/api/screensavers", ScreensaverHandler, {"peppy": self.peppy}),
            ("/api/screensaver/(.*)", ScreensaverHandler, {"peppy": self.peppy}),
            ("/api/language", LanguageHandler, {"peppy": self.peppy}),
            ("/api/languages", LanguageHandler, {"peppy": self.peppy}),
            ("/api/equalizer", EqualizerHandler, {"peppy": self.peppy}),
            ("/api/volume", VolumeHandler, {"peppy": self.peppy}),
            ("/api/mute", MuteHandler, {"peppy": self.peppy}),
            ("/api/shutdown", ShutdownHandler, {"peppy": self.peppy}),
            ("/api/playpause", PlayPauseHandler, {"peppy": self.peppy}),
            ("/api/next", NextHandler),
            ("/api/previous", PreviousHandler),
            ("/api/modes", ModesHandler, {"peppy": self.peppy}),
            ("/api/mode", ModeHandler, {"peppy": self.peppy}),
            ("/api/title", TitleHandler, {"peppy": self.peppy}),
            ("/api/orders", OrdersHandler),
            ("/api/order", OrderHandler, {"peppy": self.peppy}),
            ("/api/info", InfoHandler, {"peppy": self.peppy}),
            ("/api/timer", TimerHandler, {"peppy": self.peppy}),
            ("/api/timer/(.*)", TimerHandler, {"peppy": self.peppy}),
            ("/api/sleep", SleepHandler, {"peppy": self.peppy}),
            ("/api/wakeup", WakeUpHandler, {"peppy": self.peppy}),
            ("/api/network", NetworkHandler, {"peppy": self.peppy}),
            ("/api/wifi", WiFiHandler, {"peppy": self.peppy}),
            ("/api/wifi/(.*)", WiFiHandler, {"peppy": self.peppy}),
            ("/api/image", ImageHandler, {"peppy": self.peppy}),
            ("/api/time", TimeHandler, {"peppy": self.peppy}),
            ("/api/fileplayer", FilePlayerHandler, {"peppy": self.peppy}),
            ("/api/files", FilesHandler, {"peppy": self.peppy}),
            ("/api/playlist", PlaylistHandler, {"peppy": self.peppy}),
            ("/api/genres", GenresHandler, {"peppy": self.peppy}),
            ("/api/genre", GenreHandler, {"peppy": self.peppy}),
            ("/api/radioplayer", RadioPlayerHandler, {"peppy": self.peppy}),
            ("/api/podcasts/(.*)", PodcastHandler, {"peppy": self.peppy})
        ])

        if self.config[WEB_SERVER][HTTPS]:
            http_server = HTTPServer(app, ssl_options={"certfile": "cert", "keyfile": "key"})
        else:
            http_server = HTTPServer(app)

        port = self.config[WEB_SERVER][HTTP_PORT]
        asyncio.set_event_loop(asyncio.new_event_loop())
        http_server.listen(port)
        self.instance = tornado.ioloop.IOLoop.instance()
        logging.debug("Web Server Started")
        self.instance.start()
    
    def update_web_ui(self, state):
        """ Update Web UI component
        
        :param state: object with Web UI component as event_origin attribute
        """
        if len(self.web_clients) == 0:
            return

        if not (state and getattr(state, "event_origin", None) != None): return
        
        j = self.json_factory.container_to_json(state.event_origin)
        self.send_json_to_web_ui(j)
    
    def update_player_listeners(self, state=None):
        """ Update player listeners """

        if len(self.web_clients) == 0:
            return
        
        for c in self.player_listeners:
            self.send_json_to_web_ui(self.json_factory.container_to_json(c))
    
    def redraw_web_ui(self, state=None):
        """ Redraw the whole screen in web UI """

        if len(self.web_clients) == 0:
            return
        
        self.send_json_to_web_ui(self.screen_to_json())
            
    def start_screensaver_to_json(self, state=None):
        """ Send command to web UI to start screensaver """

        if len(self.web_clients) == 0:
            return

        if state == None:
            self.send_json_to_web_ui(self.json_factory.start_screensaver_to_json())
        else:
            name = self.config[SCREENSAVER][NAME]
            screen = state.screen
            command = self.json_factory.screen_to_json(name, screen)
            self.send_json_to_web_ui(command)
    
    def start_time_control_to_json(self, state=None):
        """ Send start time control command to all web clients """

        if len(self.web_clients) == 0:
            return
        
        j = self.json_factory.file_player_start_to_json()
        self.send_json_to_web_ui(j)        
        
    def stop_time_control_to_json(self, state=None):
        """ Send stop time control command to all web clients """

        if len(self.web_clients) == 0:
            return
        
        j = self.json_factory.file_player_stop_to_json()
        self.send_json_to_web_ui(j)
    
    def stop_screensaver_to_json(self, state=None):
        """ Send command to web UI to stop screensaver """

        if len(self.web_clients) == 0:
            return
        
        self.send_json_to_web_ui(self.json_factory.stop_screensaver_to_json())        
    
    def screen_to_json(self):
        """ Convert current screen to JSON objects
        
        :return: list of JSON objects representing current screen
        """

        if len(self.web_clients) == 0:
            return

        current_screen = self.peppy.current_screen
        screen = self.peppy.screens[current_screen]
        if not screen.visible:
            if self.peppy.screensaver_dispatcher.saver_running:
                screen = self.peppy.screensaver_dispatcher.current_screensaver
                current_screen = self.peppy.screensaver_dispatcher.current_screensaver.name
                if current_screen not in WEB_SAVERS:
                    current_screen = KEY_ABOUT
                    screen = self.peppy.screens[KEY_ABOUT]
                    screen.visible = True
        return self.json_factory.screen_to_json(current_screen, screen)

    def station_menu_to_json(self, state):
        """ Convert station menu object into Json object
        
        :param menu: the station menu object
        
        :return: Json object
        """
        if len(self.web_clients) == 0:
            return

        self.send_json_to_web_ui(self.screen_to_json())
    
    def title_to_json(self, title):
        """ Convert screen title to Json object
        
        :param title: screen title object
        """
        if len(self.web_clients) == 0:
            return

        j = self.json_factory.title_to_json(title)
        self.send_json_to_web_ui(j)
    
    def send_json_to_web_ui(self, j):
        """ Send provided Json object to all web clients
        
        "param j": Json object to send
        """
        if len(self.web_clients) == 0:
            return

        try:
            for c in self.web_clients:
                e = json.dumps(j).encode(encoding="utf-8")
                self.instance.add_callback(c.write_message, e)
        except Exception as e:
            logging.debug(e)    

    def add_player_listener(self, listener):
        """ Add player web listener
        
        :param listener: player listener
        """
        if listener not in self.player_listeners:
            self.player_listeners.append(listener)
        
    def shutdown(self):
        """ Shutdown Web Server """
        
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.add_callback(ioloop.stop)
