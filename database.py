import os
import sqlite3
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
    'PLRQGRBgN_Enp7jEkUuzG5Z32gLY8-pPJl',  # Weird Bayonetta playlist with only one video that is private
    'PLRQGRBgN_EnqUyjIu3IxgrenDPTVOV_wM',  # SteamRolled
    'PLRQGRBgN_EnpND5AJknSiwwP9OKMYx4RP',  # Ghoul Grumps
    'FL9CuvdOVfMPvKCiwdGKL3cQ'             # Favorites
}

playlist_date_overrides = {'PLRQGRBgN_Enoz2CGGTgC3GqFoprgcsZFh': '2013-09-19T12:00:00Z',  # Wheel of fortune
                           'PLRQGRBgN_Enr363LeUKhGZUif_ctjcSly': '2020-04-07T12:00:00Z'  # Mario Party 2
                           }

youtube_client = None


def main():
    while True:
        print('[0] Delete database')
        print('[1] Create database')
        print('[2] Process channel uploads')
        print('[3] Process channel playlists')
        print('[4] Interleave videos and playlists')
        print('[5] Find video')
        print('[6] Find playlist')
        print('[7] Dump created playlists')
        print('[8] Mark video unprocessed')
        print('[9] Update overrides')
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
            populate_existing_videos_table()
            print('Table populated')
        elif input_value == '3':
            populate_existing_playlists_table()
            print('Table populated')
        elif input_value == '4':
            interleave_videos_in_playlists()
            print('Table populated')
        elif input_value == '5':
            video_id = input('Video ID: ')
            print(get_video_row(video_id))
        elif input_value == '6':
            playlist_id = input('Playlist ID: ')
            print(get_existing_playlist_row(playlist_id))
        elif input_value == '7':
            print_created_playlist_table()
        elif input_value == '8':
            video_id = input('Video ID: ')
            mark_video_unprocessed(video_id)
        elif input_value == '9':
            update_playlist_dates()
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


def drop_database():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS existing_videos''')
    c.execute('''DROP TABLE IF EXISTS existing_playlists''')
    c.execute('''DROP TABLE IF EXISTS created_playlists''')
    conn.commit()
    conn.close()


# PRINT ###############################################################################################################
def print_created_playlist_table():
    conn = sqlite3.connect(DATABASE_NAME)
    for row in conn.execute(
            '''SELECT * FROM created_playlists'''):
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
    return row


def get_video_queue():
    conn = sqlite3.connect(DATABASE_NAME)
    videos = []
    for row in conn.execute(
            '''SELECT id,created_playlist_id,playlist_order FROM existing_videos WHERE processed = ? 
            AND created_playlist_id IS NOT NULL ORDER BY playlist_order ASC''',
            (False,)):
        videos.append({'video_id': row[0], 'playlist_id': row[1], 'order': row[2]})
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
            '''SELECT id,created_playlist_id,existing_playlist_id,upload_date FROM existing_videos 
            WHERE playlist_order >= :start_date AND playlist_order <= :end_date''',
            {'start_date': start_order, 'end_date': end_order}):
        videos.append(
            {
                'video_id': row[0], 'created_playlist_id': row[1], 'existing_playlist_id': row[2],
                'playlist_order': row[3]
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
            WHERE created_playlist_id == :created_playlist_id''',
            {'created_playlist_id': created_playlist_id}):
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


def get_existing_playlist_date(playlist_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''SELECT date FROM existing_playlist WHERE id = ?''', (playlist_id,))
    row = c.fetchone()
    conn.close()

    if row is None:
        return None

    return row[0]


def get_created_playlists():
    playlists = {}
    conn = sqlite3.connect(DATABASE_NAME)
    for row in conn.execute(
            '''SELECT id,start_date,end_date FROM created_playlists'''):
        playlists = {'id': row[0], 'start_date': row[1], 'end_date': row[2]}
    return playlists


# GENERATE TABLES ####################################################################################################
def populate_existing_videos_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    videos = list_all_uploads()
    c.executemany(
        '''INSERT INTO existing_videos (id,upload_date,playlist_order) VALUES (:video_id,:date,:playlist_order)''',
        videos)
    conn.commit()
    conn.close()


def populate_existing_playlists_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    playlists = list_all_playlists_for_channel()
    c.executemany('''INSERT INTO existing_playlists (id) VALUES (?)''', playlists)
    conn.commit()
    conn.close()


def interleave_videos_in_playlists():
    remove_skipped_playlists()

    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    for row in conn.execute('''SELECT id FROM existing_playlists'''):
        playlist_id = row[0]
        video_ids = list_all_videos_in_playlist(playlist_id)

        if len(video_ids) == 0:
            continue

        # Set the playlist for the video
        c.executemany(
            '''UPDATE existing_videos 
            SET existing_playlist_id = :playlist_id, playlist_order = :playlist_order 
            WHERE id = :video_id''',
            video_ids)
        # Set the playlist date to the earliest video so insertion happens in the correct order
        c.execute('''UPDATE existing_playlists SET date = :date WHERE id = :playlist_id''', video_ids[0])
        for video in video_ids:
            print(
                f'Processed [{video["video_id"]}]. Consider updating playlist for {video["date"]}')
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
        SET id = :video_id,created_playlist_id = :created_playlist_id,processed = :processed WHERE id = :video_id''',
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
    for key in playlist_date_overrides.keys():
        date = playlist_date_overrides[key]
        vals = {'key': key, 'date': date, 'processed': False, 'created': None}
        c.execute('''UPDATE existing_playlists SET date = :date WHERE id = :key''', vals)
        counter = 0
        for row in conn.execute(
                '''SELECT id FROM existing_videos WHERE existing_playlist_id = :key ORDER BY upload_date ASC''',
                vals):
            vals['order'] = get_order_string(date, counter)
            vals['video_id'] = row[0]
            c.execute(
                '''UPDATE existing_videos 
                SET playlist_order = :order,processed = :processed,created_playlist_id = :created 
                WHERE id = :video_id''',
                vals)
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


def remove_skipped_playlists():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    for playlist_id in SKIP_PLAYLISTS:
        values = {'playlist_id': playlist_id, 'none_value': None}
        c.execute('''DELETE FROM existing_playlists WHERE id = :playlist_id''', values)
        c.execute(
            '''UPDATE existing_videos SET existing_playlist_id = :none_value 
            WHERE existing_playlist_id = :playlist_id''',
            values)
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
        # Skip processing if the playlist is already in the db
        if get_existing_playlist_row(playlist_id) is None:
            items.append((playlist_id,))
    return items


def list_all_uploads():
    print(f'Retrieving uploads')

    authorize()
    response_items = youtube.list_all_videos_in_playlist(youtube_client, os.getenv('UPLOADS_PLAYLIST'))

    items = []
    for result in response_items:
        publish_date = result.get('contentDetails').get('videoPublishedAt')
        video_id = result.get('snippet').get('resourceId').get('videoId')

        # Skip processing if the video is already processed
        if get_video_row(video_id) is None:
            items.append({
                'video_id': video_id, 'date': publish_date,
                'playlist_order': get_order_string(publish_date, 0)
            })
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

    index = 0
    for result in response_items:
        video_id = result.get('snippet').get('resourceId').get('videoId')
        # Skip processing if the video is already updated
        if get_video_playlist(video_id) is None:
            items.append({
                'video_id': video_id, 'playlist_id': playlist_id, 'date': publish_date,
                'playlist_order': get_order_string(publish_date, index)
            })
        index += 1
    return items


def get_order_string(date, num):
    return f'{date}~{"{:0>4d}".format(num)}'


if __name__ == "__main__":
    main()
