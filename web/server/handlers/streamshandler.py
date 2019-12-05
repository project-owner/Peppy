import os
import json

from tornado.web import RequestHandler

class StreamsHandler(RequestHandler):
    def initialize(self, util):
        self.util = util

    def get(self):
        streams_str = self.util.get_streams_string()
        d = json.dumps(streams_str)
        self.write(d)
        return

    def put(self):
        value = json.loads(self.request.body)
        try:
            self.util.save_streams(value)
        except Exception as e:
            print(e)
