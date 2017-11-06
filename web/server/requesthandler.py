# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
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

import json
import pygame

from http.server import SimpleHTTPRequestHandler
from web.server.websocket import WebSocketProtocolHandler
from threading import Thread
from queue import Queue

web_socket = None
message_queue = Queue()

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
            thread = Thread(target=pygame.event.post, args=[event])
            thread.start()        

def send_message(msg):
    """ Add message to the queue
    
    :param msg: message
    """
    if msg: message_queue.put(msg)

def process_message_queue():
    """ Wait for the message in the queue. Call web socket whenever message is available """
    
    while True:
        msg = message_queue.get()
        if msg == None: return       
        global web_socket
        if web_socket != None:
            try:
                web_socket.send_message(msg)
            except:
                web_socket = None

message_thread = Thread(target = process_message_queue)
message_thread.start()

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

def update_about_button(handler):
    """ Update about button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.about_button_to_json())
    
def update_home_player_button(handler):
    """ Update player button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.home_player_button_to_json())
    
def update_home_language_button(handler):
    """ Update language button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.home_language_button_to_json())
    
def update_home_saver_button(handler):
    """ Update saver button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.home_saver_button_to_json())
    
def update_home_back_button(handler):
    """ Update back button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.home_back_button_to_json())
    
def update_language_home_button(handler):
    """ Update home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.language_home_button_to_json())
     
def update_language_player_button(handler):
    """ Update player button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.language_player_button_to_json())

def update_saver_home_button(handler):
    """ Update saver button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.saver_home_button_to_json())
 
def update_saver_player_button(handler):
    """ Update player button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.saver_player_button_to_json())
        
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
    send_message(RequestHandler.screen_to_json())
    send_message(RequestHandler.title_to_json())
    send_message(RequestHandler.file_player_title_to_json())
    
def mode_listener(handler):
    """ Send Station Screen change mode event to browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.left_button_to_json())
    send_message(RequestHandler.page_down_button_to_json())
    send_message(RequestHandler.right_button_to_json())
    send_message(RequestHandler.page_up_button_to_json())
    send_message(RequestHandler.station_menu_to_json())
    
def update_file_player_title(handler):
    """ Update file player title in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_title_to_json())
    
def update_file_player_left_button(handler):
    """ Update file player left button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_left_button_to_json())
    
def update_file_player_right_button(handler):
    """ Update file player right button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_right_button_to_json())
    
def update_file_player_time_volume_button(handler):
    """ Update file player time/volume button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_time_volume_button_to_json())
    
def update_file_player_file_button(handler):
    """ Update file player file button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_file_button_to_json())
    
def update_file_player_home_button(handler):
    """ Update file player home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_home_button_to_json())
    
def update_file_player_shutdown_button(handler):
    """ Update file player shutdown button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_shutdown_button_to_json())
    
def update_file_player_play_button(handler):
    """ Update file player play button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_play_button_to_json())

def update_file_player_volume(handler):
    """ Update file player volume button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_volume_to_json())

def update_file_player_time_control(handler):
    """ Update file player time slider in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_time_control_to_json())

def timer_start(handler):
    """ Update file player time slider in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_timer_start_to_json())
    
def timer_stop(handler):
    """ Update file player time slider in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_player_timer_stop_to_json())
    
def update_file_browser_left_button(handler):
    """ Update file browser left button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_browser_left_button_to_json())
    
def update_file_browser_right_button(handler):
    """ Update file browser right button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_browser_right_button_to_json())
    
def update_file_browser_home_button(handler):
    """ Update file browser home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_browser_home_button_to_json())
    
def update_file_browser_user_home_button(handler):
    """ Update file browser user home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_browser_user_home_button_to_json())
    
def update_file_browser_root_button(handler):
    """ Update file browser root button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_browser_root_button_to_json())
    
def update_file_browser_parent_button(handler):
    """ Update file browser parent button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_browser_parent_button_to_json())
    
