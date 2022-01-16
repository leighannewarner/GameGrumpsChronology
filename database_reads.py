import database_utils as utils


# VIDEOS ##############################################################################################################
def get_video_row(video_id):
    """
    Retrieves the specified video row and returns a map of database values.
    """

    row = utils.execute_one(
        '''SELECT id,upload_date,existing_playlist_id,created_playlist_id,playlist_order,processed 
        FROM existing_videos WHERE id = :video_id''',
        {'video_id': video_id})

    return {'video_id': row[0], 'upload_date': row[1], 'existing_playlist_id': row[2], 'created_playlist_id': row[3],
            'playlist_order': row[4], 'processed': row[5]}


def get_video_queue():
    """
    Retrieves a list of videos that need to be processed and them as maps of database values
    """

    videos = []
    for row in utils.execute(
            '''SELECT id,created_playlist_id,playlist_order,processed FROM existing_videos WHERE processed = ? 
            AND created_playlist_id IS NOT NULL ORDER BY playlist_order DESC''',
            {'processed': False}):
        videos.append(
            {'video_id': row[0], 'playlist_id': row[1], 'order': row[2], 'processed': row[3]})
    return videos


# EXISTING PLAYLISTS ##################################################################################################
def get_existing_playlist_row(playlist_id):
    """
    Retrieves the specified playlist row and returns a map of database values.
    """

    row = utils.execute_one(
        '''SELECT id,date FROM existing_playlists WHERE id = :playlist_id''',
        {'playlist_id': playlist_id})[0]
    return row
