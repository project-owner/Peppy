# Copyright 2022-2023 Peppy Player peppy.player@gmail.com
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
import psutil

from ui.card.card import HEADER_FOOTER_BGR, LABEL, DETAIL_VALUE, SCREEN_BGR, ICON, ICON_LABEL, SHADOW, \
    DETAIL_LABEL, TREND_UP_COLOR, TREND_DOWN_COLOR, VALUE, COLOR_THEME, TREND

BLACK = (0, 0, 0)

GREEN_THEME = {
    SCREEN_BGR: (154, 164, 139),
    HEADER_FOOTER_BGR: (0, 0, 0),
    LABEL: (154, 164, 139),
    ICON: (0, 0, 0),
    ICON_LABEL: (0, 0, 0),
    VALUE: (0, 0, 0),
    SHADOW: (146, 157, 132),
    DETAIL_LABEL: (126, 137, 112),
    DETAIL_VALUE: (184, 194, 169),
    TREND_UP_COLOR: (0, 160, 0),
    TREND_DOWN_COLOR: (160, 0, 0)
}

GREY_THEME = {
    SCREEN_BGR: (173, 180, 182),
    HEADER_FOOTER_BGR: (0, 0, 0),
    LABEL: (173, 180, 182),
    ICON: (0, 0, 0),
    ICON_LABEL: (0, 0, 0),
    VALUE: (0, 0, 0),
    SHADOW: (167, 172, 175),
    DETAIL_LABEL: (150, 155, 158),
    DETAIL_VALUE: (203, 210, 212),
    TREND_UP_COLOR: (0, 160, 0),
    TREND_DOWN_COLOR: (160, 0, 0)
}

ORANGE_THEME = {
    SCREEN_BGR: (0, 0, 0),
    HEADER_FOOTER_BGR: (80, 30, 30),
    LABEL: (255, 120, 50),
    ICON: (255, 120, 50),
    ICON_LABEL: (255, 120, 50),
    VALUE: (255, 120, 50),
    SHADOW: (35, 10, 10),
    DETAIL_LABEL: (200, 105, 45),
    DETAIL_VALUE: (255, 130, 60),
    TREND_UP_COLOR: (0, 160, 0),
    TREND_DOWN_COLOR: (160, 0, 0)
}

BLUE_THEME = {
    SCREEN_BGR: (0, 0, 0),
    HEADER_FOOTER_BGR: (0, 47, 117),
    LABEL: (180, 210, 255),
    ICON: (180, 210, 255),
    ICON_LABEL: (180, 210, 255),
    VALUE: (180, 210, 255),
    SHADOW: (10, 20, 30),
    DETAIL_LABEL: (140, 150, 194),
    DETAIL_VALUE: (180, 210, 255),
    TREND_UP_COLOR: (0, 160, 0),
    TREND_DOWN_COLOR: (160, 0, 0)
}

COLOR_THEMES = [
    GREEN_THEME,
    ORANGE_THEME,
    GREY_THEME,
    BLUE_THEME
]

LABELS = "labels"
CPU = "cpu"
MEMORY = "memory"
DISKS = "disks"
PEPPY = "peppy"
PEPPY_ICON_NAME = "about"
DISKS_ICON_NAME = "disk"
VALUE = "value"
UNIT = "unit"
DETAILS = "details"
TOTAL = "total"
USED = "used"
FREE = "free"
THREADS = "threads"

DIVIDER_GB = 1024.0 ** 3
FORMATTER = "{:.1f}"

