import sqlite3
import datetime
from database_utils import DATABASE_NAME


def init():
    """
    Creates a new db with the name from the dotenv file
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    try:
        c.execute(
            '''CREATE TABLE existing_videos (
                id text, upload_date text, existing_playlist_id text, 
                created_playlist_id text, playlist_order text, processed bool)''')
    except sqlite3.OperationalError as err:
        print(err)

    try:
        c.execute('''CREATE TABLE existing_playlists (id text, date text)''')
    except sqlite3.OperationalError as err:
        print(err)

    try:
        c.execute('''CREATE TABLE created_playlists (id text, start_date text, end_date text)''')
    except sqlite3.OperationalError as err:
        print(err)

    conn.commit()
    conn.close()


def backup():
    """
    Creates a backup of the current database listed in the dotenv file
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
    Drops the existing tables out of the database listed in the dotenv
    """

    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS existing_videos''')
    c.execute('''DROP TABLE IF EXISTS existing_playlists''')
    c.execute('''DROP TABLE IF EXISTS created_playlists''')
    conn.commit()
    conn.close()
