import os
import sqlite3
import youtube
import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_NAME = 'playlists.db'

# These videos will go in as created instead of chunked together like most playlists
SKIP_PLAYLISTS = {
    'PLC4E9F4F6136EF251',  # GG animated
    'FL9CuvdOVfMPvKCiwdGKL3cQ',  # Favorites
    'PLRQGRBgN_Enp7Z8-nL2FPZh5XPX5xdBOH',  # Best of
    'PLRQGRBgN_EnrsxaVTQJKIao6lDAJyYOw-',  # Game Grumps VS
    'PLRQGRBgN_EnrjPMktYLDYVwjwK-TXjimo',  # Game Grumps Starter Pack
    'PLRQGRBgN_EnrGIejPUT4H-oHJ0-_9K47A',  # Good Game
    'PLRQGRBgN_Enp8AlpQw7vGS0mEANb7ufIz',  # The G Club [Weekly Podcast]
    'PLRQGRBgN_EnpSqUheSWgweSMOcLdtI9w7',  # Game Grumps 10 Minute Power Hour
    'PLRQGRBgN_EnrCbSE3UselKt4lupjneBjM',  # Game Grumps Compilations
    'PLRQGRBgN_EnpsHKpbrow0ex8bOm8TXWej',  # GRUMPSWAVE Music
    'PLRQGRBgN_EnqizkZXJB4LP-af3Gum7Uhe',  # Commercials!!
    'PLRQGRBgN_EnrxtvIO8iQIuWItwFfkJ3Vk',  # Mario Maker 1
    'PLRQGRBgN_EnqIWG6TuaGLWmn9NLcaHi7P',  # One Offs
    'PLRQGRBgN_Enq32ulNww6QJxdSp0cygD6m',  # Guest grumps
    'PLRQGRBgN_Enp7jEkUuzG5Z32gLY8-pPJl',  # Weird Bayonetta playlist with only one video that is private
    'PLRQGRBgN_EnqUyjIu3IxgrenDPTVOV_wM',  # SteamRolled
    'PLRQGRBgN_EnpND5AJknSiwwP9OKMYx4RP',  # Ghoul Grumps
    'PLRQGRBgN_EnrbKMOysGunwG4vdcmJwK8c',  # Second undertale playlist
    'PLRQGRBgN_Enofh0M71j-c-JFuCM6Fpu7y',  # Livestreams
    'PLRQGRBgN_EnqU1NBgebcb6qP3YfYhmFi5',  # Reaction compilations
    'PLRQGRBgN_EnpvWVnEytLys8wLUHm5NSFh',  # Space Quest (game chronology)
    'PLRQGRBgN_Enq0QqqVJx8LDpNGdxlgEhO3',  # All monopoly series
    'PLRQGRBgN_EnqsgAMZkHdcQswhgYSqsptx',  # Mario party all series, there are a lot of dupe playlists
    'PLRQGRBgN_EnpB6_L4ILekVICF_0kep4Kq',  # Mario Maker (all)
    'PLRQGRBgN_Eno4h3d-LKBHSB7K89cWAC4f',  # Mario Maker 2
    'PLRQGRBgN_EnrjPMktYLDYVwjwK-TXjimo',  # Game grumps starter pack
    'PLRQGRBgN_Enr29rZZEzgSAQ21HjZXY0bv',  # Table flip
    'PLRQGRBgN_Enoz2CGGTgC3GqFoprgcsZFh',  # Wheel of fortune, has like 10 different series in it
    'PLRQGRBgN_EnoTAtMuaDjzjfuHvHVXXvZs',  # Mario party 10 dupe
    'PLRQGRBgN_EnocWoGhzsaXOgtlXhiX6LQC',  # Super Mega
}

PLAYLIST_SPLITS = {
    'PLRQGRBgN_Enr363LeUKhGZUif_ctjcSly': '2020-04-07T12:00:00Z',  # Mario Party 2
    'PLRQGRBgN_EnqnzgNkK8uEc6TIw-WLH9WM': '2015-11-20T00:00:00Z',  # Mario party 10
}

youtube_client = None


