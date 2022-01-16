import playlists_utils as utils
import database_reads as database_read
import database_mutations as database_mutate
import youtube_mutations as youtube_mutate
import os


def create_playlist(start_date, end_date, title):
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
    database_mutate.store_created_playlist(playlist_id, start_date, end_date)
    print(f'Created playlist [{playlist_id}]')
