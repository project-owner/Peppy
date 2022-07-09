# Copyright 2019-2022 Peppy Player peppy.player@gmail.com
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

import os
import feedparser
import requests
import codecs
import json
import logging

from threading import Thread
from util.keys import *
from ui.state import State
from ui.layout.borderlayout import BorderLayout
from ui.screen.screen import PERCENT_TOP_HEIGHT, PERCENT_TITLE_FONT
from ui.screen.menuscreen import PERCENT_TOP_HEIGHT as PERCENT_TOP_HEIGHT_MENU_SCREEN
from ui.menu.menu import Menu
from util.config import PODCASTS, AUDIO_FILES, LOADING, PODCASTS_FOLDER, COLORS, COLOR_DARK, \
    UTF8, FOLDER_PLAYLISTS

FILE_PODCASTS = "podcasts.m3u"
FILE_DEFAULT_PODCAST = "podcasts.svg"
FILE_PODCASTS_JSON = "podcasts.json"

STATUS_AVAILABLE = "available"
STATUS_LOADING = "loading"
STATUS_LOADED = "loaded"

MENU_ROWS_EPISODES = 3
MENU_COLUMNS_EPISODES = 1
PAGE_SIZE_EPISODES = MENU_ROWS_EPISODES * MENU_COLUMNS_EPISODES

MENU_ROWS_PODCASTS = 2
MENU_COLUMNS_PODCASTS = 1
PAGE_SIZE_PODCASTS = MENU_ROWS_PODCASTS * MENU_COLUMNS_PODCASTS

