import os
import json
import logging

from tornado.web import RequestHandler

class UploadHandler(RequestHandler):
    def initialize(self, path):
        self.root = path

    def post(self):
        arguments = self.request.arguments

        if "language" in arguments.keys():
            self.saveRadioPlaylists(arguments)
        else:
            self.saveStreamPlaylist(arguments)

    def delete(self):
        j = json.loads(self.request.body.decode("utf-8"))
        image_path = j["imagePath"]
        streamimage = "streamimage/"
        radioimage = "flag/"
        path = None
        
        if image_path and image_path.startswith(streamimage):
            filename = image_path[len(streamimage):]
            path = self.root + os.sep + "streams" + os.sep + filename
        elif image_path and image_path.startswith(radioimage):
            filename = image_path[len(radioimage):]
            path = self.root + os.sep + "languages" + os.sep + filename

        if path == None:
            logging.debug(f"No path in delete: {image_path}")
            return

        try:
            logging.debug(f"Deleting file: {path}")
            os.remove(path) 
            logging.debug(f"Deleted file: {path}")
        except Exception as e:
            logging.debug(e)
            self.set_status(500)
            self.finish(json.dumps({ "message": f"Cannot delete file: {path}" }))

    def saveRadioPlaylists(self, arguments):
        language = arguments["language"][0].decode("utf-8")
        genre = arguments["genre"][0].decode("utf-8")
        image = self.request.files["image"][0]
        filename = arguments["filename"][0].decode("utf-8")
        file = image["body"]
        path = self.root + os.sep + "languages" + os.sep + language + os.sep + "radio-stations" + os.sep + \
            "Genre" + os.sep + genre + os.sep + filename
        try:
            logging.debug(f"Saving file: {path}")
            new_file = open(path, "wb")
            new_file.write(file)
            logging.debug(f"Saved file: {path}")
        except Exception as e:
            logging.debug(e)
            self.set_status(500)
            self.finish(json.dumps({ "message": f"Cannot save file: {filename}"}))

    def saveStreamPlaylist(self, arguments):
        image = self.request.files["image"][0]
        filename = arguments["filename"][0].decode("utf-8")
        file = image["body"]
        path = self.root + os.sep + "streams" + os.sep + filename
        try:
            logging.debug(f"Saving file: {path}")
            new_file = open(path, "wb")
            new_file.write(file)
            logging.debug(f"Saved file: {path}")
        except Exception as e:
            logging.debug(e)
            self.set_status(500)
            self.finish(json.dumps({ "message": f"Cannot save file: {filename}"}))
