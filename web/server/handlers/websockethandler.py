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
import pygame
import json
import tornado.websocket

from threading import Thread

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """ Custom WebSocket handler extends Tornado handler """
    
    def initialize(self, redraw_web_ui, web_clients):
        """ Initializer
        
        :param redraw_web_ui: method to redraw the whole web UI
        :param web_clients: the list of web clients
        """
        self.redraw_web_ui = redraw_web_ui
        self.web_clients = web_clients
    
    def open(self):
        """ Handle opening WebSocket connection """
        
        if self not in self.web_clients:
            self.web_clients.append(self)
            logging.debug("Added web client")
      
    def on_message(self, message):
        """ Handle message received from web UI """
        
        d = json.loads(message)
        self.handle_command(d)
 
    def on_close(self):
        """ Handle closing WebSocket connection """
        
        if self in self.web_clients:
            self.web_clients.remove(self)
            logging.debug("Removed web client")
 
    def check_origin(self, origin):
        """ Check request origin """
        
        return True
    
    def handle_command(self, d):
        """ Handle commands sent from web client 
        
        :param d: command object
        """
        if d["command"] == "init":
            self.redraw_web_ui()
        elif d["command"] == "mouse":
            a = {}
            a["pos"] = (d["x"], d["y"])
            a["button"] = d["b"]
            event = None
            if d["d"] == 0:
                event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, **a)
            elif d["d"] == 1:
                event = pygame.event.Event(pygame.MOUSEBUTTONUP, **a)
            elif d["d"] == 2:
                a["buttons"] = [1]
                event = pygame.event.Event(pygame.MOUSEMOTION, **a)
                event.p = True
            event.source = "browser"
            thread = Thread(target=pygame.event.post, args=[event])
            thread.start()