def main():
    while True:
        print('[0] Delete database')
        print('[1] Create database')
        print('[2] Backup database')
        print('[3] Find video')
        print('[4] Find playlist')
        print('[5] Dump created playlists')
        print('[6] Dump queue')
        input_value = input('Option: ')

        if input_value == '0':
            confirm = input('Delete database y/n: ')
            if confirm == 'y':
                drop_database()
                print('Database deleted')
        elif input_value == '1':
            init_db()
            print('Database created')
        elif input_value == '2':
            backup()
            print('Backup created')
        elif input_value == '3':
            video_id = input('Video ID: ')
            print(get_video_row(video_id))
        elif input_value == '4':
            playlist_id = input('Playlist ID: ')
            print(get_existing_playlist_row(playlist_id))
        elif input_value == '5':
            print_created_playlist_table()
        elif input_value == '6':
            print_queue()
        else:
            break
        print('')

    print('Done.')


# TABLE MANAGEMENT ####################################################################################################
def init_db():
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
    date = datetime.datetime.now().strftime("%Y%m%d")

    con = sqlite3.connect(DATABASE_NAME)
    bck = sqlite3.connect(date + '-' + DATABASE_NAME)
    with bck:
        con.backup(bck)
    bck.close()
    con.close()


def drop_database():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS existing_videos''')
    c.execute('''DROP TABLE IF EXISTS existing_playlists''')
    # c.execute('''DROP TABLE IF EXISTS created_playlists''')
    conn.commit()
    conn.close()


# PRINT ###############################################################################################################
def print_created_playlist_table():
    conn = sqlite3.connect(DATABASE_NAME)
    for row in conn.execute(
            '''SELECT * FROM created_playlists'''):
        print(row)


def print_queue():
    for row in get_video_queue():
        print(row)


# CLEAR TABLES ########################################################################################################
def clear_existing_videos_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DELETE FROM existing_videos''')
    conn.commit()
    conn.close()


def clear_existing_playlist_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DELETE FROM existing_playlists''')
    conn.commit()
    conn.close()


def clear_created_playlist_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DELETE FROM created_playlists''')
    conn.commit()
    conn.close()