class MonitorUtil(object):
    """ Monitor utility class """

    def __init__(self, util):
        """ Initializer 
        
        :param util: utility object
        """
        self.util = util
        self.config = util.config

    def get_dashboard_values(self):
        """ Get dashboard values
        
        :return: dictionary with values
        """
        values = []
        
        values.append(self.get_cpu_values())
        values.append(self.get_memory_values())
        values.append(self.get_disks_values())
        values.append(self.get_peppy_values())

        return values

    def get_cpu_values(self):
        """ Get CPU values
        
        :return: dictionary with values
        """
        cpus = psutil.cpu_percent(interval=1, percpu=True)
        value = sum(cpus)
        details = []
        for i, c in enumerate(cpus):
            details.append((self.config[LABELS][CPU] + str(i), c, "%"))

        return {
            LABEL: self.config[LABELS][CPU],
            ICON_LABEL: self.config[LABELS][TOTAL],
            COLOR_THEME: GREEN_THEME,
            VALUE: value,
            UNIT: "%",
            DETAILS: details,
            TREND: None
        }

    def get_memory_values(self):
        """ Get Memory values
        
        :return: dictionary with values
        """
        memory = psutil.virtual_memory()
        value = memory.percent
        details = []
        
        total_gb = FORMATTER.format(memory.total / DIVIDER_GB)
        used_gb = FORMATTER.format(memory.used / DIVIDER_GB)
        free_gb = FORMATTER.format(memory.free / DIVIDER_GB)

        used_percent = FORMATTER.format((memory.used * 100.0) / memory.total)
        free_percent = FORMATTER.format((memory.free * 100.0) / memory.total)

        details.append((self.config[LABELS][TOTAL], total_gb, "GB"))
        details.append((self.config[LABELS][USED], used_gb, "GB"))
        details.append((self.config[LABELS][FREE], free_gb, "GB"))
        details.append((self.config[LABELS][TOTAL], 100, "%"))
        details.append((self.config[LABELS][USED], used_percent, "%"))
        details.append((self.config[LABELS][FREE], free_percent, "%"))

        return {
            LABEL: self.config[LABELS][MEMORY],
            ICON_LABEL: self.config[LABELS][USED],
            COLOR_THEME: ORANGE_THEME,
            VALUE: value,
            UNIT: "%",
            DETAILS: details,
            TREND: None
        }

    def get_disks_values(self):
        """ Get Disks values
        
        :return: dictionary with values
        """
        disks = psutil.disk_usage('/')
        value = disks.percent
        details = []
        
        total_gb = FORMATTER.format(disks.total / DIVIDER_GB)
        used_gb = FORMATTER.format(disks.used / DIVIDER_GB)
        free_gb = FORMATTER.format(disks.free / DIVIDER_GB)

        used_percent = FORMATTER.format((disks.used * 100.0) / disks.total)
        free_percent = FORMATTER.format((disks.free * 100.0) / disks.total)

        details.append((self.config[LABELS][TOTAL], total_gb, "GB"))
        details.append((self.config[LABELS][USED], used_gb, "GB"))
        details.append((self.config[LABELS][FREE], free_gb, "GB"))
        
        details.append((self.config[LABELS][TOTAL], 100, "%"))
        details.append((self.config[LABELS][USED], used_percent, "%"))
        details.append((self.config[LABELS][FREE], free_percent, "%"))

        return {
            LABEL: self.config[LABELS][DISKS],
            ICON_LABEL: self.config[LABELS][USED],
            COLOR_THEME: BLUE_THEME,
            VALUE: value,
            UNIT: "%",
            DETAILS: details,
            TREND: None
        }

    def get_peppy_values(self):
        """ Get Peppy values
        
        :return: dictionary with values
        """
        pid = os.getpid()
        peppy = psutil.Process(pid)
        peppy.cpu_percent(interval=1.0)
        value = peppy.cpu_percent(interval=1.0)
        details = []

        details.append((self.config[LABELS][MEMORY], FORMATTER.format(peppy.memory_percent()), "%"))
        details.append((self.config[LABELS][THREADS], peppy.num_threads(), ""))

        return {
            LABEL: self.config[LABELS][PEPPY],
            ICON_LABEL: self.config[LABELS][CPU],
            COLOR_THEME: GREY_THEME,
            VALUE: value,
            UNIT: "%",
            DETAILS: details,
            TREND: None 
        }
