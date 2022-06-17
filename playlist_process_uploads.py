from dotenv import load_dotenv
import database_mutations
import database_mutations as database_mutate
import database_reads
import database_utils as database_util
import os
import playlist_config as config
import playlists_utils as utils
import youtube_reads as youtube_read
import playlist_operations as operations

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
    processed_uploads = _process_uploads(raw_uploads)

    if utils.dry_run:
        for upload in processed_uploads:
            print(f'Insert {upload["video_id"]} / {upload["upload_date"]} / {upload["playlist_order"]}')
    else:
        database_mutate.insert_videos(processed_uploads)

    # Update the skipped bit for videos
    _update_skipped()

    # List and process all playlists
    raw_playlists = _list_channel_playlists()
    processed_playlists = _process_channel_playlists(raw_playlists)

    if utils.dry_run:
        for playlist in processed_playlists:
            print(f'Insert {playlist["playlist_id"]}')
        print('')
    else:
        database_mutate.insert_existing_playlists(processed_playlists)

    playlist_videos = _process_playlist(processed_playlists)
    if utils.dry_run:
        for video in playlist_videos:
            print(f'Set {video["video_id"]} / {video["playlist_order"]} / {video["existing_playlist_id"]}')
        print('')
    else:
        database_mutate.update_playlist_order(playlist_videos)
        database_mutate.set_existing_playlist_id(playlist_videos)


def _list_all_uploads():
    """
    Lists all uploads in the playlists indicated by the UPLOADS_PLAYLISTS lists in playlist.config.

    :return: A list of videos as json items
    """

    items = []

    for playlist_id in config.UPLOADS_PLAYLISTS:
        print(f'[{playlist_id}] Retrieving uploads...')
        items.extend(operations.list_videos_in_playlist(playlist_id))

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
        publish_date = result.get('snippet').get('publishedAt')
        privacy_status = result.get('status').get('privacyStatus')

        # Count new videos
        if database_reads.get_video_row(video_id) is None:
            counter += 1

        items.append({
            'video_id': video_id, 'upload_date': publish_date,
            'playlist_order': database_util.get_order_string(publish_date, 0), 'existing_playlist_id': '',
            'public_video': privacy_status == 'public'
        })

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
    Processes raw json responses into a list of dict objects

    :param response_items:
    :return: A list of newly added playlists as dict objects
    """

    items = []
    counter = 0

    for result in response_items:
        playlist_id = result.get('id')

        # Skip processing if the playlist should be skipped when considering insertion order
        if playlist_id in config.SKIP_PLAYLISTS or playlist_id in config.STRICT_CHRONO:
            continue

        counter += 1
        items.append({'playlist_id': playlist_id})

    print(f'{counter} playlists processed')
    return items


def _process_playlist(playlists):
    """
    Lists items in each playlists and determines their insertion order

    :param playlists: A list of dict objects
    :return:
    """

    playlist_videos = []
    strict_chrono_videos = _get_strict_chrono()
    for playlist in playlists:
        playlist_id = playlist['playlist_id']

        print(f'[{playlist_id}] Processing playlist')
        fetch_id = playlist_id
        if playlist_id in config.ALTERNATE_PLAYLIST:
            fetch_id = config.ALTERNATE_PLAYLIST[playlist_id]

        videos = operations.list_videos_in_playlist(fetch_id)
        playlist_videos.extend(_process_playlist_videos(videos, playlist_id, strict_chrono_videos))
    return playlist_videos


def _process_playlist_videos(videos, playlist_id, strict_chrono_videos):
    """
    Determines the insertion order of a list of videos.

    :param videos:
    :return: map of video objects with playlist_order set
    """

    if len(videos) == 0:
        return []
    video_objects = []

    for video in videos:

        video_id = video.get('snippet').get('resourceId').get('videoId')
        status = video.get('status').get('privacyStatus')
        publish_date = video.get('snippet').get('publishedAt')

        video_row = database_reads.get_video_row(video_id)

        # If the video is in the playlist, but not in the db (eg: not a grumps upload), add it real quick
        if database_reads.get_video_row(video_id) is None:
            video_row = {'video_id': video_id, 'upload_date': publish_date,
                         'playlist_order': database_util.get_order_string(publish_date, 0),
                         'existing_playlist_id': playlist_id, 'public_video': status == 'public'}
            database_mutations.insert_videos([video_row])
        elif video_id in strict_chrono_videos:
            continue

        video_objects.append(
            {'video_id': video_id, 'upload_date': video_row['upload_date'], 'existing_playlist_id': playlist_id})

    video_objects = sorted(video_objects, key=lambda j: j['upload_date'])


    return _set_order_string(playlist_id, video_objects)


def _set_order_string(playlist_id, video_objects):
    """
    Sets the order string in the video objects list

    :param playlist_id: The id of the playlist being processed
    :param video_objects: The list of video objects to amend
    :return: The amended video objects with playlist_order
    """
    oldest_publish_date = None
    for video in video_objects[::1]:
        oldest_publish_date = video['upload_date']
        if oldest_publish_date is not None:
            break

    index = 0
    current_sort_date = oldest_publish_date
    is_split_playlist = playlist_id in config.PLAYLIST_SPLITS.keys()
    split_index = 0
    for i in range(len(video_objects)):
        if is_split_playlist and split_index < len(config.PLAYLIST_SPLITS[playlist_id]) and \
                video_objects[i]['upload_date'] >= config.PLAYLIST_SPLITS[playlist_id][split_index]:
            print(f'[{playlist_id}] Splitting at {config.PLAYLIST_SPLITS[playlist_id][split_index]}.')
            current_sort_date = config.PLAYLIST_SPLITS[playlist_id][split_index]
            split_index = split_index + 1
            index = 0

        video_objects[i]['playlist_order'] = database_util.get_order_string(current_sort_date, index)
        index = index + 1

    print(f'Processed {index} videos\n')

    return video_objects


def _get_strict_chrono():
    """
    List videos in strict chronological playlists.

    :return: A list of video ids
    """

    video_ids = set([])
    counter = 0

    for playlist_id in config.STRICT_CHRONO:
        counter += 1
        items = operations.list_videos_in_playlist(playlist_id)
        video_ids.update([v.get('snippet').get('resourceId').get('videoId') for v in items])

    print(f'{counter} playlists processed')
    return video_ids


def _update_skipped():
    database_videos = database_reads.get_all_videos()
    skipped_videos = set([v['video_id'] for v in database_videos if v['skipped']])
    inserted_videos = set([v['video_id'] for v in database_videos if not v['skipped']])
    all_videos = skipped_videos.union(inserted_videos)

    playlist_videos = set([])
    for playlist in config.FORCE_REMOVE:
        print(f'[{playlist}] Retrieving videos...')
        videos = operations.list_videos_in_playlist(playlist)
        playlist_videos.update([v.get('snippet').get('resourceId').get('videoId') for v in videos])

    playlist_videos.update(config.SKIP_VIDEOS)

    set_skipped = set(playlist_videos)
    set_inserted = all_videos.difference(playlist_videos)

    # Reduce the number of necessary updates by removing videos that are already the correct bit
    set_skipped = set_skipped.difference(skipped_videos)
    set_inserted = set_inserted.difference(inserted_videos)

    print(f'Marking {len(set_skipped)} videos to skip.')
    print(f'Marking {len(set_inserted)} videos to no longer skip.')

    if not utils.dry_run:
        database_mutations.mark_all_videos_not_skipped(set_inserted)
        database_mutations.mark_all_videos_skipped(set_skipped)
