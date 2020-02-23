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

import os
import sys
import sqlite3
import logging

from util.collector import DbUtil, FILENAME, TITLE, FOLDER
from util.keys import KEY_ABC, KEY_SEARCH

class Selector(object):
    """ Collection of the SQL select statements and helper functions """

    def __init__(self, dbutil=None):
        """ Initializer

        :param dbutil: DB utility class (if any)
        """
        if dbutil:
            self.dbutil = dbutil
        else:
            self.dbutil = DbUtil()

    def get_sign(self, next):
        """ Get comparison sign

        :param next: next page parameter

        :return: > for next < for previous
        """
        if next: return ">"
        else: return "<"

    def get_count(self, result, page_size):
        """ Get page count

        :param result: result set
        :param page_size: page size

        :return: number of pages
        """
        n = 0
        if result:
            m = int(result[0][0])
            n = int(m / page_size)
            if m % page_size != 0:
                n += 1
        return n

    def get_list(self, r, single=True):
        """ Get list of values from provided result set

        :param r: result set
        :param single: True - return list of single objects, False - return list of tuples

        :return: list of values
        """
        result = []
        if r:
            for n in r:
                if single:
                    result.append(n[0])
                else:
                    result.append((n[0], n[1]))
        return result

    def get_offset(self, page, next, page_size):
        """ Get offset clause

        :param page: page number
        :param next: next or previous page
        :param page_size: page size

        :return: empty string for next, OFFSET clause for previous
        """
        if next:
            return ""
        else:
            return "OFFSET " + str((page - 1) * page_size)

    def get_topic_page(self, mode, topic, search_str, current_page, previous_page, first, last, page_size):
        """ Dispatching function to get topic page

        :param mode: mode
        :param topic: collection topic
        :param search_str: search string (if any)
        :param current_page: current topic page number
        :param previous_page: previous topic page number
        :param first: first item in previous select
        :param last: last item in previous select
        :param page_size: page size

        :return: list of items for topic page
        """
        if mode == KEY_ABC:
            return self.get_abc_page(topic, search_str, current_page, previous_page, first, last, page_size=page_size)
        elif mode == KEY_SEARCH:
            return self.get_search_page(topic, search_str, current_page, previous_page, first, last, page_size=page_size)
        else:
            return self.get_list_page(topic, search_str, current_page, previous_page, first, last, page_size=page_size)

    def get_list_page(self, topic, search_str, current_page, previous_page, first, last, page_size):
        """ Get the list of items for the topic page

        :param topic: collection topic
        :param search_str: search string (if any)
        :param current_page: current topic page number
        :param previous_page: previous topic page number
        :param first: first item in previous select
        :param last: last item in previous select
        :param page_size: page size

        :return: list of items for topic page
        """
        if current_page == previous_page:
            return self.get_page(topic, page_size)
        elif current_page > previous_page:
            return self.get_page(topic, page_size, last, None, True)
        elif current_page < previous_page:
            return self.get_page(topic, page_size, first, current_page, False)

    def get_abc_page(self, topic, search_str, current_page, previous_page, first, last, page_size=10):
        """ Get the list of items for the topic page with alphabetical search

        :param topic: collection topic
        :param search_str: search string (if any)
        :param current_page: current topic page number
        :param previous_page: previous topic page number
        :param first: first item in previous select
        :param last: last item in previous select
        :param page_size: page size

        :return: list of items for topic page
        """
        if current_page == previous_page:
            return self.get_page_by_char(topic, search_str, page_size=page_size)
        elif current_page > previous_page:
            return self.get_page_by_char(topic, search_str, last, None, True, page_size=page_size)
        elif current_page < previous_page:
            return self.get_page_by_char(topic, search_str, first, current_page, False, page_size=page_size)

    def get_search_page(self, topic, search_str, current_page, previous_page, first, last, page_size):
        """ Get the list of items for the topic page with keyboard search

        :param topic: collection topic
        :param search_str: search string (if any)
        :param current_page: current topic page number
        :param previous_page: previous topic page number
        :param first: first item in previous select
        :param last: last item in previous select
        :param page_size: page size

        :return: list of items for topic page
        """
        if current_page == previous_page:
            return self.get_page_by_pattern(topic, search_str, page_size=page_size)
        elif current_page > previous_page:
            return self.get_page_by_pattern(topic, search_str, last, True, page_size=page_size)
        elif current_page < previous_page:
            return self.get_page_by_pattern(topic, search_str, first, current_page, False, page_size=page_size)

    def get_page_count(self, column, page_size):
        """ Get page count

        :param column: column name
        :param page_size: page size

        :return: page count
        """
        query = f"""
            SELECT COUNT(DISTINCT {column})
            FROM {self.dbutil.table_name}
            WHERE LENGTH({column}) > 0
        """
        return self.get_count(self.dbutil.run_parameterized_query(query, ()), page_size)

    def get_page(self, column, page_size, value="", page=None, next=True):
        """ Get values for the current page

        :param column: column name
        :param page_size: page size
        :param value: first or last value in the current page
        :param page: page number
        :param next: True - next page, False - previous page

        :return: list of values
        """
        query = f"""
            SELECT DISTINCT {column}
            FROM {self.dbutil.table_name} 
            WHERE LENGTH({column}) > 0 AND 
            {column} {self.get_sign(next)} ?
            ORDER BY {column} ASC 
            LIMIT {page_size} {self.get_offset(page, next, page_size)}
        """
        g = self.get_list(self.dbutil.run_parameterized_query(query, (value,)))
        return g

    def get_page_count_by_char(self, column, ch, page_size):
        """ Get page count filtered by the first character

        :param column: column name
        :param ch: character
        :param page_size: page size

        :return: page count
        """
        query = f"""
            SELECT COUNT(DISTINCT {column})
            FROM {self.dbutil.table_name} 
            WHERE LENGTH(TRIM({column})) > 2 AND 
            LOWER(TRIM({column})) like ?
            ORDER BY {column} ASC
        """
        return self.get_count(self.dbutil.run_parameterized_query(query, (ch.lower() + "%",)), page_size)

    def get_page_by_char(self, column, ch, value="", page=None, next=True, page_size=10):
        """ Get values for the page filtered by the first character

        :param column: column name
        :param ch: character
        :param value: first or last value in the current page
        :param page: page number
        :param next: True - next page, False - previous page
        :param page_size: page size

        :return: list of values
        """
        query = f"""
            SELECT DISTINCT {column}
            FROM {self.dbutil.table_name} 
            WHERE LENGTH(TRIM({column})) > 2 AND 
            LOWER(TRIM({column})) like ? AND 
            {column} {self.get_sign(next)} ?
            ORDER BY {column} ASC 
            LIMIT {page_size} {self.get_offset(page, next, page_size)}
        """
        return self.get_list(self.dbutil.run_parameterized_query(query, (ch.lower() + "%", value)))

    def get_page_count_by_pattern(self, column, pattern, page_size):
        """ Get page count filtered by the search pattern

        :param column: column name
        :param pattern: search string
        :param page_size: page size

        :return: page count
        """
        query = f"""
            SELECT COUNT(DISTINCT {column})
            FROM {self.dbutil.table_name} 
            WHERE LENGTH(LOWER(TRIM({column}))) > 0 AND 
            LOWER(TRIM({column})) like ?
            ORDER BY {column} ASC
        """
        return self.get_count(self.dbutil.run_parameterized_query(query, ("%" + pattern.lower() + "%",)), page_size)

    def get_page_by_pattern(self, column, pattern, value="", page=None, next=True, page_size=10):
        """ Get values for the page filtered by the string pattern

        :param column: column name
        :param pattern: serach pattern
        :param value: first or last value in the current page
        :param page: page number
        :param next: True - next page, False - previous page
        :param page_size: page size

        :return: list of values
        """
        query = f"""
            SELECT DISTINCT {column}
            FROM {self.dbutil.table_name} 
            WHERE LENGTH(TRIM({column})) > 2 AND 
            LOWER(TRIM({column})) like ? AND 
            {column} {self.get_sign(next)} ?
            ORDER BY {column} ASC 
            LIMIT {page_size} {self.get_offset(page, next, page_size)}
        """
        return self.get_list(self.dbutil.run_parameterized_query(query, ("%" + pattern + "%", value)))

    def get_topic_detail_page(self, topic, selection, current_page, prev_page, first, last, page_size):
        """ Get topic details

        :param topic: collection topic
        :param selection: search string
        :param current_page: current page number
        :param prev_page: previous page number
        :param first: first item in previous select
        :param last: last item in previous select
        :param page_size: page size

        :return: list of items for topic page
        """
        if current_page == prev_page:
            return self.get_page_by_column(topic, selection, page_size=page_size)
        elif current_page > prev_page:
            return self.get_page_by_column(topic, selection, last, None, next=True, page_size=page_size)
        elif current_page < prev_page:
            return self.get_page_by_column(topic, selection, first, current_page, next=False, page_size=page_size)

    def get_page_count_by_column(self, topic, param, page_size):
        """ Get page count filtered by the column

        :param topic: collection topic
        :param param: selection parameter
        :param page_size: page size

        :return: page count
        """
        query = f"""
            SELECT COUNT(DISTINCT folder)
            FROM {self.dbutil.table_name}
            WHERE {topic} = ?
        """
        return self.get_count(self.dbutil.run_parameterized_query(query, (param,)), page_size)

    def get_page_by_column(self, topic, param, value='', page=None, next=True, page_size=10):
        """ Get values for the page filtered by the colum

        :param topic: collection topic
        :param param: selection parameter
        :param value: first or last value in the current page
        :param page: page number
        :param next: True - next page, False - previous page
        :param page_size: page size

        :return: list of values
        """
        query = f"""
            SELECT DISTINCT folder
            FROM {self.dbutil.table_name}
            WHERE {topic} = ?
            AND folder {self.get_sign(next)} ?
            ORDER BY folder ASC 
            LIMIT {page_size} {self.get_offset(page, next, page_size)}
        """
        return self.get_list(self.dbutil.run_parameterized_query(query, (param, value)), True)

    def get_filename_by_title(self, folder, title):
        """ Get filename by title

        :param folder: folder name
        :param title: track title

        :return: track filename
        """
        query = f"""
            SELECT DISTINCT filename
            FROM {self.dbutil.table_name}
            WHERE folder = ?
            AND title = ?
            ORDER BY filename ASC LIMIT 1
        """
        r = self.get_list(self.dbutil.run_parameterized_query(query, (folder, title)), True)
        if r:
            return r[0]
        else:
            return None
