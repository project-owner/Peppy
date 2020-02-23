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
import logging
import sqlite3
import time

from timeit import default_timer as timer
from datetime import timedelta
from mutagen import File

# DB Util constants

DEFAULT_TABLE_NAME = "metadata"
DEFAULT_SUMMARY_TABLE_NAME = "summary"
FOLDER = "folder"
FILENAME = "filename"
TYPE = "type"
GENRE = "genre"
ALBUM = "album"
COMPOSER = "composer"
ARTIST = "artist"
PERFORMER = "performer"
TITLE = "title"
DATE = "date"
BASEFOLDER = "basefolder"
ORIGINOS = "originos"
EXTENSIONS = (".aac", ".ac3", ".aiff", ".ape", ".flac", ".m4a", ".mp3", ".ogg", ".opus", ".wav", ".wma", ".wv")
METADATA = [GENRE, ALBUM, COMPOSER, ARTIST, PERFORMER, TITLE, DATE]
INFO = ["sample_rate", "channels", "bits_per_sample", "length", "bitrate"]
ALL_METADATA = [FOLDER, FILENAME, TYPE]
ALL_METADATA.extend(METADATA + INFO)
SUMMARY = [BASEFOLDER, ORIGINOS, GENRE, ARTIST, COMPOSER, ALBUM, TITLE, DATE, TYPE, FOLDER, FILENAME]

# Collector constants

SCANNED_FOLDERS = "Scanned folders: "
TIME_TO_PARSE = "time_to_parse"
SCAN_TIME = "Scan time (h:mm:ss): "
PARSING_TIME = "Parsing time (h:mm:ss): "
ESTIMATED_TIME = "Estimated metadata parse time (h:mm:ss): "
ESTIMATED_DISK_SPACE = "Estimated disk space for metadata database (bytes): "
FILES = "files"
TOTAL_TRACKS = "total tracks"
TOTAL_FILES = "Total audio files: "
FILES_STATISTICS = "Files Statistics"
METADATA_STATISTICS = "Metadata Statistics"
DATABASE_STATISTICS = "Database Statistics"
ERRORS = "Errors: "
AVERAGE_PARSE_TIME = 0.016
AVERAGE_METADATA_SIZE = 278
EMPTY_COLLECTION_SIZE = 8192
STARS = 60
PROGRESS_BAR_PREFIX = "Progress:"
PROGRESS_BAR_SUFFIX = "Complete"
PROGRESS_BAR_LENGTH = 50
BATCH_SIZE = 300
FILE_BATCH_SIZE = 50
FULL_BLOCK_CHARACTER = chr(9608)

