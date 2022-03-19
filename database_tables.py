import sqlite3
import datetime
import database_utils as utils
from database_utils import DATABASE_NAME


def init():
    """
    Creates a new db with the name from the dotenv file.

    :return:
    """

    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    try:
        c.execute(
            '''CREATE TABLE existing_videos (
                id text PRIMARY KEY, upload_date text, existing_playlist_id text,
                created_playlist_id text, playlist_order text, processed bool, skipped bool)''')
    except sqlite3.OperationalError as err:
        print(err)

    try:
        c.execute('''CREATE TABLE existing_playlists (id text PRIMARY KEY, date text)''')
    except sqlite3.OperationalError as err:
        print(err)

    try:
        c.execute('''CREATE TABLE created_playlists (id text PRIMARY KEY, start_date text, end_date text)''')
    except sqlite3.OperationalError as err:
        print(err)

    conn.commit()
    conn.close()


def backup():
    """
    Creates a backup of the current database listed in the dotenv file.

    :return:
    """
    date = datetime.datetime.now().strftime("%Y%m%d")

    con = sqlite3.connect(DATABASE_NAME)
    bck = sqlite3.connect(date + '-' + DATABASE_NAME)
    with bck:
        con.backup(bck)
    bck.close()
    con.close()


def drop_database():
    """
    Drops the existing tables out of the database listed in the dotenv.

    :return:
    """

    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS existing_videos''')
    c.execute('''DROP TABLE IF EXISTS existing_playlists''')
    c.execute('''DROP TABLE IF EXISTS created_playlists''')
    conn.commit()
    conn.close()


def clear_existing_videos_table():
    """
    Clears all data from the videos table.

    :return:
    """

    utils.execute('''DELETE FROM existing_videos''')


def clear_existing_playlist_table():
    """
    Clears all data from the existing playlist table.

    :return:
    """

    utils.execute('''DELETE FROM existing_playlists''')


def clear_created_playlist_table():
    """
    Clears all data from the created playlist table.

    :return:
    """

    utils.execute('''DELETE FROM created_playlists''')
