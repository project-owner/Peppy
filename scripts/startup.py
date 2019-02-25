# Copyright 2019 PeppyMeter peppy.player@gmail.com
# 
# This file is part of PeppyMeter.
# 
# PeppyMeter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PeppyMeter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PeppyMeter. If not, see <http://www.gnu.org/licenses/>.

import sys
import logging

from threading import Thread

class Startup(object):
    """ Example of the asynchronous startup script. """
        
    def __init__(self):
        """ Initializer """
        
        self.type = "async"
        logging.debug("Startup script initializer called")
            
    def start_thread(self):
        """ Start thread """
        
        self.running = True
        thread = Thread(target = self.run_async_thread)
        thread.start()
        
    def run_async_thread(self):
        """ Async thread method """
        
        logging.debug("Started startup asynchronous thread")
