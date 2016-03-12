# Copyright 2016 Peppy Player peppy.player@gmail.com
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

from http.server import SimpleHTTPRequestHandler
import json
import pygame
import threading
from web.server.websocket import WebSocketProtocolHandler

web_socket = None

class RequestHandler(SimpleHTTPRequestHandler):
    """ HTTP Request Handler """
    
    def do_GET(self):
        """ GET request handler. Initiates WebSocket protocol """
        u = None
        try:
            u = self.headers['upgrade']
        except:
            pass
        if u and u.lower() == 'websocket':
            self.protocol_version = 'HTTP/1.1'
            global web_socket
            if web_socket == None:
                web_socket = WebSocketProtocolHandler(self)
            web_socket.handshake()
            while True:
                if web_socket == None:
                    return
                msg = web_socket.read_message()
                if not msg: continue
                d = json.loads(msg)
                self.handle_command(d)
        else:
            super().do_GET()
            
    def log_message(self, f, *args):
        """ Empty implementation to avoid issues when used without console """
        return
    
    def handle_command(self, d):
        """ Handles commands sent from web client 
        
        :param d: command object
        """
        if d["command"] == "init":
            json_data = self.screen_to_json()
            web_socket.send_message(json_data)
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
                event = pygame.event.Event(pygame.MOUSEMOTION, **a)
                event.p = True
            event.source = "browser"
            thread = threading.Thread(target=pygame.event.post, args=[event])
            thread.start()

def send_message(msg):
    """ Sends message to browser using WebSocket
    
    :param msg: the message
    """
    global web_socket
    if web_socket != None:
        try:
            web_socket.send_message(msg)
        except:
            web_socket = None
 
def update_title(handler):
    """ Update title in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.title_to_json())
         
def update_volume(handler):
    """ Update volume in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.volume_to_json())
     
def update_genre_button(handler):
    """ Update genre in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.genre_button_to_json())

def update_home_button(handler):
    """ Update home in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.home_button_to_json())

def update_left_button(handler):
    """ Update left button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.left_button_to_json())

def update_page_down_button(handler):
    """ Update page down button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.page_down_button_to_json())
    
def update_right_button(handler):
    """ Update right button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.right_button_to_json())
    
def update_page_up_button(handler):
    """ Update page up button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.page_up_button_to_json())
 
def create_screen(handler):
    """ Create new screen in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.screen_to_json())
     
def update_station_menu(handler):
    """ Update station menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.station_menu_to_json())
    
def update_play_button(handler):
    """ Update play button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.play_button_to_json())
    
def update_shutdown_button(handler):
    """ Update shutdown button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.shutdown_button_to_json())
    
def update_genre_menu(handler):
    """ Update genre menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.genre_menu_to_json())
    
def update_home_menu(handler):
    """ Update home menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.home_menu_to_json())
    
def update_language_menu(handler):
    """ Update language menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.language_menu_to_json())
    
def update_saver_screen(handler):
    """ Update screensaver screen in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.saver_screen_to_json())
    
def update_about_screen(handler):
    """ Update about screen in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.about_screen_to_json())
    
def start_screensaver(handler):
    """ Send start screensaver event to browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.start_screensaver_to_json())
    
def stop_screensaver(handler):
    """ Send stop screensaver event to browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.stop_screensaver_to_json())    
    
def mode_listener(handler):
    """ Send Station Screen change mode event to browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.left_button_to_json())
    send_message(RequestHandler.page_down_button_to_json())
    send_message(RequestHandler.right_button_to_json())
    send_message(RequestHandler.page_up_button_to_json())
    send_message(RequestHandler.station_menu_to_json())
        