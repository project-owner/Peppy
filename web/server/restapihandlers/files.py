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

FILE_NAME = "file_name"
FILE_TYPE = "file_type"
FOLDER = "folder"
HAS_EMBEDDED_IMAGE = "has_embedded_image"
URL = "url"
STORE_FOLDER_NAME = "store_folder_name"
LOAD_IMAGES = "load_images"

class FilesHandler(RequestHandler):
    def initialize(self, peppy):
        self.file_util = peppy.util.file_util

    def get(self):
        try:
            current_folder = self.file_util.current_folder
            store_folder_name = False
            load_images = False

            if self.request.arguments:
                current_folder = self.get_argument("folder", default=current_folder)
                store_folder_name = self.get_argument("store", default=False)
                if isinstance(store_folder_name, str):
                    if store_folder_name == "True":
                        store_folder_name = True
                    else:
                        store_folder_name = False
                load_images = self.get_argument("images", default=False)
                if isinstance(load_images, str):
                    if load_images == "True":
                        load_images = True
                    else:
                        load_images = False

            file_objects = self.file_util.get_folder_content(current_folder, store_folder_name, load_images)

            if file_objects == None:
                return

            folder_content = self.convert_to_dictionaries(file_objects)
            files = {"current.folder": current_folder, "files": folder_content}

            self.write(json.dumps(files))
        except:
            self.set_status(500)
            return self.finish()

    def convert_to_dictionaries(self, files):
        result = []
        for file in files:
            new_dict = {}
            new_dict[FILE_NAME] = getattr(file, FILE_NAME, None)
            new_dict[FILE_TYPE] = getattr(file, FILE_TYPE, None)
            new_dict[FOLDER] = getattr(file, FOLDER, None)
            new_dict[HAS_EMBEDDED_IMAGE] = getattr(file, HAS_EMBEDDED_IMAGE, False)
            new_dict[URL] = getattr(file, URL, None)
            result.append(new_dict)
        return result

