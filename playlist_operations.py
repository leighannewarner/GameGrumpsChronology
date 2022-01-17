import playlists_utils as utils
import database_reads as database_read
import database_mutations as database_mutate
import youtube_mutations as youtube_mutate
import playlist_config as config
import os


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
