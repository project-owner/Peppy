# Copyright 2019 Peppy Player peppy.player@gmail.com
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

import dbus
import logging
import time

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
from gi.repository import GLib

REMOTE_CONTROL_NAME = "org.gnome.ShairportSync.RemoteControl"
ADVANCED_REMOTE_CONTROL_NAME = "org.gnome.ShairportSync.AdvancedRemoteControl"
SHAIRPORT_SYNC_NAME = "org.gnome.ShairportSync"
SHAIRPORT_SYNC_PATH = "/org/gnome/ShairportSync"
DBUS_PROPERTIES = "org.freedesktop.DBus.Properties"
VOLUME_PROPERTY = "AirplayVolume"
PLAYER_STATE_PROPERTY = "PlayerState"
PLAYER_STATE_NA = "Not Available"
PLAYER_STATE_STOPPED = "Stopped"
PLAYER_STATE_PAUSED = "Paused"
PLAYER_STATE_PLAYING = "Playing"

class ShairportDbusConnector(object):
    """ This class provides dbus metadata reader and commander for shairport-sync. """

    def __init__(self, util, notify_player_listeners):
        """ Initializer 
        
        :param util: utility functions
        :param notify_player_listeners: player callback
        """        
        self.util = util
        self.notify_player_listeners = notify_player_listeners
        self.loop = GLib.MainLoop()
        self.bus = dbus.SystemBus()
        self.init_dbus_proxy()
        self.init_dbus_properties()

    def init_dbus_proxy(self):
        """ Initialize dbus proxy object """

        attempts = 5
        timeout = 1
        self.proxy = None

        for n in range(attempts):
            try:
                self.proxy = self.bus.get_object(SHAIRPORT_SYNC_NAME, SHAIRPORT_SYNC_PATH)
            except Exception as e:
                logging.debug(e)
            if self.proxy:
                break
            else:
                if n == (attempts - 1):
                    return
                else:
                    time.sleep(timeout)
                    continue

    def init_dbus_properties(self):
        """ Initialize dbus properties object """

        self.remote_control = None
        self.dbus_properties = None
        if self.proxy:
            self.remote_control = dbus.Interface(self.proxy, dbus_interface=REMOTE_CONTROL_NAME)
            self.dbus_properties = dbus.Interface(self.remote_control, DBUS_PROPERTIES)

    def get_dbus_prop(self, prop):
        """ Get dbus property defined by name

        :param prop: property name

        :return: property value
        """
        state = None
        attempts = 2
        for _ in range(attempts):
            try:
                state = self.dbus_properties.Get(REMOTE_CONTROL_NAME, prop)
            except Exception as e:
                logging.debug(e)
                self.init_dbus_proxy()
                self.init_dbus_properties()
                continue
            else:
                break
        return state

    def play_pause(self, flag):
        """ Play/pause

        :param flag: True - pause, False - play
        """
        state = self.get_dbus_prop(PLAYER_STATE_PROPERTY)
        if flag and state == PLAYER_STATE_PLAYING:
            self.remote_control.Pause()
        elif not flag and (state == PLAYER_STATE_STOPPED or state == PLAYER_STATE_PAUSED):
            self.remote_control.Play()

    def play(self):
        """ Play """

        self.remote_control.Play()

    def pause(self):
        """ Pause """

        state = self.get_dbus_prop(PLAYER_STATE_PROPERTY)
        if state == PLAYER_STATE_PLAYING:
            self.remote_control.Pause()

    def next(self):
        """ Next track """

        self.remote_control.Next()

    def previous(self):
        """ Previous track """

        self.remote_control.Previous()

    def set_volume(self, level):
        """ Set volume level

        :param level: volume in range 0-100
        """
        old = self.get_dbus_prop(VOLUME_PROPERTY)
        if old == None:
            return

        if old == 0.0:
            old = -30
        new = -(30 - (level * (30 / 100))) # convert from 0-100 range to -30-0

        try:
            if abs(old) > abs(new):
                steps = round((abs(old) - abs(new)) / 2.0)
                for _ in range(steps):
                    self.remote_control.VolumeUp()
            elif abs(old) < abs(new):
                steps = round((abs(new) - abs(old)) / 2.0)
                for _ in range(steps):
                    self.remote_control.VolumeDown()
        except:
            pass

    def mute(self):
        """ Mute """

        pass
