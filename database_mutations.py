import database_utils as utils


def mark_video_unprocessed(video_id):
    """
    Marks a video as unprocessed
    """

    utils.execute('''UPDATE existing_videos SET processed = :processed WHERE id = :video_id''',
                  {'processed': False, 'video_id': video_id})


def mark_playlist_unprocessed(playlist_id):
    """
    Marks every video in an existing playlist as unprocessed
    """

    utils.execute(
        '''UPDATE existing_videos SET processed = :processed WHERE existing_playlist_id = :existing_playlist_id''',
        {'processed': False, 'existing_playlist_id': playlist_id})


def mark_created_playlist_unprocessed(playlist_id):
    """
    Marks every video in a created playlist as unprocessed
    """

    utils.execute(
        '''UPDATE existing_videos SET processed = :processed WHERE created_playlist_id = :created_playlist_id''',
        {'processed': False, 'created_playlist_id': playlist_id})


def remove_video_from_created_playlist(video_id):
    """
    Removes the connection between a video and its created playlist
    """

    utils.execute('''UPDATE existing_videos SET created_playlist_id = :created_playlist_id WHERE id = :video_id''',
                  {'video_id': video_id, 'created_playlist_id': None})


def remove_all_from_created_playlist(created_playlist_id):
    """
    Removes the connection between a video and their created playlist
    """

    utils.execute('''UPDATE existing_videos SET created_playlist_id = :new_id WHERE created_playlist_id = :old_id''',
                  {'old_id': created_playlist_id, 'new_id': None})


def remove_playlist_from_created_playlist(existing_playlist_id):
    """
    Removes the connection between all videos in an existing playlist and their created playlist
    """

    utils.execute(
        '''UPDATE existing_videos SET created_playlist_id = :created_playlist_id WHERE 
        existing_playlist_id = :existing_playlist_id''',
        {'existing_playlist_id': existing_playlist_id, 'created_playlist_id': None})
