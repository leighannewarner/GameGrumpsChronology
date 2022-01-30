from dotenv import load_dotenv
import database_mutations as database_mutate
import database_reads
import database_utils as database_util
import os
import playlist_config as config
import playlists_utils as utils
import youtube_reads as youtube_read

load_dotenv()


def process():
    """
    Process Channel uploads

    :return:
    """

    utils.dry_run_prompt()
    utils.authorize()

    # List and process all the uploads on the Channel
    raw_uploads = _list_all_uploads()
    new_uploads = _process_uploads(raw_uploads)

    if utils.dry_run:
        for upload in new_uploads:
            print(f'Insert {upload["video_id"]} / {upload["date"]} / {upload["playlist_order"]}')
        print('')
    else:
        database_mutate.insert_videos(new_uploads)

    # List and process all playlists
    raw_playlists = _list_channel_playlists()
    new_playlists = _process_channel_playlists(raw_playlists)

    if utils.dry_run:
        for playlist in new_playlists:
            print(f'Insert {playlist["playlist_id"]}')
        print('')
    else:
        database_mutate.insert_existing_playlists(new_playlists)


def _list_all_uploads():
    """
    Lists all uploads in the playlists indicated by the UPLOADS_PLAYLISTS lists in playlist.config.

    :return: A list of videos as json items
    """

    utils.authorize()
    items = []

    for playlist_id in config.UPLOADS_PLAYLISTS:
        print(f'[{playlist_id}] Retrieving uploads...')
        items.extend(youtube_read.list_videos_in_playlist(utils.youtube_client, playlist_id))

    return items


def _process_uploads(response_items):
    """
    Filters previously processed videos so new ones can be inserted.

    :param response_items:
    :return: A list of newly added videos as dict items
    """

    items = []
    counter = 0

    for result in response_items:
        video_id = result.get('snippet').get('resourceId').get('videoId')
        publish_date = result.get('contentDetails').get('videoPublishedAt')

        # Skip processing if the video is already processed
        if database_reads.get_video_row(video_id) is not None:
            continue

        # Skip processing if the video is in the SKIP_VIDEOS_LIST
        if video_id in config.SKIP_VIDEOS:
            continue

        items.append({
            'video_id': video_id, 'date': publish_date,
            'playlist_order': database_util.get_order_string(publish_date, 0),
        })
        counter += 1

    print(f'{counter} new videos')
    return items


def _list_channel_playlists():
    """
    Lists all the playlists indicated by the CHANNEL_ID in the dotenv file

    :return: A list of playlists as json items
    """

    utils.authorize()
    channel_id = os.getenv('CHANNEL_ID')

    print(f'[{channel_id}] Retrieving playlists...')
    items = youtube_read.list_playlists_on_channel(utils.youtube_client, channel_id)

    return items


def _process_channel_playlists(response_items):
    """

    :param response_items:
    :return: A list of newly added playlists as dict objects
    """

    items = []
    counter = 0

    for result in response_items:
        playlist_id = result.get('id')

        # Skip processing if the playlist is already processed
        if database_reads.get_existing_playlist_row(playlist_id) is not None:
            continue

        # Skip processing if the playlist should be skipped when considering insertion order
        if result.get('id') in config.SKIP_PLAYLISTS:
            continue

        counter += 1
        items.append({'playlist_id': playlist_id})

    print(f'{counter} new playlists')
    return items
