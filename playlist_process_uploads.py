import youtube_reads as youtube_read
import playlists_utils as utils
import playlist_config as config
import database_reads as database_read
import database_utils as database_util
import database_mutations as database_mutate
from dotenv import load_dotenv

load_dotenv()


def process():
    """
    Process Channel uploads

    :return:
    """

    utils.dry_run_prompt()
    utils.authorize()

    raw_uploads = _list_all_uploads()
    new_uploads = _process_uploads(raw_uploads)

    if utils.dry_run:
        for upload in new_uploads:
            print(f'Insert {upload["video_id"]} / {upload["date"]} / {upload["playlist_order"]}')
        print('')
    else:
        database_mutate.insert_videos(new_uploads)


def _list_all_uploads():
    """
    Lists all uploads in the playlists indicated by the UPLOADS_PLAYLISTS lists in playlist.config.

    :return:
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
    :return:
    """

    items = []
    counter = 0

    for result in response_items:
        video_id = result.get('snippet').get('resourceId').get('videoId')
        publish_date = result.get('contentDetails').get('videoPublishedAt')

        # Skip processing if the video is already processed
        if database_read.get_video_row(video_id) is not None:
            continue

        # Skip processing if the video is in the SKIP_VIDEOS_LIST
        if video_id in config.SKIP_VIDEOS:
            continue

        counter += 1
        items.append({
            'video_id': video_id, 'date': publish_date,
            'playlist_order': database_util.get_order_string(publish_date, 0),
        })

    print(f'{counter} new videos')
    return items
