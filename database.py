import sqlite3
import datetime
from database_utils import DATABASE_NAME, RETRY_LIMIT, get_order_string, execute, execute_one, execute_many


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
    'PLRQGRBgN_EnrbKMOysGunwG4vdcmJwK8c',  # Second Undertale playlist
    'PLRQGRBgN_Enofh0M71j-c-JFuCM6Fpu7y',  # Livestreams
    'PLRQGRBgN_EnqU1NBgebcb6qP3YfYhmFi5',  # Reaction compilations
    'PLRQGRBgN_EnpvWVnEytLys8wLUHm5NSFh',  # Space Quest (game chronology)
    'PLRQGRBgN_Enq0QqqVJx8LDpNGdxlgEhO3',  # All monopoly series
    'PLRQGRBgN_EnqsgAMZkHdcQswhgYSqsptx',  # Mario party all series, there are a lot of dupe playlists
    'PLRQGRBgN_EnpB6_L4ILekVICF_0kep4Kq',  # Mario Maker (all)
    'PLRQGRBgN_Eno4h3d-LKBHSB7K89cWAC4f',  # Mario Maker 2
    'PLRQGRBgN_EnrjPMktYLDYVwjwK-TXjimo',  # Game grumps starter pack
    'PLRQGRBgN_Enr29rZZEzgSAQ21HjZXY0bv',  # Table Flip
    'PLRQGRBgN_Enoz2CGGTgC3GqFoprgcsZFh',  # Wheel of fortune, has like 10 different series in it
    'PLRQGRBgN_EnoTAtMuaDjzjfuHvHVXXvZs',  # Mario party 10 dupe
    'PLRQGRBgN_EnocWoGhzsaXOgtlXhiX6LQC',  # Super Mega
}

PLAYLIST_SPLITS = {
    'PLRQGRBgN_Enr363LeUKhGZUif_ctjcSly': '2020-04-07T12:00:00Z',  # Mario Party 2
    'PLRQGRBgN_EnqnzgNkK8uEc6TIw-WLH9WM': '2015-11-20T00:00:00Z',  # Mario Party 10
    'PLRQGRBgN_EnoTjbUUPdHGN0Fs3f6Zl5dL': '2021-04-15T00:00:00Z',  # Danganronpa best ofs
}


def main():
    while True:
        print('[0] Delete database')
        print('[1] Create database')
        print('[2] Backup database')
        print('[3] Find video')
        print('[4] Find playlist')
        print('[5] Dump created playlists')
        print('[6] Dump queue')
        print('[7] Spot fix')
        print('[8] Reset video')
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
        elif input_value == '7':
            spot_fix()
        elif input_value == '8':
            reset_video()
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
    c.execute('''DROP TABLE IF EXISTS created_playlists''')
    conn.commit()
    conn.close()


def spot_fix():
    video_id = input('Insert after (video ID): ')
    new_date = input('New Date [yyyy-mm-dd]: ')
    index = int(input('Index: '))
    playlist = input('Playlist ID: ')

    row = get_video_row(video_id)
    order = get_order_string(new_date, index)

    print(f'Update [{row["video_id"]}] insertion order from [{row["playlist_order"]}] to [{order}]')
    confirm = input('Proceed? (y/n): ')
    if confirm != 'y':
        return

    try:
        update_video_order(video_id, order, playlist)
    except sqlite3.OperationalError as err:
        print(err)
        return

    print('Row updated\n')


def reset_video():
    video_id = input('Video ID: ')
    mark_video_unprocessed(video_id)
    remove_video_from_created_playlist(video_id)


# PRINT ###############################################################################################################
def print_created_playlist_table():
    for row in execute('''SELECT * FROM created_playlists'''):
        print(row)


def print_queue():
    for row in get_video_queue():
        print(row)


# CLEAR TABLES ########################################################################################################
def clear_existing_videos_table():
    execute('''DELETE FROM existing_videos''')


def clear_existing_playlist_table():
    execute('''DELETE FROM existing_playlists''')


def clear_created_playlist_table():
    execute('''DELETE FROM created_playlists''')


def execute(query, values={}):
    retries = 0
    rows = []
    while retries < RETRY_LIMIT:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            c = conn.cursor()
            c.execute(query, values)
            rows = c.fetchall()
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as err:
            retries += 1
            if retries >= RETRY_LIMIT:
                print(err)
                return []

    return rows


def execute_one(query, values={}):
    retries = 0
    row = None
    while retries < RETRY_LIMIT:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as err:
            retries += 1
            if retries >= RETRY_LIMIT:
                print(err)
                return None

    return row


def execute_many(query, values):
    retries = 0
    while retries < RETRY_LIMIT:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            c = conn.cursor()
            c.executemany(query, values)
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as err:
            retries += 1
            if retries >= RETRY_LIMIT:
                print(err)
                return


# GET ROWS ############################################################################################################
def get_video_row(video_id):
    row = execute_one(
        '''SELECT id,upload_date,existing_playlist_id,created_playlist_id,playlist_order,processed 
        FROM existing_videos WHERE id = :video_id''',
        {'video_id': video_id})

    return {'video_id': row[0], 'upload_date': row[1], 'existing_playlist_id': row[2], 'created_playlist_id': row[3],
            'playlist_order': row[4], 'processed': row[5]}