class DbUtil(object):
    """ Database utility class. Keeps the connection to the database and provides utility SQL functions. """

    def __init__(self, db_filename=None):
        """ Initializer.

        :param db_filename: folder and filename of the database file
        """
        self.db_path = db_filename
        self.table_name = DEFAULT_TABLE_NAME
        self.summary_table_name = DEFAULT_SUMMARY_TABLE_NAME
        self.metadata_keys = METADATA
        self.info_keys = INFO

        csv = ",".join([m + " text" for m in ALL_METADATA])
        self.CREATE_METADATA_TABLE = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (id integer PRIMARY KEY,{csv});"""

        csv = ",".join([m + " text" for m in SUMMARY])
        self.CREATE_SUMMARY_TABLE = f"""CREATE TABLE IF NOT EXISTS {self.summary_table_name} ({csv});"""

        csv = ",".join([m for m in ALL_METADATA])
        values = ",".join(["?" for _ in ALL_METADATA])
        self.INSERT_DATA = f"""INSERT INTO {self.table_name}({csv}) VALUES({values});"""

        csv = ",".join([m for m in SUMMARY])
        values = ",".join(["?" for _ in SUMMARY])
        self.INSERT_SUMMARY_DATA = f"""INSERT INTO {self.summary_table_name}({csv}) VALUES({values});"""

        self.conn = None

    def is_db_file_available(self):
        """ Check that the database file exists

        :return: True - exists, False - doesn't exist
        """
        if not self.db_path or not os.path.isfile(self.db_path):
            logging.debug(f"""Collection database {self.db_path} not found""")
            return False
        else:
            logging.debug(f"""Collection database {self.db_path} exists""")
            return True

    def is_metadata_available(self):
        """ Check if metadata table exists

        :return: True - table exists, False - table doesn't exist
        """
        query = f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}';"""
        if self.run_query(query):
            return True
        else:
            return False

    def connect(self):
        """ Connect to the collection database """

        try:
            self.conn = sqlite3.connect(self.db_path)
            logging.debug(f"""Connected to the collection database {self.db_path}""")
            if not self.is_metadata_available():
                logging.debug("Collection tables don't exist")
                self.run_command(self.CREATE_METADATA_TABLE)
                self.run_command(self.CREATE_SUMMARY_TABLE)
                logging.debug("Created collection tables")
        except Exception as e:
            logging.debug(e)

    def disconnect(self):
        """ Disconnect from the collection database """

        if self.conn:
            self.conn.close()

    def run_command(self, command, values=None):
        """ Run single SQL command in transaction. Rollback if exception.

        :param command: SQL command
        :param values: input values
        """
        try:
            self.conn.execute("begin")
            if values:
                self.conn.execute(command, values)
            else:
                self.conn.execute(command)
            self.conn.commit()
        except Exception as e:
            self.conn.execute("rollback")
            logging.debug(e)

    def run_batch_insert(self, params):
        """ Run multiple INSERT commands in transaction. Rollback if exception.

        :param params: list of values for multiple inserts
        """
        try:
            self.conn.execute("begin")
            self.conn.executemany(self.INSERT_DATA, params)
            self.conn.commit()
        except Exception as e:
            self.conn.execute("rollback")
            logging.debug(e)

    def run_query(self, query):
        """ Run SELECT query

        :param query: SQL query

        :return: param set
        """
        if not self.conn:
            logging.debug(f"""No connection to the database: {self.db_path}""")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            logging.debug(e)
            logging.debug(query)
            return None

    def run_parameterized_query(self, query, params):
        """ Run SELECT query

        :param query: SQL query
        :param params: query parameters

        :return: param set
        """
        if not self.conn:
            logging.debug(f"""No connection to the database: {self.db_path}""")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Exception as e:
            logging.debug(e)
            logging.debug(query)
            return None

    def get_collection_summary(self):
        """ Get collection summary from the SUMMARY table

        :return: dictionary with summary
        """
        if not self.is_db_file_available():
            return

        s = self.run_query(f"""
            SELECT *
            FROM {self.summary_table_name}
        """)

        if not s:
            logging.debug("Collection summary not found")
            return None

        summary = {
            BASEFOLDER: s[0][0],
            ORIGINOS: s[0][1],
            GENRE: s[0][2],
            ARTIST: s[0][3],
            COMPOSER: s[0][4],
            ALBUM: s[0][5],
            TITLE: s[0][6],
            DATE: s[0][7],
            TYPE: s[0][8],
            FOLDER: s[0][9],
            FILENAME: s[0][10]
        }
        return summary

    def purge_collection_tables(self):
        """ Delete collection tables """

        command = f"""DROP TABLE IF EXISTS {self.table_name}"""
        self.run_command(command)
        command = f"""DROP TABLE IF EXISTS {self.summary_table_name}"""
        self.run_command(command)
        self.run_command(self.CREATE_METADATA_TABLE)
        self.run_command(self.CREATE_SUMMARY_TABLE)
        logging.debug("Collection deleted")

