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

import os
import sys
import logging
import shutil
import codecs
import requests
import psutil

from configparser import ConfigParser
from operator import itemgetter
from pathlib import Path
from voiceassistant.voiceassistantutil import VOICE_ASSISTANT_FOLDER
from util.keys import UTF8
from util.config import VOICE_ASSISTANT_LANGUAGE_CODES
from threading import RLock, Thread
from zipfile import ZipFile
from vosk import MODEL_LIST_URL, Model

VOSK_MODEL_PATH = "VOSK_MODEL_PATH"
VOICE_ASSISTANT_FOLDER = "voiceassistant"
VOSK_FOLDER = "voskassistant"
VOSK_CONFIG_FILENAME = "vosk-config.txt"
VOSK_MODELS_FOLDER = "vosk.models.folder"
DEFAULT_MODEL_FOLDER = "/home/pi/vosk-models"
FOLDER = "folder"
VOSK_MODELS = "models"
DEFAULT_LANGUAGE = "en-us"
MODEL_NAME = "name"
MODEL_SIZE = "size"
MODEL_SIZE_BYTES = "size_bytes"
MODEL_SIZE_UNIT = "unit"
MODEL_URL = "url"
MODEL_REMOTE = "remote"
MODEL_CURRENT = "current"
DIVIDER_MB = 1024.0 ** 2
DIVIDER_GB = 1024.0 ** 3
FORMATTER = "{:.1f}"

