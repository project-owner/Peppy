# Copyright 2023 Peppy Player peppy.player@gmail.com
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
import logging

from tornado.web import RequestHandler
from voiceassistant.voiceassistantutil import VoiceAssistantUtil
from voiceassistant.voskassistant.voskutil import VoskUtil, FOLDER
from util.util import VOICE_ASSISTANT_LANGUAGE_CODES

class VoiceAssistantHandler(RequestHandler):
    def initialize(self, util):
        self.util = util
        self.config = util.config
        self.voice_assistant_util = VoiceAssistantUtil()
        self.vosk_util = VoskUtil(util)

    def get(self, command):
        if command == "config":
            config = self.voice_assistant_util.load_config()
            config[FOLDER] = self.vosk_util.models_folder_config
            d = json.dumps(config)
            self.write(d)
        elif command == "voskmodels" and self.request.arguments:
            language = self.get_argument("language")
            language_code = self.config[VOICE_ASSISTANT_LANGUAGE_CODES][language]
            config = self.vosk_util.get_models()
            lang_config = config[language_code]
            d = json.dumps(lang_config)
            self.write(d)
        elif command == "downloadprogress":
            progress = {"progress": self.vosk_util.get_download_progress()}
            d = json.dumps(progress)
            self.write(d)

    def put(self, command):
        if command == "downloadmodel":
            try:
                values = json.loads(self.request.body.decode("utf-8"))
                url = values["url"]
                logging.debug(f"Download model {url}")
                self.vosk_util.download_model(values["name"], url, values["size"])
            except Exception as e:
                self.set_status(500, reason=str(e))
                self.finish()
        elif command == "resetprogress":
            try:
                self.vosk_util.reset_progress()
            except Exception as e:
                logging.debug(e)
        elif command == "setcurrentmodel":
            try:
                values = json.loads(self.request.body.decode("utf-8"))
                self.vosk_util.set_current_model(values["name"], values["language"])
            except Exception as e:
                logging.debug(e)   
        else:
            try:
                value = json.loads(self.request.body)
                self.voice_assistant_util.save_config(value)
                self.vosk_util.save_models_folder_config(value)
            except Exception as e:
                logging.debug(e)

    def delete(self, command):
        try:
            if self.request.arguments:
                name = self.get_argument("name")
                self.vosk_util.delete_model(name)
        except Exception as e:
            logging.debug(e)
            self.set_status(500, reason=str(e))
            return self.finish()
