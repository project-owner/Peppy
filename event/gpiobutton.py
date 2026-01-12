# Copyright 2020 Peppy Player peppy.player@gmail.com
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

import pygame
from util.keys import KEY_SUB_TYPE, SUB_TYPE_KEYBOARD, KEY_ACTION, \
    KEY_KEYBOARD_KEY, USER_EVENT_TYPE
import logging
from datetime import timedelta

class GpioButtonsMonitor(object):

    def __init__(self):
        try:
            import gpiod
            self.gpiod = gpiod
        except ImportError:
            logging.error("Failed to import gpiod module")
        from .gpiomon import GPIOMon
        self.GPIOMon = GPIOMon
        self.monitors = {}
        self.buttons = {}

    def add_button(self, pin, key):
        raw = pin.split("/")
        if len(raw) == 1:
            chip = 'gpiochip0'
            pin = int(raw[0])
        else:
            chip, pin = raw[0], int(raw[1])
        self.buttons[chip, pin] = key
        if chip not in self.monitors:
            self.monitors[chip] = self.GPIOMon(
                dev_name=f"/dev/{chip}",
                lines=pin,
                settings=self.gpiod.LineSettings(
                    edge_detection=self.gpiod.line.Edge(self.gpiod.line.Edge.BOTH),
                    bias=self.gpiod.line.Bias(self.gpiod.line.Bias.PULL_UP),
                    debounce_period=timedelta(milliseconds=50),
                ),
                handler=self.on_interrupt,
                kwargs={'chip': chip}
            )
        else:
            self.monitors[chip].add_lines(pin)

    def on_interrupt(self, event, chip):
        if (chip, event.line_offset) in self.buttons:
            d = {
                KEY_SUB_TYPE: SUB_TYPE_KEYBOARD,
                KEY_KEYBOARD_KEY: self.buttons[(chip, event.line_offset)],
                KEY_ACTION: pygame.KEYDOWN if event.event_type == self.gpiod.EdgeEvent.Type.FALLING_EDGE else pygame.KEYUP
            }
            pygame.event.post(pygame.event.Event(USER_EVENT_TYPE, **d))

    def start(self):
        for monitor in self.monitors.values():
            monitor.start()
