# Copyright 2022 Peppy Player peppy.player@gmail.com
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

from tornado.web import RequestHandler

NAME = "name"
DESCRIPTION = "description"
URL = "url"
ONLINE = "online"
STATUS = "status"
TYPE = "type"
IMAGE_NAME = "image_name"

class PodcastHandler(RequestHandler):
    def initialize(self, peppy):
        self.podcast_util = peppy.util.get_podcasts_util()

    def get(self, resource):
        try:
            if resource == "links":
                payload = self.podcast_util.get_podcasts_links()
                if not payload:
                    return
            elif resource == "info":
                info = self.podcast_util.get_podcasts_info()
                if not info:
                    return
                payload = self.convert_info_to_dictionaries(info)
            elif resource.startswith("url="):
                url = resource.split("=")
                info = self.podcast_util.get_podcast_info(None, url[1], include_icon=False)
                payload = self.convert_info_to_dictionary(info)
            elif resource.startswith("episodes/url="):
                url = resource.split("=")
                episodes = self.podcast_util.get_episodes(url[1])
                payload = self.convert_episodes_to_dictionaries(episodes)
            self.write(json.dumps(payload))
        except:
            self.set_status(500)
            return self.finish()

    def convert_info_to_dictionaries(self, info):
        result = []
        for i in info:
            new_dict = self.convert_info_to_dictionary(i)
            result.append(new_dict)
        return result

    def convert_info_to_dictionary(self, info):
        new_dict = {}
        new_dict[NAME] = getattr(info, NAME, None)
        new_dict[DESCRIPTION] = getattr(info, DESCRIPTION, None)
        new_dict[URL] = getattr(info, URL, None)
        new_dict[ONLINE] = getattr(info, ONLINE, None)
        new_dict[IMAGE_NAME] = getattr(info, IMAGE_NAME, None)
        return new_dict

    def convert_episodes_to_dictionaries(self, episodes):
        result = []
        for e in episodes:
            new_dict = self.convert_episode_to_dictionary(e)
            result.append(new_dict)
        return result

    def convert_episode_to_dictionary(self, episode):
        new_dict = {}
        new_dict[NAME] = getattr(episode, NAME, None)
        new_dict[DESCRIPTION] = getattr(episode, DESCRIPTION, None)
        new_dict[URL] = getattr(episode, URL, None)
        new_dict[ONLINE] = getattr(episode, ONLINE, None)
        new_dict[STATUS] = getattr(episode, STATUS, None)
        new_dict[TYPE] = getattr(episode, TYPE, None)
        return new_dict
