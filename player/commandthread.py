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

from threading import Thread

class CommandThread(Thread):
    """ Custom thread class which returns value on join """
    
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        """ Initializer """
        
        Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)
        self.return_value = None

    def run(self):
        """ Start thread method """
        
        self.return_value = self._target(*self._args, **self._kwargs)

    def join(self, timeout):
        """ Join method
        
        :param timeout: thread timeout
        :return: thread method return value
        """
        Thread.join(self, timeout)
        return self.return_value
