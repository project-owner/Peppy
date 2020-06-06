# Copyright 2016-2020 Peppy Player peppy.player@gmail.com
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

class GridLayout(object):
    """ Create bounding boxes for placing components in a grid """

    def __init__(self, bb):
        """ Initializer

        :param bb: bounding box for the whole component
        """
        self.x, self.y = bb.x, bb.y
        self.width, self.height = bb.width, bb.height
        self.constraints = []
        self.current_constraints = 0

    def get_next_constraints(self):
        """ Return bounding box for the next layout component

        :return: next bounding box
        """
        const = self.constraints[self.current_constraints]
        if self.current_constraints + 1 < len(self.constraints):
            self.current_constraints += 1
        else:
            self.current_constraints = 0
        return const

    def set_pixel_constraints(self, rows, cols, gap_x=0, gap_y=0):
        """ Prepare the list of bounding boxes according to the provided parameters

        :param rows: number of rows in the grid
        :param cols: number of columns in the grid
        :param gap_x: horizontal gap between components
        :param gap_y: vertical gap between components
        """
        x_gaps = (cols + 1) * gap_x
        y_gaps = (rows + 1) * gap_y

        if y_gaps > 2:
            self.height += 1

        grid_width = int((self.width - x_gaps) / cols)
        grid_height = int((self.height - y_gaps) / rows)

        leftover_x = self.width - (grid_width * cols) - x_gaps
        leftover_y = self.height - (grid_height * rows) - y_gaps
        reminder_y = leftover_y

        for num_y in range(rows):
            x = 0

            if reminder_y > 0:
                y = self.y + gap_y + (num_y * (grid_height + gap_y + 1))
                h = grid_height + 1
                reminder_y -= 1
            else:
                if reminder_y == 0:
                    if leftover_y:
                        y = y + grid_height + gap_y + 1
                        reminder_y -= 1
                    else:
                        y = self.y + gap_y + (num_y * (grid_height + gap_y))
                else:
                    y = y + grid_height + gap_y
                h = grid_height

            reminder_x = leftover_x

            for num_x in range(cols):
                if reminder_x > 0:
                    x = self.x + gap_x + (num_x * (grid_width + gap_x + 1))
                    w = grid_width + 1
                    reminder_x -= 1
                else:
                    if reminder_x == 0:
                        if leftover_x:
                            x = x + grid_width + gap_x + 1
                            reminder_x -= 1
                        else:
                            x = self.x + gap_x + (num_x * (grid_width + gap_x))
                    else:
                        x = x + grid_width + gap_x
                    w = grid_width

                self.constraints.append(pygame.Rect(x, y, w, h))
