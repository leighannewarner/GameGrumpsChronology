import os
import socket
import sqlite3
import time
import youtube

from dotenv import load_dotenv

load_dotenv()

DATABASE_NAME = 'playlists.db'

# These videos will go in as created instead of chunked together like most playlists
SKIP_PLAYLISTS = {
    'PLC4E9F4F6136EF251',  # GG animated
    'PLRQGRBgN_Enp7Z8-nL2FPZh5XPX5xdBOH',  # Best of
    'PLRQGRBgN_EnrsxaVTQJKIao6lDAJyYOw-',  # Game Grumps VS
    'PLRQGRBgN_EnrjPMktYLDYVwjwK-TXjimo',  # Game Grumps Starter Pack
    'PLRQGRBgN_EnrGIejPUT4H-oHJ0-_9K47A',  # Good Game
    'PLRQGRBgN_Enp8AlpQw7vGS0mEANb7ufIz',  # The G Club [Weekly Podcast]
    'PLRQGRBgN_EnpSqUheSWgweSMOcLdtI9w7',  # Game Grumps 10 Minute Power Hour
    'PLRQGRBgN_EnrCbSE3UselKt4lupjneBjM',  # Game Grumps Compilations
    'PLRQGRBgN_EnpsHKpbrow0ex8bOm8TXWej',  # GRUMPSWAVE Music
    'PLRQGRBgN_EnqizkZXJB4LP-af3Gum7Uhe',  # Commercials!!
    'PLRQGRBgN_EnrxtvIO8iQIuWItwFfkJ3Vk',  # Mario Maker
    'PLRQGRBgN_EnqIWG6TuaGLWmn9NLcaHi7P',  # One Offs
    'PLRQGRBgN_Enq32ulNww6QJxdSp0cygD6m',  # Guest grumps
    'PLRQGRBgN_Enp7jEkUuzG5Z32gLY8-pPJl'  # Weird Bayonetta playlist with only one video that is private
}

youtube_client = None


def main():
    value = input("Delete database y/n:\n")
    if value == 'y':
        drop_database()

    value = input("Create database y/n:\n")
    if value == 'y':
        init_db()

    value = input("Update playlists table y/n:\n")
    if value == 'y':
        populate_existing_playlists_table()

    value = input("Update videos table y/n:\n")
    if value == 'y':
        populate_videos_in_playlists_table()

    value = input("Print playlists y/n:\n")
    if value == 'y':
        print_playlist_table()

    value = input("Print videos y/n:\n")
    if value == 'y':
        print_video_table()


# TABLE MANAGEMENT ####################################################################################################
def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    try:
        c.execute('''CREATE TABLE existing_playlists (id text, date text)''')
    except sqlite3.OperationalError as err:
        print(err)

    try:
        c.execute('''CREATE TABLE videos_in_playlists (id text, playlist_id text)''')
    except sqlite3.OperationalError as err:
        print(err)

    try:
        c.execute('''CREATE TABLE video_queue (id text, playlist_id text, playlist_order text, processed bool)''')
    except sqlite3.OperationalError as err:
        print(err)

    try:
        c.execute('''CREATE TABLE created_playlists (id text, start_date text, end_date text)''')
    except sqlite3.OperationalError as err:
        print(err)

    conn.commit()
    conn.close()


def drop_database():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS existing_playlists''')
    c.execute('''DROP TABLE IF EXISTS videos_in_playlists''')
    c.execute('''DROP TABLE IF EXISTS video_queue''')
    c.execute('''DROP TABLE IF EXISTS created_playlists''')
    conn.commit()
    conn.close()


# CLEAR TABLES ########################################################################################################
def clear_existing_playlist_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DELETE FROM existing_playlists''')
    conn.commit()
    conn.close()


def clear_videos_in_playlists_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DELETE FROM videos_in_playlists''')
    conn.commit()
    conn.close()


def clear_generated_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DELETE FROM video_queue''')
    conn.commit()
    conn.close()


def clear_created_playlist_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DELETE FROM created_playlists''')
    conn.commit()
    conn.close()


# PRINT TABLES ########################################################################################################
def print_playlist_table():
    conn = sqlite3.connect(DATABASE_NAME)
    counter = 0
    for row in conn.execute('''SELECT * FROM existing_playlists'''):
        counter += 1
        print(row)
    conn.close()


def print_video_table():
    conn = sqlite3.connect(DATABASE_NAME)
    for row in conn.execute('''SELECT * FROM videos_in_playlists'''):
        print(row)
    conn.close()


def print_generated_table():
    conn = sqlite3.connect(DATABASE_NAME)
    for row in conn.execute('''SELECT * FROM video_queue'''):
        print(row)
    conn.close()


def print_queue():
    conn = sqlite3.connect(DATABASE_NAME)
    for row in conn.execute('''SELECT * FROM video_queue WHERE processed = ?''', (False,)):
        print(row)
    conn.close()


def print_created_playlist_table():
    conn = sqlite3.connect(DATABASE_NAME)
    for row in conn.execute('''SELECT * FROM created_playlists'''):
        print(row)
    conn.close()


# GET ROWS ############################################################################################################
def get_video_in_playlist(video_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''SELECT * FROM videos_in_playlists WHERE id = ?''', (video_id,))
    row = c.fetchone()
    conn.close()
    return row