def get_video_queue():
    videos = []
    for row in execute(
            '''SELECT id,created_playlist_id,playlist_order,processed FROM existing_videos WHERE processed = ? 
            AND created_playlist_id IS NOT NULL ORDER BY playlist_order DESC''',
            {'processed': False}):
        videos.append(
            {'video_id': row[0], 'playlist_id': row[1], 'order': row[2], 'processed': row[3]})[0]
    return videos


def get_video_playlist(video_id):
    row = execute_one('''SELECT existing_playlist_id FROM existing_videos WHERE id = ?''', (video_id,))
    return row


def get_videos_for_range(start_date, end_date):
    start_order = get_order_string(start_date, 0)
    end_order = get_order_string(end_date, 9999)
    videos = []
    for row in execute(
            '''SELECT id,created_playlist_id,existing_playlist_id,upload_date,processed FROM existing_videos 
            WHERE playlist_order >= :start_date AND playlist_order <= :end_date''',
            {'start_date': start_order, 'end_date': end_order}):
        videos.append(
            {
                'video_id': row[0], 'created_playlist_id': row[1], 'existing_playlist_id': row[2],
                'playlist_order': row[3], 'processed': row[4]
            })

    return videos


def get_videos_before(end_date):
    end_order = get_order_string(end_date, 0)
    videos = []
    for row in execute(
            '''SELECT id,created_playlist_id,existing_playlist_id,upload_date,processed FROM existing_videos 
            WHERE playlist_order <= :end_date''',
            {'end_date': end_order}):
        videos.append(
            {
                'video_id': row[0], 'created_playlist_id': row[1], 'existing_playlist_id': row[2],
                'playlist_order': row[3], 'processed': row[4]
            })

    return videos


def get_videos_after(start_date):
    start_order = get_order_string(start_date, 0)
    videos = []
    for row in execute(
            '''SELECT id,created_playlist_id,existing_playlist_id,upload_date,processed FROM existing_videos 
            WHERE playlist_order >= :start_date''',
            {'start_date': start_order}):
        videos.append(
            {
                'video_id': row[0], 'created_playlist_id': row[1], 'existing_playlist_id': row[2],
                'playlist_order': row[3], 'processed': row[4]
            })

    return videos


def get_videos_in_playlist(existing_playlist_id):
    videos = []
    for row in execute(
            '''SELECT id,created_playlist_id,existing_playlist_id,upload_date FROM existing_videos 
            WHERE existing_playlist_id == existing_playlist_id''',
            {'existing_playlist_id': existing_playlist_id}):
        videos.append(
            {'video_id': row[0], 'created_playlist_id': row[1], 'existing_playlist_id': row[2], 'upload_date': row[3]})

    return videos


def get_videos_in_created_playlist(created_playlist_id):
    videos = []
    for row in execute(
            '''SELECT id,created_playlist_id,existing_playlist_id,playlist_order FROM existing_videos 
            WHERE created_playlist_id == :created_playlist_id AND processed = :processed''',
            {'created_playlist_id': created_playlist_id, 'processed': True}):
        videos.append(
            {
                'video_id': row[0], 'created_playlist_id': row[1], 'existing_playlist_id': row[2],
                'playlist_order': row[3]
            })

    return videos


def get_existing_playlist_row(playlist_id):
    row = execute_one(
        '''SELECT id,date FROM existing_playlists WHERE id = :playlist_id''',
        {'playlist_id': playlist_id})[0]
    return row


def get_created_playlist_id(start_date, end_date):
    row = execute_one(
        '''SELECT id FROM created_playlists WHERE start_date = :start_date AND end_date = :end_date''',
        {start_date, end_date})

    return row[0]


def get_created_playlists():
    playlists = []
    for row in execute_one(
            '''SELECT id,start_date,end_date FROM created_playlists'''):
        playlists.append({'id': row[0], 'start_date': row[1], 'end_date': row[2]})
    return playlists


def list_existing_playlists():
    items = []
    for row in execute('''SELECT id,date FROM existing_playlists'''):
        items.append({'playlist_id': row[0], 'date': row[1]})
    return items


# GENERATE TABLES ####################################################################################################
def insert_videos(videos):
    execute_many(
        '''INSERT INTO existing_videos (id,upload_date,playlist_order) VALUES (:video_id,:date,:playlist_order)''',
        videos)


def insert_playlists(playlists):
    execute_many('''INSERT INTO existing_playlists (id) VALUES (:playlist_id)''', playlists)


def update_video_status(videos):

    if len(videos) == 0:
        return

    # Set the playlist for the video
    execute_many(
        '''UPDATE existing_videos 
        SET existing_playlist_id = :existing_playlist_id, playlist_order = :playlist_order, processed = :processed
        WHERE id = :video_id''',
        videos)

    # Set the playlist date to the earliest video so insertion happens in the correct order
    execute('''UPDATE existing_playlists SET date = :date WHERE id = :existing_playlist_id''', videos[0])
    for video in videos:
        print(
            f'\nProcessed [{video["video_id"]}]/[{video["existing_playlist_id"]}]. ' +
            f'Consider updating playlist for {video["date"]}')