# GET ROWS ############################################################################################################
def get_video_row(video_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute(
        '''SELECT id,upload_date,existing_playlist_id,created_playlist_id,playlist_order,processed 
        FROM existing_videos WHERE id = ?''',
        (video_id,))
    row = c.fetchone()
    conn.close()
    if row is None:
        return None
    return {'video_id': row[0], 'upload_date': row[1], 'existing_playlist_id': row[2], 'created_playlist_id': row[3],
            'playlist_order': row[4], 'processed': row[5]}


def get_video_queue():
    conn = sqlite3.connect(DATABASE_NAME)
    videos = []
    for row in conn.execute(
            '''SELECT id,created_playlist_id,playlist_order,processed FROM existing_videos WHERE processed = ? 
            AND created_playlist_id IS NOT NULL ORDER BY playlist_order DESC''',
            (False,)):
        videos.append(
            {'video_id': row[0], 'playlist_id': row[1], 'order': row[2], 'processed': row[3]})
    conn.close()
    return videos


def get_video_playlist(video_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''SELECT existing_playlist_id FROM existing_videos WHERE id = ?''', (video_id,))
    row = c.fetchone()
    conn.close()

    if row is None:
        return None

    return row[0]


def get_videos_for_range(start_date, end_date):
    conn = sqlite3.connect(DATABASE_NAME)

    start_order = get_order_string(start_date, 0)
    end_order = get_order_string(end_date, 9999)
    videos = []
    for row in conn.execute(
            '''SELECT id,created_playlist_id,existing_playlist_id,upload_date,processed FROM existing_videos 
            WHERE playlist_order >= :start_date AND playlist_order <= :end_date''',
            {'start_date': start_order, 'end_date': end_order}):
        videos.append(
            {
                'video_id': row[0], 'created_playlist_id': row[1], 'existing_playlist_id': row[2],
                'playlist_order': row[3], 'processed': row[4]
            })
    conn.close()

    return videos


def get_videos_before(end_date):
    conn = sqlite3.connect(DATABASE_NAME)

    end_order = get_order_string(end_date, 0)
    videos = []
    for row in conn.execute(
            '''SELECT id,created_playlist_id,existing_playlist_id,upload_date,processed FROM existing_videos 
            WHERE playlist_order <= :end_date''',
            {'end_date': end_order}):
        videos.append(
            {
                'video_id': row[0], 'created_playlist_id': row[1], 'existing_playlist_id': row[2],
                'playlist_order': row[3], 'processed': row[4]
            })
    conn.close()

    return videos


def get_videos_after(start_date):
    conn = sqlite3.connect(DATABASE_NAME)

    start_order = get_order_string(start_date, 0)
    videos = []
    for row in conn.execute(
            '''SELECT id,created_playlist_id,existing_playlist_id,upload_date,processed FROM existing_videos 
            WHERE playlist_order >= :start_date''',
            {'start_date': start_order}):
        videos.append(
            {
                'video_id': row[0], 'created_playlist_id': row[1], 'existing_playlist_id': row[2],
                'playlist_order': row[3], 'processed': row[4]
            })
    conn.close()

    return videos


def get_videos_in_playlist(existing_playlist_id):
    conn = sqlite3.connect(DATABASE_NAME)

    videos = []
    for row in conn.execute(
            '''SELECT id,created_playlist_id,existing_playlist_id,upload_date FROM existing_videos 
            WHERE existing_playlist_id == existing_playlist_id''',
            {'existing_playlist_id': existing_playlist_id}):
        videos.append(
            {'video_id': row[0], 'created_playlist_id': row[1], 'existing_playlist_id': row[2], 'upload_date': row[3]})
    conn.close()

    return videos


def get_videos_in_created_playlist(created_playlist_id):
    conn = sqlite3.connect(DATABASE_NAME)

    videos = []
    for row in conn.execute(
            '''SELECT id,created_playlist_id,existing_playlist_id,playlist_order FROM existing_videos 
            WHERE created_playlist_id == :created_playlist_id AND processed = :processed''',
            {'created_playlist_id': created_playlist_id, 'processed': True}):
        videos.append(
            {
                'video_id': row[0], 'created_playlist_id': row[1], 'existing_playlist_id': row[2],
                'playlist_order': row[3]
            })
    conn.close()

    return videos


def get_existing_playlist_row(playlist_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute(
        '''SELECT id,date FROM existing_playlists WHERE id = ?''',
        (playlist_id,))
    row = c.fetchone()
    conn.close()
    return row


def get_created_playlist_id(start_date, end_date):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''SELECT id FROM created_playlists WHERE start_date = ? AND end_date = ?''', (start_date, end_date))
    row = c.fetchone()
    conn.close()

    if row is None:
        return None

    return row[0]


def get_created_playlists():
    playlists = []
    conn = sqlite3.connect(DATABASE_NAME)
    for row in conn.execute(
            '''SELECT id,start_date,end_date FROM created_playlists'''):
        playlists.append({'id': row[0], 'start_date': row[1], 'end_date': row[2]})
    return playlists


def list_existing_playlists():
    conn = sqlite3.connect(DATABASE_NAME)
    items = []
    for row in conn.execute('''SELECT id,date FROM existing_playlists'''):
        items.append({'playlist_id': row[0], 'date': row[1]})
    return items


# GENERATE TABLES ####################################################################################################
def insert_videos(videos):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.executemany(
        '''INSERT INTO existing_videos (id,upload_date,playlist_order) VALUES (:video_id,:date,:playlist_order)''',
        videos)
    conn.commit()


def insert_playlists(playlists):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.executemany('''INSERT INTO existing_playlists (id) VALUES (:playlist_id)''', playlists)
    conn.commit()
    conn.close()


def update_video_status(videos):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    if len(videos) == 0:
        return

    # Set the playlist for the video
    c.executemany(
        '''UPDATE existing_videos 
        SET existing_playlist_id = :existing_playlist_id, playlist_order = :playlist_order, processed = :processed
        WHERE id = :video_id''',
        videos)

    # Set the playlist date to the earliest video so insertion happens in the correct order
    c.execute('''UPDATE existing_playlists SET date = :date WHERE id = :existing_playlist_id''', videos[0])
    for video in videos:
        print(
            f'\nProcessed [{video["video_id"]}]/[{video["existing_playlist_id"]}]. ' +
            f'Consider updating playlist for {video["date"]}')

    conn.commit()
    conn.close()


# UPDATE ROWS #########################################################################################################
def store_created_playlist(playlist_id, start_date, end_date):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO created_playlists (id,start_date,end_date) VALUES (:playlist_id,:start_date,:end_date)''',
              {'playlist_id': playlist_id, 'start_date': start_date, 'end_date': end_date})
    conn.commit()
    conn.close()


def store_videos_to_add(item_list):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.executemany(
        '''UPDATE existing_videos
        SET id = :video_id,
        created_playlist_id = :created_playlist_id,
        processed = :processed 
        WHERE id = :video_id''',
        item_list)
    conn.commit()
    conn.close()


def mark_video_processed(video_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''UPDATE existing_videos SET processed = :processed WHERE id = :video_id''',
              {'processed': True, 'video_id': video_id})
    conn.commit()
    conn.close()


