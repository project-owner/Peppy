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
import datetime

from tornado.web import RequestHandler

COMMAND_CURRENT_FOLDER = "currentfolder"
COMMAND_CURRENT_FILE = "currentfile"
COMMAND_LIST_content = "content"
COMMAND_ROOT = "root"
COMMAND_USER_FOLDER = "userfolder"
COMMAND_UP = "up"
COMMAND_CHANGE_FOLDER = "changefolder"
COMMAND_FILE_INFO = "fileinfo"

ARGUMENT_IMAGES = "images"
ARGUMENT_METADATA = "metadata"

FOLDER = "folder"
FILE = "file"
FILES = "files"
FOLDER_IMAGE_PATH = "folder.image.path"

FILE_NAME = "file_name"
FILE_TYPE = "file_type"
FILE_SIZE = "file_size"
FILE_CREATED_TIME = "file_created_time"
FILE_MODIFIED_TIME = "file_modified_time"
FILE_ACCESSED_TIME = "file_accessed_time"
HAS_EMBEDDED_IMAGE = "has_embedded_image"
URL = "url"
STORE_FOLDER_NAME = "store_folder_name"
LOAD_IMAGES = "load_images"
FALSE = "false"
TRUE = "true"

FILE_TIME_FORMAT = "%a, %b %d, %Y, %H:%M:%S"

class FileBrowserHandler(RequestHandler):
    """
    curl http://localhost:8000/api/filebrowser
    curl http://localhost:8000/api/filebrowser?images=true - show if file has embedded image:
        {
            "file_name": "test.flac",
            "file_type": "file",
            "has_embedded_image": true,
            "url": "C:\\music\\test.flac"
        }
    curl http://localhost:8000/api/filebrowser?folder="C:\\music\\samples"
    """
    def initialize(self, peppy):
        self.util = peppy.util
        self.file_util = peppy.util.file_util
        self.read_embedded_images = False
        self.show_file_details = True

    def get(self):
        try:
            folder = self.file_util.current_folder
            store_folder_name = True
            
            if self.request.arguments:
                folder = self.get_argument("folder", default=folder)
                self.read_embedded_images = self.get_boolean_argument(ARGUMENT_IMAGES, FALSE)

            file_objects = self.file_util.get_folder_content(folder, store_folder_name, self.read_embedded_images, self.show_file_details)
            folder_image_path = self.util.get_folder_image_path(folder)

            if file_objects == None:
                files = {FOLDER: folder, FOLDER_IMAGE_PATH: folder_image_path, FILES: []}
            else:
                folder_content = self.convert_to_dictionaries(file_objects)
                files = {FOLDER: folder, FOLDER_IMAGE_PATH: folder_image_path, FILES: folder_content}

            self.write(json.dumps(files))
        except Exception as e:
            self.set_status(500)
            return self.finish()

    def get_boolean_argument(self, name, default_value):
        arg = self.get_argument(name, default=default_value)
        if not isinstance(arg, str):
            return False
        
        if arg.lower() == TRUE:
            return True
        else:
            return False    

    def convert_to_dictionaries(self, files):
        result = []
        for file in files:
            new_dict = {}
            new_dict[FILE_NAME] = getattr(file, FILE_NAME, None)
            new_dict[FILE_TYPE] = getattr(file, FILE_TYPE, None)
            
            s = getattr(file, FILE_SIZE, None)
            if s != None:
                new_dict[FILE_SIZE] = s

            t = getattr(file, FILE_CREATED_TIME, None)
            if t != None:
                new_dict[FILE_CREATED_TIME] = datetime.datetime.fromtimestamp(t).strftime(FILE_TIME_FORMAT)
            t = getattr(file, FILE_MODIFIED_TIME, None)
            if t != None:
                new_dict[FILE_MODIFIED_TIME] = datetime.datetime.fromtimestamp(t).strftime(FILE_TIME_FORMAT)
            t = getattr(file, FILE_ACCESSED_TIME, None)
            if t != None:
                new_dict[FILE_ACCESSED_TIME] = datetime.datetime.fromtimestamp(t).strftime(FILE_TIME_FORMAT)

            if self.read_embedded_images:
                new_dict[HAS_EMBEDDED_IMAGE] = getattr(file, HAS_EMBEDDED_IMAGE, False)
            
            new_dict[URL] = getattr(file, URL, None)
            result.append(new_dict)
        return result
