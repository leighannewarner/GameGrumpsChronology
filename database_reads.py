import database_utils
import database_utils as utils


# VIDEOS ##############################################################################################################
def get_video_row(video_id):
    """
    Retrieves the specified video row and returns a map of database values.

    :param video_id:
    :return:
    """

    row = utils.execute_one(
        '''SELECT id,upload_date,existing_playlist_id,created_playlist_id,playlist_order,processed 
        FROM existing_videos WHERE id = :video_id''',
        {'video_id': video_id})

    if not row:
        return None

    return {'video_id': row[0], 'upload_date': row[1], 'existing_playlist_id': row[2], 'created_playlist_id': row[3],
            'playlist_order': row[4], 'processed': row[5]}


def get_video_queue():
    """
    Retrieves a list of videos that need to be processed and them as maps of database values.

    :return: A list of video objects
    """

    videos = []
    for row in utils.execute(
            '''SELECT id,created_playlist_id,playlist_order,processed FROM existing_videos 
            WHERE created_playlist_id IS NULL 
            ORDER BY playlist_order DESC''',
            {'processed': False}):
        videos.append(
            {'video_id': row[0], 'playlist_id': row[1], 'order': row[2], 'processed': row[3]})
    return videos


def get_video_queue_for_range(start_date, end_date):
    """
    Retrieves a list of videos that need to be processed within a date range and them as maps of database values.

    :return: A list of video objects
    """

    videos = []
    for row in utils.execute(
            '''SELECT id,created_playlist_id,playlist_order,processed FROM existing_videos 
            WHERE playlist_order >= :start_date AND playlist_order <= :end_date
            ORDER BY playlist_order DESC''',
            {'start_date': database_utils.get_order_string(start_date, 0),
             'end_date': database_utils.get_order_string(end_date, 9999)}):
        videos.append(
            {'video_id': row[0], 'playlist_id': row[1], 'order': row[2], 'processed': row[3]})
    return videos


# EXISTING PLAYLISTS ##################################################################################################
def get_existing_playlist_row(playlist_id):
    """
    Retrieves the specified playlist row and returns a map of database values.

    :param playlist_id:
    :return:
    """

    row = utils.execute_one(
        '''SELECT id,date FROM existing_playlists WHERE id = :playlist_id''',
        {'playlist_id': playlist_id})
    return row[0] if row else None


# CREATED PLAYLISTS ###################################################################################################
def get_created_playlist(playlist_id):
    """
    Retrieves the playlist information given an id

    :param playlist_id:
    :return: A playlist object
    """
    row = utils.execute_one('''SELECT * FROM created_playlists WHERE id = :playlist_id''', {'playlist_id': playlist_id})
    return {'playlist_id': row[0], 'start_date': row[1], 'end_date': row[2]}


def get_created_playlist_id(start_date, end_date):
    """
    Retrieves the playlist id for a specified date range.

    :param start_date:
    :param end_date:
    :return:
    """
    row = utils.execute_one(
        '''SELECT id FROM created_playlists WHERE start_date = :start_date AND end_date = :end_date''',
        {'start_date': start_date, 'end_date': end_date})

    return row[0] if row else None


def get_all_created_playlists():
    """
    Retrieves all the created playlists.

    :return: A list of playlist objects
    """

    playlists = []
    for row in utils.execute('''SELECT id,start_date,end_date FROM created_playlists ORDER BY start_date DESC'''):
        playlists.append({'playlist_id': row[0], 'start_date': row[1], 'end_date': row[2]})
    return playlists