def mark_video_unprocessed(video_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''UPDATE existing_videos SET processed = :processed WHERE id = :video_id''',
              {'processed': False, 'video_id': video_id})
    conn.commit()
    conn.close()


def mark_all_videos_processed(created_playlist_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''UPDATE existing_videos SET processed = :processed WHERE created_playlist_id = :created_playlist_id''',
              {'processed': True, 'created_playlist_id': created_playlist_id})
    conn.commit()
    conn.close()


def mark_all_videos_unprocessed(created_playlist_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''UPDATE existing_videos SET processed = :processed WHERE created_playlist_id = :created_playlist_id''',
              {'processed': False, 'created_playlist_id': created_playlist_id})
    conn.commit()
    conn.close()


def remove_created_playlist_id(created_playlist_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''UPDATE existing_videos SET created_playlist_id = :new WHERE created_playlist_id = :created''',
              {'created': created_playlist_id, 'new': None})
    conn.commit()
    conn.close()


def update_playlist_dates():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    for key in PLAYLIST_SPLITS.keys():
        date = PLAYLIST_SPLITS[key]
        values = {'key': key, 'date': date, 'processed': False}
        c.execute('''UPDATE existing_playlists SET date = :date WHERE id = :key''', values)

        counter = 0
        after_date = get_videos_after(date)
        for video in after_date:
            values['order'] = get_order_string(date, counter)
            values['video_id'] = video['video_id']
            c.execute(
                '''UPDATE existing_videos 
                SET playlist_order = :order,
                processed = :processed
                WHERE id = :video_id''',
                values)
            counter += 1
    conn.commit()
    conn.close()


def clear_playlist_dates():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    vals = {'existing': None}
    for row in conn.execute(
            '''SELECT id,upload_date FROM existing_videos WHERE existing_playlist_id = :existing''',
            vals):
        vals['video_id'] = row[0]
        vals['date'] = row[1]
        vals['order'] = get_order_string(vals['date'], 0)
        c.execute(
            '''UPDATE existing_videos 
            SET playlist_order = :order,
            WHERE id = :video_id''',
            vals)
    conn.commit()
    conn.close()


def unprocess_existing_playlist(playlist_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    vals = {'existing': playlist_id, 'processed': False, 'none_value': None}
    c.execute('''DELETE FROM existing_playlists WHERE id = :existing''', vals)
    for row in conn.execute(
            '''SELECT id,upload_date FROM existing_videos WHERE existing_playlist_id = :existing''',
            vals):
        vals['date'] = row[1]
        vals['order'] = get_order_string(vals['date'], 0)
        vals['video_id'] = row[0]
        c.execute(
            '''UPDATE existing_videos 
            SET playlist_order = :order,
            processed = :processed,
            created_playlist_id = :none_value,
            existing_playlist_id = :none_value
            WHERE id = :video_id''',
            vals)
    conn.commit()
    conn.close()


def unprocess_created_playlist(playlist_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    values = {'created': playlist_id, 'processed': False, 'none_value': None}
    c.execute('''DELETE FROM existing_playlists WHERE id = :existing''', values)
    for row in conn.execute(
            '''SELECT id,upload_date FROM existing_videos WHERE created_playlist_id = :created''',
            values):
        values['date'] = row[1]
        values['order'] = get_order_string(values['date'], 0)
        values['video_id'] = row[0]
        c.execute(
            '''UPDATE existing_videos 
            SET playlist_order = :order,
            processed = :processed,
            created_playlist_id = :none_value,
            existing_playlist_id = :none_value
            WHERE id = :video_id''',
            values)
    conn.commit()


def remove_skipped_playlists():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    for playlist_id in SKIP_PLAYLISTS:
        values = {'playlist_id': playlist_id, 'none_value': None}
        c.execute('''DELETE FROM existing_playlists WHERE id = :playlist_id''', values)
    conn.commit()
    conn.close()


def get_order_string(date, num):
    return f'{date}~{"{:0>4d}".format(num)}'


if __name__ == "__main__":
    main()
