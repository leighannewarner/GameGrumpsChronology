import database_utils as utils


# UNPROCESS ###########################################################################################################
def mark_video_unprocessed(video_id):
    """
    Marks a video as unprocessed.

    :param video_id:
    :return:
    """

    utils.execute('''UPDATE existing_videos SET processed = :processed WHERE id = :video_id''',
                  {'processed': False, 'video_id': video_id})


def mark_playlist_unprocessed(playlist_id):
    """
    Marks every video in an existing playlist as unprocessed.

    :param playlist_id:
    :return:
    """

    utils.execute(
        '''UPDATE existing_videos SET processed = :processed WHERE existing_playlist_id = :existing_playlist_id''',
        {'processed': False, 'existing_playlist_id': playlist_id})


def mark_created_playlist_unprocessed(playlist_id):
    """
    Marks every video in a created playlist as unprocessed.

    :param playlist_id:
    :return:
    """

    utils.execute(
        '''UPDATE existing_videos SET processed = :processed WHERE created_playlist_id = :created_playlist_id''',
        {'processed': False, 'created_playlist_id': playlist_id})


# REMOVE FROM PLAYLIST ################################################################################################
def remove_video_from_created_playlist(video_id):
    """
    Removes the connection between a video and its created playlist.

    :param video_id:
    :return:
    """

    utils.execute('''UPDATE existing_videos SET created_playlist_id = :created_playlist_id WHERE id = :video_id''',
                  {'video_id': video_id, 'created_playlist_id': None})


def remove_all_from_created_playlist(created_playlist_id):
    """
    Removes the connection between a video and their created playlist.

    :param created_playlist_id:
    :return:
    """

    utils.execute('''UPDATE existing_videos SET created_playlist_id = :new_id WHERE created_playlist_id = :old_id''',
                  {'old_id': created_playlist_id, 'new_id': None})


def remove_playlist_from_created_playlist(existing_playlist_id):
    """
    Removes the connection between all videos in an existing playlist and their created playlist.

    :param existing_playlist_id:
    :return:
    """

    utils.execute(
        '''UPDATE existing_videos SET created_playlist_id = :created_playlist_id WHERE 
        existing_playlist_id = :existing_playlist_id''',
        {'existing_playlist_id': existing_playlist_id, 'created_playlist_id': None})


# UPDATE PLAYLIST ORDER ###############################################################################################
def update_playlist_order(videos):
    utils.execute_many('''UPDATE existing_videos SET playlist_order = :playlist_order WHERE video_id = :video_id''',
                       videos)


# INSERT ##############################################################################################################
def insert_created_playlist(playlist_id, start_date, end_date):
    """
    Store information about a created playlist.

    :param playlist_id:
    :param start_date:
    :param end_date:
    :return:
    """

    utils.execute(
        '''INSERT INTO created_playlists (id,start_date,end_date) VALUES (:playlist_id,:start_date,:end_date)''',
        {'playlist_id': playlist_id, 'start_date': start_date, 'end_date': end_date})


def insert_existing_playlists(playlists):
    """
    Insert a channel's playlist into the existing_playlists table.

    :param playlists: A list of dict objects containing a playlist_id key value
    :return:
    """
    utils.execute_many('''INSERT INTO existing_playlists (id) VALUES (:playlist_id)''', playlists)


def insert_videos(videos):
    """
    Insert all provided videos into the database, where each video is a map containing a video_id, date,
    and playlist_order.

    :param videos: A list containing dictionaries of video properties
    :return:
    """

    utils.execute_many(
        '''INSERT INTO existing_videos (id,upload_date,playlist_order) VALUES (:video_id,:date,:playlist_order)''',
        videos)