class PodcastsUtil(object):
    """ Podcasts Utility class """
    
    def __init__(self, util):
        """ Initializer
        
        :param util: utility object
        """
        self.util = util
        self.config = util.config
        self.image_util = util.image_util
        self.podcasts_links = None
        self.summary_cache = {}
        self.loading = []
        self.available_icon = None
        self.loading_icon = None
        self.loaded_icon = None
        self.podcast_image_cache = {}
        self.podcasts_json = []
        
        layout = BorderLayout(util.screen_rect)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_TOP_HEIGHT_MENU_SCREEN, 0, 0)
        self.episode_button_font_size = int((layout.TOP.h * PERCENT_TITLE_FONT)/100.0)        
        tmp = Menu(util, (0, 0, 0), layout.CENTER, MENU_ROWS_EPISODES, MENU_COLUMNS_EPISODES)
        layout = tmp.get_layout([1]*PAGE_SIZE_EPISODES)
        self.episode_button_bb = layout.get_next_constraints()
        
        layout = BorderLayout(util.screen_rect)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_TOP_HEIGHT_MENU_SCREEN, 0, 0)
        self.podcast_button_font_size = int((layout.TOP.h * PERCENT_TITLE_FONT)/100.0)        
        tmp = Menu(util, (0, 0, 0), layout.CENTER, MENU_ROWS_PODCASTS, MENU_COLUMNS_PODCASTS)
        layout = tmp.get_layout([1]*PAGE_SIZE_PODCASTS)
        self.podcast_button_bb = layout.get_next_constraints()        
        layout = tmp = None

    def init_playback(self, state):
        """ Initialize podcasts playback
        
        :param state: button state
        """
        url = state.podcast_url
        if self.util.connected_to_internet:
            index = self.get_podcast_index(url)
            s = self.get_podcast_info(index, url)
            self.get_episodes(url)
            state.online = True
        else:
            s = self.get_podcasts_from_disk(0, 2)
            self.get_episodes_from_disk(url)
            state.online = False
        
        state.status = state.file_name = self.get_episode_status(url, state.url)  
        state.podcast_image_url = self.summary_cache[url].episodes[0].podcast_image_url

    def get_episode_status(self, podcast_url, episode_url):
        """ Episode status getter
        
        :param podcast_url: podcast url
        :param episode_url: episode url
        
        :return: episode status
        """
        try:
            episodes = self.summary_cache[podcast_url].episodes
            for episode in episodes:
                if episode.url == episode_url:
                    return episode.status
        except:
            pass

        if podcast_url != None and episode_url != None:
            return STATUS_AVAILABLE

        return None        

    def get_podcasts_links(self):
        """ Get podcasts links from file 
        
        :return: list of podcasts URLs
        """
        if self.podcasts_links != None:
            return self.podcasts_links        
        
        path = os.path.join(os.getcwd(), FOLDER_PLAYLISTS, FILE_PODCASTS)
        self.podcasts_links = []

        for encoding in ["utf8", "utf-8-sig", "utf-16"]:
            try:
                lines = codecs.open(path, "r", encoding).read().split("\n")
                break
            except Exception as e:
                logging.error(e)
        
        for line in lines:
            if len(line.strip()) == 0 or line.strip().startswith("#"): 
                continue            
            self.podcasts_links.append(line.strip())
        
        return self.podcasts_links        

    def get_podcasts_string(self):
        """ Read file

        :return: string
        """
        path = os.path.join(os.getcwd(), FOLDER_PLAYLISTS, FILE_PODCASTS)
        for encoding in ["utf8", "utf-8-sig", "utf-16"]:
            try:
                with codecs.open(path, 'r', encoding) as file:
                    return file.read()
            except Exception as e:
                logging.error(e)

    def save_podcasts(self, podcasts):
        """ Save podcasts file

        :param podcasts: file with podcasts links
        """
        path = os.path.join(os.getcwd(), FOLDER_PLAYLISTS, FILE_PODCASTS)
        with codecs.open(path, 'w', UTF8) as file:
            file.write(podcasts)

    def load_podcasts(self):
        """ Load list of all loaded podcasts/episodes from file
        
        :return: list of downloaded
        """
        podcast_folder = self.config[PODCASTS_FOLDER]
        if len(podcast_folder.strip()) == 0:
            return []
        
        podacsts_file = os.path.join(podcast_folder, FILE_PODCASTS_JSON)
        
        d = []
        try:
            with open(podacsts_file) as f:
                try:
                    d = json.load(f)
                except:
                    pass
        except:
            pass
        
        return d
            
    def get_podcasts(self, page, page_size):
        """ Get dictionary with podcasts state objects
        
        :param page: page number
        :param page_size: number of buttons per page
        
        :return: dictionary with state objects
        """ 
        result = {}       
        links = self.get_podcasts_links()
        if len(links) == 0:
            return result
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        try:
            self.podcasts_json = self.load_podcasts()
        except:
            pass              
        
        for i, link in enumerate(links[start_index : end_index]):
            try:
                p = self.summary_cache[link]
                p.index = i
                result[link] = p
                continue
            except:
                pass
            
            r = self.get_podcast_info(i, link)
            if r:
                result[link] = r
            
        return result

    def get_podcasts_info(self):
        """ Get podcasts info
        
        :return: list of podcast info
        """
        links = self.get_podcasts_links()

        if not links:
            return []

        result = []

        for i, link in enumerate(links):
            try:
                p = self.summary_cache[link]
                p.index = i
                result[link] = p
                continue
            except:
                pass

            r = self.get_podcast_info(i, link)
            if r:
                result.append(r)

        return result

    def get_podcast_info(self, index, podcast_url, include_icon=True):
        """ Get podcast info as state object
        
        :param index: podcast index
        :param podcast_url: podcast url
        :param include_icon: True - include binary icon, False - don't include
        
        :return: podcast info as State object
        """
        try:
            p = self.summary_cache[podcast_url]
            p.index = index
            return p
        except:
            pass

        try:
            response = requests.get(podcast_url, timeout=(2, 2))
            if response.status_code == 404:
                return None
            rss = feedparser.parse(response.content)
            if rss and getattr(rss, "bozo_exception", None):
                return None
        except Exception as e:
            return None
            
        s = State()
        s.index = index
        s.name = rss.feed.title
        s.l_name = s.name
        s.description = rss.feed.subtitle
        s.url = podcast_url
        s.online = True
        s.fixed_height = int(self.podcast_button_font_size * 0.8)
        s.file_type = PODCASTS
        s.comparator_item = s.index
        s.bgr = self.config[COLORS][COLOR_DARK]
        s.show_bgr = True
            
        if 'image' in rss.feed and 'href' in rss.feed.image:
            img = rss.feed.image.href.strip()
        else:
            img = ''
            
        s.image_name = img
        if include_icon:
            s.icon_base = self.get_podcast_image(img, 0.48, 0.8, self.podcast_button_bb)
        self.summary_cache[s.url] = s
        
        return s

    def get_podcasts_from_disk(self, page, page_size):
        """ Get one page of loaded podcasts
        
        :param page: page number
        :page_size: page size
        
        :return: dictionary of podcasts where the key is the podcast name
        """
        result = {}       
        self.podcasts_json = self.load_podcasts()
        if len(self.podcasts_json) == 0:
            return result
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size                
        
        for i, podcast in enumerate(self.podcasts_json[start_index : end_index]):
            try:
                p = self.summary_cache[podcast]
                result[podcast] = p
                continue
            except:
                pass
            
            result[podcast["name"]] = self.get_podcast_info_from_disk(i, podcast)
            
        return result

    def get_podcast_info_from_disk(self, index, podcast):
        """ Get the info of loaded podcast as State object
        
        :param index: podcast index
        :param podcast: podcast dictionary
        
        :return: podcast info as State object
        """
        s = State()
        s.index = index
        s.name = podcast["name"]
        s.l_name = s.name
        s.url = podcast["url"]
        s.online = False
        s.description = podcast["summary"]
        s.fixed_height = int(self.podcast_button_font_size * 0.8)
        s.file_type = PODCASTS
        s.comparator_item = s.index
        s.bgr = self.config[COLORS][COLOR_DARK]
        s.show_bgr = True
            
        try:
            img = os.path.join(self.config[PODCASTS_FOLDER], podcast["image"])                
        except:
            img = ''
            
        s.image_name = img
        s.icon_base = self.get_podcast_image(img, 0.5, 0.8, self.podcast_button_bb, False)
        self.summary_cache[s.url] = s

        return s

    def get_podcast_image(self, img_name, k, f, bb, online=True):
        """ Get podcast image
        
        :param img_name: image filename
        :param k: scale factor
        :param f: scale ratio
        :param b: bounding box
        :param online: online/offline flag
        
        :return: podcast image
        """
        podcast_image = None
        
        if len(img_name) != 0:
            cache_key = img_name + str(k) + str(f)
            try:
                podcast_image = self.podcast_image_cache[cache_key]
            except:
                pass
            
            if podcast_image != None:
                return podcast_image
        
        podcast_image = self.image_util.load_icon_main(PODCASTS, bb, k)
        cache_key = PODCASTS + str(k) + str(f) 
        if len(img_name) != 0:
            if online:
                image = self.image_util.load_image_from_url(img_name)
            else:
                image = self.image_util.load_image(img_name)
                
            if image != None:
                scale_ratio = self.image_util.get_scale_ratio((bb.w * f, bb.h * f), image[1], fit_height=True)
                podcast_image = (img_name, self.image_util.scale_image(image, scale_ratio))
                cache_key = img_name + str(k) + str(f) 
                
        self.podcast_image_cache[cache_key] = podcast_image                
        return podcast_image

    def get_podcast_page(self, url, page_size):
        """ Define podcast page number by its URL
        
        :param url: podcast url
        :param page_size: page size
        
        :return: page number for specified podcast
        """
        links = self.get_podcasts_links()
        for i, link in enumerate(links):
            if url == link:
                break
        n = int(i/page_size)
        r = int(i%page_size)
        if r > 0:
            n += 1

        if i < page_size:
            return 1
            
        return n + 1

    def get_podcast_index(self, url):
        """ Define podcast index by its URL
        
        :param url: podcast url
        
        :return: podcast index
        """
        links = self.get_podcasts_links()
        for i, link in enumerate(links):
            if url == link:
                return i
        return None

    def set_episode_icon(self, episode_name, bb, s, online=True):
        """ Set icon, status and file name on provided episode state object
        
        :param episode_name: episode name
        :param bb: bounding box
        :param s: state object
        :param online: episode status
        """
        podcast_folder = self.config[PODCASTS_FOLDER]
        
        if not online:
            filename = s.file_name
            episode_file = os.path.join(podcast_folder, s.podcast_name, filename)
            self.loaded_icon = self.image_util.load_icon_main(AUDIO_FILES, bb, 0.4)
            s.icon_base = self.loaded_icon
            s.status = STATUS_LOADED
            s.file_name = episode_file
            return
        
        filename = s.url.split('/')[-1]
        episode_file = os.path.join(podcast_folder, filename)
        
        if self.available_icon == None:
            self.available_icon = self.image_util.load_icon_main(PODCASTS, bb, 0.4)
            self.loading_icon = self.image_util.load_icon_main(LOADING, bb, 0.4)
            self.loaded_icon = self.image_util.load_icon_main(AUDIO_FILES, bb, 0.4)
        
        if episode_name in self.loading:
            s.icon_base = self.loading_icon
            s.status = STATUS_LOADING
            s.file_name = ""
        elif (self.is_episode_saved(s)) or not online:
            s.icon_base = self.loaded_icon
            s.status = STATUS_LOADED
            s.file_name = episode_file
        else:
            s.icon_base = self.available_icon
            s.status = STATUS_AVAILABLE
            s.file_name = s.url

    def clean_summary(self, summary):
        """ Clean provide summary from special characters
        
        "param summary": summary string to clean
        
        :return: clean summary string
        """
        s = summary.replace("<p>", "").replace("</p>", "")
        s = s.replace("<span>", "").replace("</span>", "")
        s = s.replace("<strong>", "").replace("</strong>", "")
        s = s.replace("<a href=\"", "").replace("</a>", "")
        s = s.replace("\">", " ").replace("\\n", " ")
        s = s.replace("&#39;", "'").replace("<br>", "")
        return s.replace("<em>", "").replace("</em>", "")

    def get_episodes(self, podcast_url):
        """ Get podcast episodes
        
        :param podcast_url: podcast URL
        
        :return: dictionary with episodes
        """
        podcast = None
        try:
            podcast = self.summary_cache[podcast_url]
            podcast_image_url = podcast.image_name
            episodes = podcast.episodes
            return episodes
        except:
            pass
        
        episodes = []
        rss = feedparser.parse(podcast_url)
        if rss == None:
            return episodes

        if podcast == None:
            index = self.get_podcast_index(podcast_url)
            podcast = self.get_podcast_info(index, podcast_url)
            podcast_image_url = podcast.image_name
        
        entries = rss.entries
        i = 0
        
        for entry in entries:
            try:
                enclosure = entry.enclosures[0]
            except:
                continue
            s = State()
            s.index = i
            s.name = entry.title
            s.l_name = s.name

            s.url = getattr(enclosure, "href", None)
            if s.url == None:
                s.url = getattr(enclosure, "url", None)
            s.length = getattr(enclosure, "length", None)
            s.type = enclosure.type

            s.description = self.clean_summary(entry.summary)
            s.fixed_height = int(self.episode_button_font_size * 0.8)
            s.file_type = PODCASTS
            s.online = podcast.online
            s.comparator_item = s.index
            s.bgr = self.config[COLORS][COLOR_DARK]
            s.show_bgr = True
            s.podcast_name = podcast.name
            s.podcast_url = podcast_url
            s.podcast_image_url = podcast_image_url
            episode_name = s.url.split("/")[-1]
            self.set_episode_icon(episode_name, self.episode_button_bb, s)
            episodes.append(s)
            i += 1
        
        self.summary_cache[podcast_url].episodes = episodes        
        return episodes

    def get_episodes_from_disk(self, podcast_url):
        """ Get podcast episodes from disk
        
        :param podcast_url: podcast URL
        
        :return: dictionary with episodes
        """
        try:
            podcast = self.summary_cache[podcast_url]
            podcast_image_url = podcast.image_name
            episodes = podcast.episodes
            return episodes
        except:
            pass
        
        episodes = []
        podcast = self.summary_cache[podcast_url]
        
        entries = []
        for p in self.podcasts_json:
            if p["url"] == podcast_url:
                try:
                    entries = p["episodes"]
                except:
                    pass 
        if len(entries) == 0:
            return []
        
        for i, entry in enumerate(entries):
            s = State()
            s.index = i
            s.name = entry["name"]
            s.l_name = s.name
            s.file_name = entry["filename"]
            s.description = entry["summary"]
            s.fixed_height = int(self.episode_button_font_size * 0.8)
            s.file_type = PODCASTS
            s.online = podcast.online
            s.comparator_item = s.index
            s.bgr = self.config[COLORS][COLOR_DARK]
            s.show_bgr = True
            s.podcast_url = podcast_url
            s.podcast_name = podcast.name
            s.url = ""
            s.podcast_image_url = podcast_image_url
            self.set_episode_icon(s.name, self.episode_button_bb, s, False)
            episodes.append(s)
        
        self.summary_cache[podcast_url].episodes = episodes        
        return episodes

    def is_episode_saved(self, s):
        """ Check if episode was saved or not
        
        :param s: episode state object
        
        :return: True - episode was saved, False - not saved
        """
        if len(self.podcasts_json) == 0:
            try:
                self.podcasts_json = self.load_podcasts()
            except:
                pass 
            if len(self.podcasts_json) == 0:
                return False
        
        for p in self.podcasts_json:
            if p["url"] == s.podcast_url:
                try:
                    episodes = p["episodes"]
                    for e in episodes:
                        if e["name"] == s.name:
                            return True
                except:
                    pass
        return False

    def save_episode(self, state, callback):
        """ Start saving thread """
        
        thread = Thread(target=self.save, args=[state, callback])
        thread.start()

    def save(self, button_state, callback):
        """ Episode saving thread
        
        :param button_state: state object defining episode details
        :param callback: callback function to call when saving finished
        """
        podcast_folder = self.config[PODCASTS_FOLDER]
        url = button_state.url
        filename = url.split('/')[-1]

        if "?" in filename:
            filename = filename.split("?")[0]    

        self.loading.append(filename)
        
        episode_file = os.path.join(podcast_folder, filename)
        self.save_file_from_web(episode_file, url)
                            
        url = button_state.podcast_image_url
        if url.startswith("http"):
            f = url.split("/")[-1]
            image_file = os.path.join(podcast_folder, f)
            self.save_file_from_web(image_file, url)
                           
        self.loading.remove(filename)
        button_state.file_name = episode_file
        self.cache_episode(button_state)
        callback()       

    def save_file_from_web(self, filename, url):
        """ Save file from web
        
        :param filename: file name
        :param url: URL of the file to save
        """
        r = requests.get(url, stream=True, timeout=(2, 2))
        size = 4096
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=size): 
                if chunk:
                    f.write(chunk)        

    def cache_episode(self, state):
        """ Cache episode
        
        :param state: state object defining episode
        """
        summary = self.clean_summary(state.description)
        episode = {
            "name": state.name, 
            "filename": state.file_name, 
            "summary": summary
        }
        
        podcast = None
        for p in self.podcasts_json:
            if p["name"] == state.podcast_name:
                podcast = p
                break
        
        if podcast == None:
            p = self.summary_cache[state.podcast_url]
            podcast_json = {
                "name": p.name,
                "url": p.url,
                "summary": self.clean_summary(p.description),
                "image": p.image_name.split("/")[-1],
                "episodes": [episode]
            }
            self.podcasts_json.append(podcast_json)
        else:
            try:
                episodes = podcast["episodes"]
                episodes.append(episode) 
            except:
                podcast["episodes"] = episode 

        self.save_podcasts_json()

    def delete_episode(self, button_state):
        """ Delete episode from disk and cache
        
        :param button_state: state object defining episode to delete
        """
        podcast_folder = self.config[PODCASTS_FOLDER]
        
        if button_state.online:
            url = button_state.url
            filename = url.split('/')[-1]
            episode_file = os.path.join(podcast_folder, filename)
        else:
            episode_file = button_state.file_name
        
        try:
            os.remove(episode_file)
        except:
            pass
        
        podcast = None
        for p in self.podcasts_json:
            if p["name"] == button_state.podcast_name:
                podcast = p
                break
        
        if podcast == None:
            return
        
        try:
            episodes = podcast["episodes"]
            for i, e in enumerate(episodes):
                if e["name"] == button_state.name:
                    del episodes[i]
            if len(episodes) == 0:
                for i, p in enumerate(self.podcasts_json):
                    if p["name"] == button_state.podcast_name:                
                        del self.podcasts_json[i]
                        self.save_podcasts_json()
                        self.delete_podcast_icon(p)
            else:
                self.save_podcasts_json()
        except:
            pass
        
    def delete_podcast_icon(self, p):
        """ Delete podcast icon from disk
        
        :param p: dictionary defining podcast
        """
        podcast_folder = self.config[PODCASTS_FOLDER]
        filename = p["image"]
        path = os.path.join(podcast_folder, filename)
        os.remove(path)
        
    def save_podcasts_json(self):
        """  Save podcasts Json file """
        
        podcast_folder = self.config[PODCASTS_FOLDER]
        filename = os.path.join(podcast_folder, FILE_PODCASTS_JSON)
        
        if len(self.podcasts_json) == 0:
            os.remove(filename)
        else:
            with open(filename, 'w') as f:
                json.dump(self.podcasts_json, f)

    def are_there_any_downloads(self):
        """ Check if there are any downloaded podcasts episodes
        
        :return: True - episodes available, False - episodes unavailable
        """
        podcast_folder = self.config[PODCASTS_FOLDER]
        
        if len(podcast_folder.strip()) == 0 or not self.is_podcast_folder_available():
            return False
        
        if [f for f in os.listdir(podcast_folder) if f.lower().endswith(FILE_PODCASTS_JSON)] == []:
            return False
        else: 
            return True
        
    def is_podcast_folder_available(self):
        """ Check if there is podcasts folder
        
        :return: True - folder available, False - unavailable
        """
        podcast_folder = self.config[PODCASTS_FOLDER]
        
        if len(podcast_folder.strip()) == 0:
            return False

        try:
            os.listdir(podcast_folder)
            return True
        except:
            return False