class Collector(object):
    """ Collects audio files metadata and inserts into the database. Reports statistics. """

    def __init__(self, dbfile=None, dbutil=None):
        """ Initializer

        :param dbfile: database filename
        :param dbutil: database utility class. Provided if class is used in the player.
        """
        if dbutil:
            self.dbutil = dbutil
        else:
            self.dbutil = DbUtil(db_filename=dbfile)

    def get_files_statistics(self, base_folder, total_folders, progress_callback=None):
        """ Collect recursively statistics about all audio files in the specified folder and its subfolders.
        This function doesn't parse files and doesn't create collection database.

        :param base_folder: base folder
        :param total_folders: total number of all subfolders
        :param progress_callback: callback function to send progress to

        :return: dictionary with statistics
        """
        stats = {}
        found_audio_files = {}
        scanned_folders = 0
        total_files = 0

        logging.debug(f"""Collecting statistics for files in folder {base_folder}""")

        start = timer()

        for _, __, files in os.walk(base_folder, followlinks=True):
            scanned_folders += 1
            for file in files:
                if not file.lower().endswith(EXTENSIONS):
                    continue
                ext = file[file.rfind('.') + 1:].lower()
                total_files += 1
                if ext in found_audio_files.keys():
                    found_audio_files[ext] = found_audio_files[ext] + 1
                else:
                    found_audio_files[ext] = 1
            if progress_callback:
                progress_callback(scanned_folders, total_folders)

        end = timer()

        stats[SCAN_TIME] = timedelta(seconds=(end - start))
        stats[FILES] = found_audio_files
        stats[SCANNED_FOLDERS] = scanned_folders
        stats[TOTAL_FILES] = total_files
        stats[TIME_TO_PARSE] = AVERAGE_PARSE_TIME

        logging.debug("Finished collecting statistics")

        return stats

    def get_database_statistics(self):
        """ Count all unique values for each metadata column.

        :return: dictionary with DB stats for each metadata column
        """
        if not self.dbutil.is_db_file_available():
            return

        total_tracks = self.dbutil.run_query(f"""
            SELECT COUNT(*)
            FROM {self.dbutil.table_name}
        """)

        if total_tracks == None:
            return None

        collection_stats = {TOTAL_TRACKS: total_tracks[0][0]}

        for c in SUMMARY[2:]:
            r = self.dbutil.run_query(f"""
                SELECT COUNT(DISTINCT {c})
                FROM {self.dbutil.table_name}
                WHERE LENGTH(TRIM({c})) > 0""")
            if r:
                collection_stats[c] = r[0][0]

        return collection_stats

    def get_file_metadata(self, folder, filename, ext, meta):
        """ Prepare audio file metadata

        :param folder: file folder
        :param filename: file name
        :param ext: file extension
        :param meta: file metadata from mutagen

        :return: file metadata list of values for insert
        """
        metadata = []

        metadata.append(folder)
        metadata.append(filename)
        metadata.append(ext)

        if meta == None:
            for _ in range(len(ALL_METADATA) - len(metadata)):
                metadata.append(None)
            return metadata

        for key in METADATA:
            if meta and (key not in meta.keys() or len(meta[key][0].replace(" ", "").strip()) == 0):
                v = None
            else:
                v = meta[key][0].strip()

            metadata.append(v)

        if hasattr(meta, "info"):
            for key in INFO:
                metadata.append(getattr(meta.info, key, None))
        else:
            for _ in INFO:
                metadata.append(None)

        return metadata

    def collect_metadata(self, base_folder, total_folders, metadata_callback=None, progress_callback=None):
        """ Collect audio file metadata

        :param base_folder: base folder
        :param base_folder: total number of subfolders
        :param metadata_callback: callback for reporting progress, called when BATCH_SIZE reached
        :param progress_callback: callback for reporting progress, called for each new folder

        :return: dictionary with statistics
        """
        metadata = []
        errors = []
        num = 0
        total_files = 0
        scanned_folders = 0
        start = timer()

        if not base_folder:
            base_folder = os.getcwd()
        elif base_folder and not os.path.isdir(base_folder):
            logging.debug(f"""Folder {base_folder} not found""")
            return

        for current_folder, _, files in os.walk(base_folder, followlinks=True):
            scanned_folders += 1
            for file in files:
                if not file.lower().endswith(EXTENSIONS):
                    continue

                ext = file[file.rfind('.') + 1:]
                ext = ext.lower()
                meta = None
                try:
                    meta = File(os.path.join(current_folder, file), easy=True)
                except Exception as e:
                    msg = f"""Metadata parsing error in file {file}: {e}"""
                    errors.append(msg)

                meta_folder = current_folder[len(base_folder):]
                if meta:
                    m = self.get_file_metadata(meta_folder, file, ext, meta)
                    metadata.append(m)
                else:
                    metadata.append(self.get_file_metadata(meta_folder, file, ext, None))

                num += 1
                total_files += 1

                if num == BATCH_SIZE:
                    if metadata_callback:
                        metadata_callback(metadata)
                    metadata = []
                    num = 0

            if progress_callback:
                progress_callback(scanned_folders, total_folders)

        end = timer()

        if metadata_callback and metadata:
            metadata_callback(metadata)

        stats = {
            SCANNED_FOLDERS: scanned_folders,
            TOTAL_FILES: total_files,
            PARSING_TIME: timedelta(seconds=(end - start)),
            ERRORS: errors
        }

        return stats

    def create_collection(self, base_folder, total_folders, db_filename, progress_callback=None):
        """ Create the database collection with audio files metadata

        :param base_folder: collection base folder
        :param total_folders: total number of the subfolders in the base folder
        :param db_filename: collection database filename
        :param progress_callback: callback for reporting progress

        :return: dictionary with collection database statistics
        """
        if base_folder and not os.path.isdir(base_folder):
            logging.debug(f"""Folder {base_folder} not found""")
            return None

        self.dbutil.db_path = db_filename
        self.dbutil.connect()

        logging.debug("Creating collection")
        stats = self.collect_metadata(base_folder, total_folders, self.dbutil.run_batch_insert, progress_callback)
        logging.debug("Collection created")
        logging.debug("Creating summary...")
        summary = self.get_database_statistics()
        values = [
            base_folder,
            sys.platform,
            str(summary[GENRE]),
            str(summary[ARTIST]),
            str(summary[COMPOSER]),
            str(summary[ALBUM]),
            str(summary[TITLE]),
            str(summary[DATE]),
            str(summary[TYPE]),
            str(summary[FOLDER]),
            str(summary[FILENAME])
        ]
        self.dbutil.run_command(self.dbutil.INSERT_SUMMARY_DATA, values)
        logging.debug("Summary created")
        logging.debug("Creation process completed")
        return stats

    def print_files_statistics(self, stats):
        """ Prepare formatted string with folder statistics

        :param stats: folder statistics dictionary
        """
        if not stats:
            return

        n = int((60 - 2 - len(FILES_STATISTICS)) / 2)
        s = "\n\n" + "*" * n + " " + FILES_STATISTICS + " " + "*" * n
        scanned_folders = stats[SCANNED_FOLDERS]
        s += f"""\n\n{SCANNED_FOLDERS} {scanned_folders}"""
        s += f"""\n{TOTAL_FILES} {stats[TOTAL_FILES]}"""
        s += f"""\n{SCAN_TIME} {stats[SCAN_TIME]}"""
        parse_time = timedelta(
            seconds=(stats[TIME_TO_PARSE] * stats[TOTAL_FILES]))
        disk_space = str(EMPTY_COLLECTION_SIZE +
                         (stats[TOTAL_FILES] * AVERAGE_METADATA_SIZE))
        s += f"""\n{ESTIMATED_TIME}{parse_time}"""
        s += f"""\n{ESTIMATED_DISK_SPACE}{disk_space}\n\n"""
        files = stats[FILES]
        for k in files.keys():
            ext = k.upper()
            num = files[k]
            r = f"""{ext}: \t {num}\n"""
            s += r

        s += "\n" + "*" * STARS
        
        logging.debug(s)

    def print_metadata_statistics(self, stats):
        """ Prepare formatted string with metadata statistics

        :param stats: metadata statistics dictionary
        """
        if not stats:
            return

        n = int((STARS - 2 - len(METADATA_STATISTICS)) / 2)
        s = "\n\n" + "*" * n + " " + METADATA_STATISTICS + " " + "*" * n
        s += f"""\n\n{SCANNED_FOLDERS} {stats[SCANNED_FOLDERS]}"""
        s += f"""\n{TOTAL_FILES} {stats[TOTAL_FILES]}"""
        s += f"""\n{PARSING_TIME} {stats[PARSING_TIME]}"""
        s += f"""\n{ERRORS} {len(stats[ERRORS])}\n"""
        if stats[ERRORS]:
            s += f"""{ERRORS}\n"""
            for e in stats[ERRORS]:
                s += f"""{e}\n"""
        s += "\n"
        s += "*" * STARS
        
        logging.debug(s)

    def print_statistics(self, stats, header):
        """ Prepare formatted string

        :param stats: stats dictionary
        :param header: stats header
        """
        if not stats:
            return

        n = int((STARS - 2 - len(header)) / 2)
        s = "\n\n" + "*" * n + " " + header + " " + "*" * n + "\n"
        for k, v in stats.items():
            s += f"""\n{k}: {v}"""
        s += "\n\n"
        s += "*" * STARS

        logging.debug(s)

    def print_progress_bar(self, current_value, total):
        """ Show progress bar
        Modified version of the source which was found here: 
        https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
        
        :param current_value: current value
        :param total: total values
        """
        percents = f"""{100 * (current_value / float(total)):.2f}"""
        filled_length = int(round(PROGRESS_BAR_LENGTH * current_value / float(total)))
        bar = f"""{FULL_BLOCK_CHARACTER * filled_length}{"-" * (PROGRESS_BAR_LENGTH - filled_length)}"""
        print(f"""\r{PROGRESS_BAR_PREFIX} |{bar}| {percents}% {PROGRESS_BAR_SUFFIX}""", end="")

        if current_value == total:
            print()

    def count_folders(self, base_folder=None, print_log=True):
        """ Count all folders in specified base folder

        :param base_folder: base folder
        :param progress_callback: callback function to send progress to

        :return: number of folders
        """
        count = 0
        start = timer()
        
        if not base_folder:
            base_folder = os.getcwd()
        elif base_folder and not os.path.isdir(base_folder):
            logging.debug(f"""Folder {base_folder} not found""")
            return

        logging.debug(f"""Counting folders in {base_folder}""")

        for _ in os.walk(base_folder, followlinks=True):
            count += 1
            if print_log and count % FILE_BATCH_SIZE == 0:
                print("*", end="", flush=True)

        if print_log:
            print()
        end = timer()
        elapsed_time = timedelta(seconds=(end - start))
        logging.debug(f"""Found {count} folders""")
        logging.debug(f"""Time spent (h:mm:ss): {elapsed_time}""")
        
        return (count, elapsed_time)