def get_existing_playlist(playlist_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''SELECT * FROM existing_playlists WHERE id = ?''', (playlist_id,))
    row = c.fetchone()
    return row


def get_video_queue():
    conn = sqlite3.connect(DATABASE_NAME)
    videos = []
    for row in conn.execute(
            '''SELECT id,playlist_id,playlist_order FROM video_queue WHERE processed = ? ORDER BY playlist_order ASC''',
            (True,)):
        videos.append(row)
    conn.close()
    return videos


def get_video_playlist(playlist_id):
    conn = sqlite3.connect(DATABASE_NAME)
    videos = []
    for row in conn.execute(
            '''SELECT playlist_order,id FROM video_queue WHERE processed = ? AND playlist_id = ?''' +
            '''ORDER BY playlist_order ASC''',
            (True, playlist_id)):
        videos.append(row)
    conn.close()
    return videos


def get_video_from_queue(video_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute(
        '''SELECT * FROM video_queue WHERE id = ?''', (video_id,))
    row = c.fetchone()
    conn.close()
    return row


def get_created_playlist(start_date, end_date):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''SELECT * FROM created_playlists WHERE start_date = ? AND end_date = ?''', (start_date, end_date))
    row = c.fetchone()
    conn.close()
    return row


# GENERATE TABLES ####################################################################################################
def populate_existing_playlists_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    playlists = list_all_playlists_for_channel()
    c.executemany('''INSERT INTO existing_playlists (id) VALUES (?)''', playlists)
    conn.commit()
    conn.close()


def populate_videos_in_playlists_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    video_ids = []
    for row in conn.execute('''SELECT id FROM existing_playlists'''):
        try:
            playlist_id = row[0]
            video_ids.extend(list_all_videos_in_playlist(playlist_id))
        except socket.timeout as err:
            print('')
            print(err)

    c.executemany('''INSERT INTO videos_in_playlists (id, playlist_id) VALUES (:video_id,:playlist_id)''', video_ids)
    c.executemany('''UPDATE existing_playlists SET date = :date WHERE id = :playlist_id''', video_ids)
    conn.commit()
    conn.close()


# UPDATE ROWS #########################################################################################################
def store_created_playlist(playlist_id, start_date, end_date):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO created_playlists (id,start_date,end_date) VALUES (?,?,?)''',
              (playlist_id, start_date, end_date))
    conn.commit()
    conn.close()


def store_videos_to_add(item_list):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.executemany('''INSERT INTO video_queue (id,playlist_id,playlist_order,processed) VALUES (?,?,?,?)''',
                  item_list)
    conn.commit()
    conn.close()


def mark_video_processed(video_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''UPDATE video_queue SET processed = :processed WHERE id = :video_id''',
              {'processed': True, 'video_id': video_id})
    conn.commit()
    conn.close()


def mark_all_videos_unprocessed():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''UPDATE video_queue SET processed = :processed''', {'processed': False})
    conn.commit()
    conn.close()


# API UTILS ###########################################################################################################
def authorize():
    global youtube_client

    if youtube_client is None:
        youtube_client = youtube.get_youtube_client()


def list_all_playlists_for_channel():
    authorize()
    response_items = youtube.list_all_playlists_for_channel(youtube_client, os.getenv('CHANNEL_ID'))

    items = []
    for result in response_items:
        playlist_id = result.get('id')
        if result.get('id') in SKIP_PLAYLISTS:
            continue
        if get_existing_playlist(playlist_id) is None:
            items.append((playlist_id,))
    return items


def list_all_videos_in_playlist(playlist_id):
    print(f'Retrieving videos in {playlist_id}')

    authorize()
    response_items = youtube.list_all_videos_in_playlist(
        youtube_client, playlist_id)

    items = []
    publish_date = None
    for result in response_items:
        publish_date = result.get('contentDetails').get('videoPublishedAt')
        if publish_date is not None:
            break

    for result in response_items:
        video_id = result.get('snippet').get('resourceId').get('videoId')
        if get_video_in_playlist(video_id) is None:
            items.append({'video_id': video_id, 'playlist_id': playlist_id, 'date': publish_date})
    return items


if __name__ == "__main__":
    main()