def update_file_browser_back_button(handler):
    """ Update file browser back button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_browser_back_button_to_json())
    
def update_file_browser_file_menu(handler):
    """ Update file browser file menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.file_browser_file_menu_to_json())

# site player

def update_site_player_title(handler):
    """ Update site player title in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_title_to_json())
    
def update_site_player_left_button(handler):
    """ Update left button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_left_button_to_json())
    
def update_site_player_right_button(handler):
    """ Update right button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_right_button_to_json())
    
def update_site_player_time_volume_button(handler):
    """ Update time/volume button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_time_volume_button_to_json())
    
def update_site_player_file_button(handler):
    """ Update file button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_file_button_to_json())
    
def update_site_player_home_button(handler):
    """ Update home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_home_button_to_json())
    
def update_site_player_shutdown_button(handler):
    """ Update shutdown button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_shutdown_button_to_json())
    
def update_site_player_play_button(handler):
    """ Update play button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_play_button_to_json())

def update_site_player_volume(handler):
    """ Update volume in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_volume_to_json())

def update_site_player_time_control(handler):
    """ Update time control in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_time_control_to_json())

def site_timer_start(handler):
    """ Update timer start in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_timer_start_to_json())
    
def site_timer_stop(handler):
    """ Update timer stop in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_player_timer_stop_to_json())

# news
    
def update_site_news_left_button(handler):
    """ Update left button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_news_left_button_to_json())
    
def update_site_news_right_button(handler):
    """ Update right button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_news_right_button_to_json())
    
def update_site_news_home_button(handler):
    """ Update home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_news_home_button_to_json())    
    
def update_site_news_abc_button(handler):
    """ Update abc button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_news_abc_button_to_json())
    
def update_site_news_new_books_button(handler):
    """ Update new books  button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_news_new_books_button_to_json())
    
def update_site_news_genre_button(handler):
    """ Update genre button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_news_genre_button_to_json())

def update_site_news_player_button(handler):
    """ Update player button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_news_player_button_to_json())

def update_site_news_back_button(handler):
    """ Update back button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_news_back_button_to_json())
    
def update_site_news_book_menu(handler):
    """ Update book menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_news_book_menu_to_json())

# abc

def update_site_abc_left_button(handler):
    """ Update left button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_abc_left_button_to_json())
    
def update_site_abc_right_button(handler):
    """ Update right button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_abc_right_button_to_json())
    
def update_site_abc_home_button(handler):
    """ Update home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_abc_home_button_to_json())    
    
def update_site_abc_abc_button(handler):
    """ Update abc button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_abc_abc_button_to_json())
    
def update_site_abc_new_books_button(handler):
    """ Update new books  button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_abc_new_books_button_to_json())
    
def update_site_abc_genre_button(handler):
    """ Update genre button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_abc_genre_button_to_json())

def update_site_abc_player_button(handler):
    """ Update player button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_abc_player_button_to_json())

def update_site_abc_back_button(handler):
    """ Update back button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_abc_back_button_to_json())
    
def update_site_abc_menu(handler):
    """ Update abc menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_abc_menu_to_json())
    
# authors

def update_site_authors_left_button(handler):
    """ Update left button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_authors_left_button_to_json())
    
def update_site_authors_right_button(handler):
    """ Update right button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_authors_right_button_to_json())
    
def update_site_authors_home_button(handler):
    """ Update home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_authors_home_button_to_json())    
    
def update_site_authors_abc_button(handler):
    """ Update abc button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_authors_abc_button_to_json())
    
def update_site_authors_new_books_button(handler):
    """ Update new books button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_authors_new_books_button_to_json())
    
def update_site_authors_genre_button(handler):
    """ Update genre button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_authors_genre_button_to_json())

def update_site_authors_player_button(handler):
    """ Update player button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_authors_player_button_to_json())

def update_site_authors_back_button(handler):
    """ Update back button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_authors_back_button_to_json())
    
