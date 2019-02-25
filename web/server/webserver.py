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

import logging
import socket
import tornado.httpserver
import tornado.ioloop
import tornado.web
import socket
import os
import json

from threading import Thread, RLock
from util.config import WEB_SERVER, HTTP_PORT
from util.keys import KEY_ABOUT
from web.server.jsonfactory import JsonFactory
from web.server.websockethandler import WebSocketHandler
from ui.button.button import Button

class WebServer(object):
    """ Starts Tornado web server in a separate thread """
    
    def __init__(self, util, peppy):
        """ Initializer. Start web server in separate thread
        
        :param util: utility object contains configuration settings
        :param peppy: the reference to the root object
        """
        self.lock = RLock()
        self.config = util.config
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
        index = "index.html"
        host = socket.gethostbyname(socket.gethostname())
        port = self.config[WEB_SERVER][HTTP_PORT]
        
        if tornado.version.startswith("5"):
            import asyncio
            asyncio.set_event_loop(asyncio.new_event_loop())
        
        indexHandler = (r"/()", tornado.web.StaticFileHandler, {"path": root, "default_filename": "index.html"})
        staticHandler = (r"/web/client/(.*)", tornado.web.StaticFileHandler, {"path": root + "/web/client"})
        fontHandler = (r"/font/(.*)", tornado.web.StaticFileHandler, {"path": root + "/font"})
        d = {"redraw_web_ui": self.redraw_web_ui, "web_clients": self.web_clients}
        webSocketHandler = (r"/ws", WebSocketHandler, d)
        application = tornado.web.Application([indexHandler, staticHandler, fontHandler, webSocketHandler])
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(port)
        logging.debug("Web Server Started at %s:%s", host, port) 
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
        
        