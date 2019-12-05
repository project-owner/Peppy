# Copyright 2016-2019 Peppy Player peppy.player@gmail.com
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
import socket
import tornado.httpserver
import tornado.ioloop
import tornado.web
import socket
import os
import json

from threading import Thread, RLock
from util.config import WEB_SERVER, HTTP_PORT, HTTPS
from util.keys import KEY_ABOUT
from web.server.jsonfactory import JsonFactory
from ui.button.button import Button
from tornado.web import StaticFileHandler, Application, RequestHandler
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
            (r"/streamimage/(.*)", StaticFileHandler, {"path": root + "/streams"}),
            (r"/playlists", PlaylistsHandler, {"util": self.util}),
            (r"/labels", LabelsHandler, {"util": self.util}),
            (r"/command/(.*)", CommandHandler, {"peppy": self.peppy}),
            (r"/upload", UploadHandler, {"path": root})
        ])

        if self.config[WEB_SERVER][HTTPS]:
            http_server = tornado.httpserver.HTTPServer(app, ssl_options={"certfile": "cert", "keyfile": "key"})
        else:
            http_server = tornado.httpserver.HTTPServer(app)

        port = self.config[WEB_SERVER][HTTP_PORT]
        http_server.listen(port)
        logging.debug("Web Server Started")
        tornado.ioloop.IOLoop.current().start()
    
    def update_web_ui(self, state):
        """ Update Web UI component
        
        :param state: object with Web UI component as event_origin attribute
        """
        if not (state and getattr(state, "event_origin", None) != None): return
        
        j = self.json_factory.container_to_json(state.event_origin)
        self.send_json_to_web_ui(j)
    
    def update_player_listeners(self, state=None):
        """ Update player listeners """
        
        for c in self.player_listeners:
            self.send_json_to_web_ui(self.json_factory.container_to_json(c))
    
    def redraw_web_ui(self, state=None):
        """ Redraw the whole screen in web UI """
        
        self.send_json_to_web_ui(self.screen_to_json())
            
    def start_screensaver_to_json(self, state=None):
        """ Send command to web UI to start screensaver """
        
        self.send_json_to_web_ui(self.json_factory.start_screensaver_to_json())
    
    def start_time_control_to_json(self, state=None):
        """ Send start time control command to all web clients """
        
        j = self.json_factory.file_player_start_to_json()
        self.send_json_to_web_ui(j)        
        
    def stop_time_control_to_json(self, state=None):
        """ Send stop time control command to all web clients """
        
        j = self.json_factory.file_player_stop_to_json()
        self.send_json_to_web_ui(j)
    
    def stop_screensaver_to_json(self, state=None):
        """ Send command to web UI to stop screensaver """
        
        self.send_json_to_web_ui(self.json_factory.stop_screensaver_to_json())        
    
    def screen_to_json(self):
        """ Convert current screen to JSON objects
        
        :return: list of JSON objects representing current screen
        """
        current_screen = self.peppy.current_screen
        screen = self.peppy.screens[current_screen]
        if not screen.visible:
            current_screen = KEY_ABOUT
            screen = self.peppy.screens[KEY_ABOUT]
            screen.visible = True
        return self.json_factory.screen_to_json(current_screen, screen)    
    
    def station_menu_to_json(self, state):
        """ Convert station menu object into Json object
        
        :param menu: the station menu object
        
        :return: Json object
        """
        self.send_json_to_web_ui(self.screen_to_json())
    
    def title_to_json(self, title):
        """ Convert screen title to Json object
        
        :param title: screen title object
        """
        j = self.json_factory.title_to_json(title)
        self.send_json_to_web_ui(j)
    
    def send_json_to_web_ui(self, j):
        """ Send provided Json object to all web clients
        
        "param j": Json object to send
        """
        for c in self.web_clients:
            e = json.dumps(j).encode(encoding="utf-8")
            ioloop = tornado.ioloop.IOLoop.instance()
            ioloop.add_callback(c.write_message, e)

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