def update_site_authors_menu(handler):
    """ Update authors menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_authors_menu_to_json())
    
# author books
    
def update_author_books_left_button(handler):
    """ Update left button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.author_books_left_button_to_json())
    
def update_author_books_right_button(handler):
    """ Update right button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.author_books_right_button_to_json())
    
def update_author_books_home_button(handler):
    """ Update home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.author_books_home_button_to_json())    
    
def update_author_books_abc_button(handler):
    """ Update abc button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.author_books_abc_button_to_json())
    
def update_author_books_new_books_button(handler):
    """ Update new books button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.author_books_new_books_button_to_json())
    
def update_author_books_genre_button(handler):
    """ Update genre button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.author_books_genre_button_to_json())

def update_author_books_player_button(handler):
    """ Update player button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.author_books_player_button_to_json())

def update_author_books_back_button(handler):
    """ Update back button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.author_books_back_button_to_json())
    
def update_author_books_book_menu(handler):
    """ Update book menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.author_books_book_menu_to_json())

# genre

def update_site_genre_left_button(handler):
    """ Update left button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_genre_left_button_to_json())
    
def update_site_genre_right_button(handler):
    """ Update right button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_genre_right_button_to_json())
    
def update_site_genre_home_button(handler):
    """ Update home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_genre_home_button_to_json())    
    
def update_site_genre_abc_button(handler):
    """ Update abc button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_genre_abc_button_to_json())
    
def update_site_genre_new_books_button(handler):
    """ Update new books button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_genre_new_books_button_to_json())
    
def update_site_genre_genre_button(handler):
    """ Update genre button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_genre_genre_button_to_json())

def update_site_genre_player_button(handler):
    """ Update player button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_genre_player_button_to_json())

def update_site_genre_back_button(handler):
    """ Update back button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_genre_back_button_to_json())
    
def update_site_genre_menu(handler):
    """ Update genre menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.site_genre_menu_to_json())

# genre books
    
def update_genre_books_left_button(handler):
    """ Update left button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.genre_books_left_button_to_json())
    
def update_genre_books_right_button(handler):
    """ Update right button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.genre_books_right_button_to_json())
    
def update_genre_books_home_button(handler):
    """ Update home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.genre_books_home_button_to_json())    
    
def update_genre_books_abc_button(handler):
    """ Update abc button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.genre_books_abc_button_to_json())
    
def update_genre_books_new_books_button(handler):
    """ Update new books button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.genre_books_new_books_button_to_json())
    
def update_genre_books_genre_button(handler):
    """ Update genre button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.genre_books_genre_button_to_json())

def update_genre_books_player_button(handler):
    """ Update player button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.genre_books_player_button_to_json())

def update_genre_books_back_button(handler):
    """ Update back button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.genre_books_back_button_to_json())
    
def update_genre_books_book_menu(handler):
    """ Update book menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.genre_books_book_menu_to_json())

# book track

def update_book_track_left_button(handler):
    """ Update left button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.book_track_left_button_to_json())
    
def update_book_track_right_button(handler):
    """ Update right button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.book_track_right_button_to_json())
    
def update_book_track_home_button(handler):
    """ Update home button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.book_track_home_button_to_json())    
    
def update_book_track_abc_button(handler):
    """ Update abc button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.book_track_abc_button_to_json())
    
def update_book_track_new_books_button(handler):
    """ Update new books button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.book_track_new_books_button_to_json())
    
def update_book_track_genre_button(handler):
    """ Update genre button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.book_track_genre_button_to_json())

def update_book_track_player_button(handler):
    """ Update player button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.book_track_player_button_to_json())

def update_book_track_back_button(handler):
    """ Update back button in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.book_track_back_button_to_json())
    
def update_book_track_menu(handler):
    """ Update track menu in browser
    
    :param handler: request handler  
    """
    send_message(RequestHandler.book_track_menu_to_json())


            