def main():
    import argparse
    log_handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(
        level=logging.NOTSET,
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=[log_handler]
    )
    usage = """python collector.py <command> [args]"""
    examples = """Examples (Windows):
    python collector.py -h\t\t\t show this help
    python collector.py files -h\t\t show help for specific command

    python collector.py files -i c:\\music\t show statistics for files in specific folder
    python collector.py db -i c:\\peppy.db\t show statistics for specific database file
    python collector.py create -i c:\\music -o c:\peppy.db
        create collection database using specified folder and database filename
    """
    parser = argparse.ArgumentParser(
        usage=usage,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples
    )
    subparsers = parser.add_subparsers(dest="command")
    
    p = subparsers.add_parser("files", help="show files statistics")
    p.add_argument("-i", help="audio files root folder", required=True)

    p = subparsers.add_parser("db", help="show collection database statistics")
    p.add_argument("-i", help="collection database file name", required=True)

    p = subparsers.add_parser("create", help="create collection database")
    p.add_argument("-i", help="audio files root folder", required=True)
    p.add_argument("-o", help="collection database filename", required=True)

    try:
        args = parser.parse_args()
    except Exception as e:
        logging.debug(e)
        sys.exit(1)

    command = args.command

    if command == "files":
        coll = Collector()
        base_folder = args.i
        n = coll.count_folders(base_folder)
        if n:
            stats = coll.get_files_statistics(base_folder, n[0], coll.print_progress_bar)
            coll.print_files_statistics(stats)
    elif command == "db":
        if args.i and not os.path.isfile(args.i):
            logging.debug(f"""Collection database file {args.i} not found""")
            sys.exit(1)

        coll = Collector(args.i)
        coll.dbutil.connect()
        stats = coll.dbutil.get_collection_summary()
        coll.print_statistics(stats, DATABASE_STATISTICS)
    elif command == "create":        
        base_folder = args.i
        db_filename = args.o

        if db_filename and os.path.isfile(db_filename):
            logging.debug(f"""Collection database file {db_filename} exists already""")
            sys.exit(1)

        coll = Collector(db_filename)
        coll.dbutil.connect()
        n = coll.count_folders(base_folder)
        if n:
            stats = coll.create_collection(base_folder, n[0], db_filename, coll.print_progress_bar)
            coll.print_metadata_statistics(stats)
        
if __name__ == '__main__':
    main()