# UPDATE ROWS #########################################################################################################
def store_created_playlist(playlist_id, start_date, end_date):
    execute('''INSERT INTO created_playlists (id,start_date,end_date) VALUES (:playlist_id,:start_date,:end_date)''',
              {'playlist_id': playlist_id, 'start_date': start_date, 'end_date': end_date})


def store_videos_to_add(item_list):
    execute_many(
        '''UPDATE existing_videos
        SET id = :video_id,
        created_playlist_id = :created_playlist_id,
        processed = :processed 
        WHERE id = :video_id''',
        item_list)


def mark_video_processed(video_id):
    execute('''UPDATE existing_videos SET processed = :processed WHERE id = :video_id''',
              {'processed': True, 'video_id': video_id})


def mark_video_unprocessed(video_id):
    execute('''UPDATE existing_videos SET processed = :processed WHERE id = :video_id''',
              {'processed': False, 'video_id': video_id})


def mark_all_videos_processed(created_playlist_id):
    execute('''UPDATE existing_videos SET processed = :processed WHERE created_playlist_id = :created_playlist_id''',
              {'processed': True, 'created_playlist_id': created_playlist_id})


def mark_all_videos_unprocessed(created_playlist_id):
    execute('''UPDATE existing_videos SET processed = :processed WHERE created_playlist_id = :created_playlist_id''',
              {'processed': False, 'created_playlist_id': created_playlist_id})


def remove_video_from_created_playlist(video_id):
    execute('''UPDATE existing_videos SET created_playlist_id = :new WHERE id = :video_id''',
              {'video_id': video_id, 'new': None})


def remove_created_playlist_id(created_playlist_id):
    execute('''UPDATE existing_videos SET created_playlist_id = :new WHERE created_playlist_id = :created''',
              {'created': created_playlist_id, 'new': None})


def update_playlist_dates():
    for key in PLAYLIST_SPLITS.keys():
        date = PLAYLIST_SPLITS[key]
        values = {'key': key, 'date': date, 'processed': False}
        execute('''UPDATE existing_playlists SET date = :date WHERE id = :key''', values)

        counter = 0
        after_date = get_videos_after(date)
        for video in after_date:
            values['order'] = get_order_string(date, counter)
            values['video_id'] = video['video_id']
            execute(
                '''UPDATE existing_videos 
                SET playlist_order = :order,
                processed = :processed
                WHERE id = :video_id''',
                values)
            counter += 1


def clear_playlist_dates():
    values = {'existing': None}
    for row in execute(
            '''SELECT id,upload_date FROM existing_videos WHERE existing_playlist_id = :existing''',
            values):
        values['video_id'] = row[0]
        values['date'] = row[1]
        values['order'] = get_order_string(values['date'], 0)
        execute(
            '''UPDATE existing_videos 
            SET playlist_order = :order,
            WHERE id = :video_id''',
            values)


def unprocess_existing_playlist(playlist_id):
    values = {'existing': playlist_id, 'processed': False, 'none_value': None}
    execute('''DELETE FROM existing_playlists WHERE id = :existing''', values)
    for row in execute(
            '''SELECT id,upload_date FROM existing_videos WHERE existing_playlist_id = :existing''',
            values):
        values['date'] = row[1]
        values['order'] = get_order_string(values['date'], 0)
        values['video_id'] = row[0]
        execute(
            '''UPDATE existing_videos 
            SET playlist_order = :order,
            processed = :processed,
            created_playlist_id = :none_value,
            existing_playlist_id = :none_value
            WHERE id = :video_id''',
            values)


def unprocess_created_playlist(playlist_id):
    values = {'created': playlist_id, 'processed': False, 'none_value': None}
    execute('''DELETE FROM existing_playlists WHERE id = :existing''', values)
    for row in execute(
            '''SELECT id,upload_date FROM existing_videos WHERE created_playlist_id = :created''',
            values):
        values['date'] = row[1]
        values['order'] = get_order_string(values['date'], 0)
        values['video_id'] = row[0]
        execute(
            '''UPDATE existing_videos 
            SET playlist_order = :order,
            processed = :processed,
            created_playlist_id = :none_value,
            existing_playlist_id = :none_value
            WHERE id = :video_id''',
            values)


def update_video_order(video_id, playlist_order, playlist_id):
    execute(
        '''UPDATE existing_videos SET playlist_order = :playlist_order, created_playlist_id = :playlist_id 
        WHERE id = :video_id''',
        {'playlist_order': playlist_order, 'video_id': video_id, 'playlist_id': playlist_id})


def remove_skipped_playlists():
    for playlist_id in SKIP_PLAYLISTS:
        values = {'playlist_id': playlist_id, 'none_value': None}
        execute('''DELETE FROM existing_playlists WHERE id = :playlist_id''', values)


if __name__ == "__main__":
    main()
