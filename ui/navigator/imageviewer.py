# Copyright 2021 Peppy Player peppy.player@gmail.com
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

from ui.navigator.navigator import Navigator
from util.keys import KEY_BACK

MOVE_LEFT = "left-arrow"
MOVE_RIGHT = "right-arrow"
MOVE_UP = "up-arrow"
MOVE_DOWN = "down-arrow"
FIT = "fit"
ZOOM_IN = "zoom-in"
ZOOM_OUT = "zoom-out"
ROTATE = "rotate"

class ImageViewerNavigator(Navigator):
    """ Image Viewer navigator """

    def __init__(self, util, bounding_box, listeners):
        """ Initializer
        
        :param util: utility object
        :param bounding_box: bounding box
        :param listeners: buttons listeners
        """
        items = []
        self.add_button(items, KEY_BACK, None, [listeners[KEY_BACK]])
        self.add_button(items, FIT, None, [listeners[FIT]])
        self.add_button(items, ZOOM_IN, None, [listeners[ZOOM_IN]])
        self.add_button(items, ZOOM_OUT, None, [listeners[ZOOM_OUT]])
        self.add_button(items, MOVE_LEFT, None, [listeners[MOVE_LEFT]])
        self.add_button(items, MOVE_RIGHT, None, [listeners[MOVE_RIGHT]])
        self.add_button(items, MOVE_UP, None, [listeners[MOVE_UP]])
        self.add_button(items, MOVE_DOWN, None, [listeners[MOVE_DOWN]])
        self.add_button(items, ROTATE, None, [listeners[ROTATE]])

        Navigator.__init__(self, util, bounding_box, "image.viewer.navigator", items, None)
