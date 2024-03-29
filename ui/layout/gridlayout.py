# Copyright 2016-2022 Peppy Player peppy.player@gmail.com
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

    def __init__(self, bb, horizontal=True, column_weights=None):
        """ Initializer

        :param bb: bounding box for the whole component
        :param horizontal: True - horizontal layout, False - vertical layout
        :param column_weights: list of column weights, 100 is total weight of all columns
        """
        self.x, self.y = bb.x, bb.y
        self.width, self.height = bb.width, bb.height
        self.horizontal = horizontal
        self.constraints = []
        self.current_constraints = 0
        self.row_cells = []
        self.col_cells = []
        self.column_weights = column_weights

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
        self.create_row(cols, gap_x)
        self.create_column(rows, gap_y)

        if self.horizontal:
            self.create_horizontal_layout(rows, cols)
        else:
            self.create_vertical_layout(rows, cols)

    def create_row(self, cols, gap_x):
        """ Create one template row

        :param cols: number of columns in the grid
        :param gap_x: horizontal gap between components
        """
        if self.column_weights:
            for num_x in range(cols):
                weight = self.column_weights[num_x]
                grid_width = int((self.width * weight) / 100)

                if num_x == cols - 1:
                    x = self.row_cells[num_x - 1][0] + self.row_cells[num_x - 1][0] - gap_x
                    w = int(self.width - x - gap_x)
                else:
                    x = self.x + gap_x + (num_x * (grid_width + gap_x + 1))
                    w = grid_width + 1
                self.row_cells.append((x, w))
            return

        x_gaps = (cols + 1) * gap_x
        grid_width = int((self.width - x_gaps) / cols)
        leftover_x = self.width - (grid_width * cols) - x_gaps
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

            self.row_cells.append((x, w))

    def create_column(self, rows, gap_y):
        """ Create one template column

        :param rows: number of rows in the grid
        :param gap_y: vertical gap between components
        """
        y_gaps = (rows + 1) * gap_y
        if y_gaps > 2:
            self.height += 1
        grid_height = int((self.height - y_gaps) / rows)
        leftover_y = self.height - (grid_height * rows) - y_gaps
        reminder_y = leftover_y

        for num_y in range(rows):
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

            self.col_cells.append((y, h))

    def create_horizontal_layout(self, rows, cols):
        """ Create cells for the horizontal layout

        :param rows: number of rows in the grid
        :param cols: number of columns in the grid
        """
        for num_y in range(rows):
            y = self.col_cells[num_y][0]
            h = self.col_cells[num_y][1]

            for num_x in range(cols):
                x = self.row_cells[num_x][0]
                w = self.row_cells[num_x][1]

                self.constraints.append(pygame.Rect(x, y, w, h))

    def create_vertical_layout(self, rows, cols):
        """ Create cells for the vertical layout

        :param rows: number of rows in the grid
        :param cols: number of columns in the grid
        """
        for num_x in range(cols):
            x = self.row_cells[num_x][0]
            w = self.row_cells[num_x][1]

            for num_y in range(rows):
                y = self.col_cells[num_y][0]
                h = self.col_cells[num_y][1]

                self.constraints.append(pygame.Rect(x, y, w, h))
