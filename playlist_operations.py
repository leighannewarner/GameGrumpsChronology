import playlists_utils as utils
import database_reads as database_read
import database_mutations as database_mutate
import youtube_mutations as youtube_mutate
import playlist_config as config
import os
import youtube_reads as youtube_read


def create_playlists():
    """
    Creates missing playlists based on the CREATED_PLAYLISTS config option in playlist_config.py.

    :return:
    """

    utils.dry_run_prompt()

    if utils.dry_run:
        print('DRY RUN ' + ('=' * 70))
        for playlist in config.CREATED_PLAYLISTS:
            print(f'{playlist[0]} {playlist[1]} {playlist[2]}')
        return

    for playlist in config.CREATED_PLAYLISTS:
        _create_playlist(playlist[0], playlist[1], playlist[2])


def _create_playlist(start_date, end_date, title):
    """
    Creates a playlist on the authorized YouTube Channel to hold videos for a given date range.

    :param start_date: Start of the date range this playlist should cover
    :param end_date: End of the date range this playlist should cover
    :param title: Title of the playlist
    :return:
    """

    playlist_id = database_read.get_created_playlist_id(start_date, end_date)
    if playlist_id is not None:
        print(f'Using existing playlist [{playlist_id}]')
        return

    utils.authorize()
    playlist_id = youtube_mutate.create_playlist(youtube_client=utils.youtube_client, title=title,
                                                 description=os.getenv('PLAYLIST_DESCRIPTION'), tags=['Game Grumps'])
    database_mutate.insert_created_playlist(playlist_id, start_date, end_date)
    print(f'Created playlist [{playlist_id}]')


def insert_video(playlist_id, video_id, position):
    """

    :param playlist_id:
    :param video_id:
    :param position:
    :return:
    """
    utils.dry_run_prompt()

    if utils.dry_run:
        return

    youtube_mutate.insert_video_into_playlist(youtube_client=utils.youtube_client, video_id=video_id,
                                              playlist_id=playlist_id, position=position)


def update_video(playlist_id, video_id, position):
    """

    :param playlist_id:
    :param video_id:
    :param position:
    :return:
    """
    utils.dry_run_prompt()

    if utils.dry_run:
        return

    youtube_mutate.update_video_in_playlist(youtube_client=utils.youtube_client, video_id=video_id,
                                            playlist_id=playlist_id, position=position)


def list_videos_in_playlist(playlist_id):
    """
    Lists all uploads in the given playlist

    :return: A list of videos as json items
    """

    utils.authorize()
    return youtube_read.list_videos_in_playlist(youtube_client=utils.youtube_client, playlist_id=playlist_id)


def delete_video_from_playlist(playlist_id, video_id):
    """
    Delete a video from the given playlist

    :param playlist_id:
    :param video_id:
    :return:
    """

    utils.authorize()
    youtube_mutate.delete_video_from_playlist(youtube_client=utils.youtube_client, playlist_id=playlist_id,
                                              video_id=video_id)


def delete_duplicate_videos_from_playlist(playlist_id, video_id):
    """
    Delete duplicates of a video from the given playlist

    :param playlist_id:
    :param video_id:
    :return:
    """

    utils.authorize()
    youtube_mutate.delete_duplicate_videos_from_playlist(youtube_client=utils.youtube_client, video_id=video_id,
                                                         playlist_id=playlist_id)