class VoskUtil(object):
    """ Vosk Assistant """
    
    lock = RLock()
    progress = {"progress": 0}

    def __init__(self, util):
        """ Initializer
        
        :param util: utility object which contains configuration
        """
        self.util = util
        self.config = util.config
        self.CURRENT_MODELS_FILE_PATH = os.path.join(os.getcwd(), VOICE_ASSISTANT_FOLDER, VOSK_FOLDER, VOSK_CONFIG_FILENAME)
        self.current_models_config_parser = ConfigParser()
        self.models_folder_config = ""
        self.get_models_folder()

    def get_models_folder(self):
        """ Get the models folder from config file and set environment variable """

        self.current_models_config_parser.optionxform = str
        self.current_models_config_parser.read(self.CURRENT_MODELS_FILE_PATH, encoding=UTF8)

        try:
            self.models_folder_config = self.current_models_config_parser.get(VOSK_MODELS_FOLDER, FOLDER)
            if self.models_folder_config:
                os.environ[VOSK_MODEL_PATH] = self.models_folder_config
            else:
                os.environ[VOSK_MODEL_PATH] = DEFAULT_MODEL_FOLDER
        except:
            pass

    def get_models(self):
        """ Get local and remote models
        
        :return: dictionary of the local and remote models
        """
        local_models = self.get_local_models()

        if not self.util.connected_to_internet:
            return local_models

        remote_models = self.get_remote_models()

        for lang in remote_models.keys():
            lang_remote_models = remote_models[lang]
            try:
                lang_local_models = local_models[lang]
            except:
                continue

            if not lang_local_models:
                continue

            for remote_model in lang_remote_models:
                for local_model in lang_local_models:
                    if local_model[MODEL_NAME] == remote_model[MODEL_NAME]:
                        remote_model[MODEL_REMOTE] = False
                        if local_model[MODEL_CURRENT]:
                            remote_model[MODEL_CURRENT] = True

        return remote_models

    def get_remote_models(self):
        """ Get the remote models
        
        :return: list of remote models
        """
        models = {}
        languages = list(self.config[VOICE_ASSISTANT_LANGUAGE_CODES].values())
        lang_models = None

        try:
            response = requests.get(MODEL_LIST_URL, timeout=10)
            tmp = [m for m in response.json() if m["obsolete"] == "false"]
            lang_models = sorted(tmp, key=itemgetter("size"))
        except Exception as e:
            logging.debug(e)
            return {}

        for lang in languages:
            try:
                lang_list = models[lang]
            except:
                lang_list = []

            for model in lang_models:
                if model["lang"] != lang:
                    continue
                size_bytes = model["size"]
                (size, unit) = self.get_human_readable_size(size_bytes)
                lang_list.append({
                    MODEL_NAME: model["name"],
                    MODEL_SIZE: size, 
                    MODEL_SIZE_BYTES: size_bytes,
                    MODEL_SIZE_UNIT: unit,
                    MODEL_REMOTE: True,
                    MODEL_CURRENT: False,
                    MODEL_URL: model["url"]
                })

            if lang_list:
                models[lang] = lang_list

        return models
    
    def get_local_models(self):
        """ Get the list of locally installed models
        
        :param language: language

        :return: the list of installed models
        """
        models = {}
        folder = os.environ[VOSK_MODEL_PATH]

        if not folder or not Path(folder).exists():
            return []
        
        current_models = self.get_current_models()
        model_names = os.listdir(folder)
        for model_name in model_names:
            path = os.path.join(os.environ[VOSK_MODEL_PATH], model_name)
            
            current = False
            if current_models and model_name in list(current_models.values()):
                current = True

            language = self.get_model_language(model_name)
            if not language:
                continue

            try:
                lang_list = models[language]
            except:
                lang_list = []

            size_bytes = self.get_size(path)
            (size, unit) = self.get_human_readable_size(size_bytes)
            lang_list.append({
                MODEL_NAME: model_name,
                MODEL_SIZE: size,
                MODEL_SIZE_BYTES: size_bytes,
                MODEL_SIZE_UNIT: unit,
                MODEL_REMOTE: False, 
                MODEL_CURRENT: current
            })
            models[language] = lang_list

        return models
    
    def get_human_readable_size(self, size_bytes):
        """ Get human readable model size
        
        :param size_bytes: size in bytes

        :return: human readable size e.g. 40 and unit e.g. MB
        """
        mbs = size_bytes / DIVIDER_MB

        if mbs >= 1000:
            gbs = size_bytes / DIVIDER_GB
            size = FORMATTER.format(gbs)
            unit = "gb"
        else:
            size = FORMATTER.format(mbs)
            unit = "mb"

        return (size, unit)
    
    def get_model_language(self, model_name):
        """ Get model language
        
        :param model_name: model name

        :return: language code
        """
        language_codes = list(self.config[VOICE_ASSISTANT_LANGUAGE_CODES].values())
        language = None

        for language_code in language_codes:
            if "-" + language_code + "-" in model_name:
                language = language_code
                break
            
        return language

    def get_model(self, language):
        """ Get the installed model by language. 
        If not found return the deault model for English
        
        :param language: language

        :return: model
        """
        current_model_name = None
        current_models = self.get_current_models()
        
        try:
            current_model_name = current_models[language]
            path = os.path.join(os.environ[VOSK_MODEL_PATH], current_model_name)
        except:
            pass

        if not current_model_name:
            logging.debug(f"The current model for language '{language}' not found")
            language = DEFAULT_LANGUAGE
            try:
                current_model_name = current_models[language]
                path = os.path.join(os.environ[VOSK_MODEL_PATH], current_model_name)
            except:
                logging.debug(f"The current model for language '{language}' not found")

        if not current_model_name:
            return None

        model = None

        try:
            model = self.load_model(path, current_model_name, language)
        except:
            pass

        return model
    
    def load_model(self, path, model_name, language):
        """ Load Vosk model

        :param path: path to the model
        :param model_name: model name
        :param language: language
        
        :return: Vosk model
        """
        model = None

        if not os.path.exists(path):
            logging.debug(f"Path {path} doesn't exist")
            return model

        try:
            logging.debug(f"Loading a vosk model from the path '{path}' with name '{model_name}' for language '{language}'...")
            model = Model(model_path=path, model_name=model_name, lang=language)
            logging.debug(f"Loaded vosk model from the path '{path}'")
        except Exception as e:
            logging.debug(e)

        return model

    def get_size(self, path):
        """ Get model size
        
        :param path: path to the model

        :return: model size in bytes
        """
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)

        return total_size

    def get_current_models(self):
        """ Get the current models from the vosk assistant configuration file
        
        :return: configuration dictionary
        """
        self.current_models_config_parser.optionxform = str
        self.current_models_config_parser.read(self.CURRENT_MODELS_FILE_PATH, encoding=UTF8)

        models = {}
        languages = list(self.config[VOICE_ASSISTANT_LANGUAGE_CODES].values())
        for lang in languages:
            try:
                model = self.current_models_config_parser.get(VOSK_MODELS, lang)
                if model:
                    models[lang] = model
            except:
                pass

        return models

    def delete_model(self, model_name):
        """ Delete Vosk model from file system and config file
        
        :param model_name: model name
        """
        folder = os.environ[VOSK_MODEL_PATH]
        path = os.path.join(os.environ[VOSK_MODEL_PATH], model_name)

        if not folder or not Path(folder).exists() or not Path(path).exists():
            message = f"Model {model_name} doesn't exist"
            logging.debug(message)
            raise Exception(message)
        
        shutil.rmtree(path)

        current_models = self.get_current_models()
        new_models = { k:v for k, v in current_models.items() if v != model_name }

        config_parser = ConfigParser()
        config_parser.optionxform = str
        path = os.path.join(os.getcwd(), VOICE_ASSISTANT_FOLDER, VOSK_FOLDER, VOSK_CONFIG_FILENAME)
        config_parser.read(path, encoding=UTF8)
        config_parser.remove_section(VOSK_MODELS)
        config_parser.add_section(VOSK_MODELS)

        for k, v in new_models.items():
            config_parser.set(VOSK_MODELS, k, v)

        with codecs.open(path, 'w', UTF8) as file:
            config_parser.write(file)

    def download_model(self, model_name, url, size_bytes):
        """ Start model downloading thread.
        First, check that the folder for models exists, if not create it
        Second, check that there is enough disk space and that the model doesn't exist already
        
        :param model_name: model name
        :param url: model URL
        :param size_bytes: model size in bytes
        """
        models_folder = os.environ[VOSK_MODEL_PATH]

        if not Path(models_folder).exists():
            logging.debug(f"Folder {models_folder} doesn't exist")
            logging.debug(f"Creating folder {models_folder} ...")
            try:
                os.makedirs(models_folder)
            except Exception as e:
                logging.debug(e)    
                raise e

        path = os.path.join(models_folder, model_name)
        disk_usage_bytes = psutil.disk_usage('/')
        free_bytes = disk_usage_bytes.free

        if size_bytes * 2 >= free_bytes:
            message = f"Error: {free_bytes} bytes not enough to save model of size {size_bytes} bytes"
            logging.debug(message)
            raise Exception(message)

        if Path(path).exists():
            message = f"File {path} exist already"
            logging.debug(message)
            raise Exception(message)

        thread = Thread(target=self.download_model_thread, args=[model_name, url])
        thread.start()

    def download_model_thread(self, model_name, url):
        """ Model downloading thread function
        
        :param model_name: model name
        :param url: model URL
        """
        path = os.path.join(os.environ[VOSK_MODEL_PATH], model_name + ".tmp")
        response = requests.get(url, stream=True, timeout=(10, 10))
        model_size = int(response.headers.get('Content-Length', 0))
        block_size = 8192
        
        total_chunks = int(model_size / block_size)
        loaded_chunks = 0
        if model_size % block_size != 0:
            total_chunks += 1

        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size): 
                if chunk:
                    f.write(chunk)
                    loaded_chunks += 1
                    self.progress["progress"] = int((loaded_chunks * 100) / total_chunks)

        if Path(path).exists():
            try:
                ZipFile(path, "r").extractall(path=os.environ[VOSK_MODEL_PATH])
                os.remove(path)
            except Exception as e:
                logging.debug(e)

    def get_download_progress(self):
        """ Get the downloading process progress
        
        :return: percentage progress
        """
        with self.lock:
            return self.progress["progress"]
        
    def reset_progress(self):
        """ Reset model downloading progress to 0 """

        with self.lock:
            self.progress["progress"] = 0

    def set_current_model(self, name, language):
        """ Set the model specified by its name as a current model
        
        :param name: model name
        :param language: model language
        """
        current_models = self.get_current_models()
        language_code = self.config[VOICE_ASSISTANT_LANGUAGE_CODES][language]
        current_models[language_code] = name
        self.current_models_config_parser.set(VOSK_MODELS, language_code, name)

        with codecs.open(self.CURRENT_MODELS_FILE_PATH, 'w', UTF8) as file:
            self.current_models_config_parser.write(file)

    def save_models_folder_config(self, config):
        """ Save models folder configuration
        
        :param config: new configuration
        """
        # self.get_models_folder()
        self.current_models_config_parser.set(VOSK_MODELS_FOLDER, FOLDER, str(config[FOLDER]))

        with codecs.open(self.CURRENT_MODELS_FILE_PATH, 'w', UTF8) as file:
            self.current_models_config_parser.write(file)
