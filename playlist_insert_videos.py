import database_reads
import playlists_utils as utils
import playlist_operations as operations

LIMIT = 250
counter = 0


def insert():
    """
    Updates the live playlists to match the queue in the database.

    :return:
    """
    utils.dry_run_prompt()

    queue = database_reads.get_video_queue()
    playlists = database_reads.get_all_created_playlists()
    print(f'{len(queue)} videos to process')

    for playlist in playlists:
        print(f'Updating [{playlist["playlist_id"]}]')
        _update_playlist(playlist)


def _update_playlist(playlist):
    """
    Compares the contents of the live playlists and the database queue and performs the necessary updates.

    :param playlist:
    :return:
    """

    # Read the queue from the DB and the live playlist
    queue = database_reads.get_video_queue_for_range(playlist['start_date'], playlist['end_date'])
    live_playlist = _get_live_playlist(playlist['playlist_id'])

    # Compare the queue with the current live playlist
    queue_video_ids = set([v['video_id'] for v in queue])
    live_video_ids = set([v['video_id'] for v in live_playlist])
    delete_ids = live_video_ids - queue_video_ids
    insert_ids = queue_video_ids - live_video_ids

    # Delete videos that should no longer be in the live playlist
    _delete_videos(playlist['playlist_id'], delete_ids)

    # Insert missing videos into the playlist
    print(f'{len(insert_ids)} videos to insert')
    _insert_videos_to_playlist(playlist['playlist_id'], queue, insert_ids)

    print(f'Checking for duplicates...')
    _remove_duplicates(playlist['playlist_id'])

    # Diff the newly updated playlists to check for correct order
    live_playlist = _get_live_playlist(playlist['playlist_id'])
    max_len = min(len(live_playlist), len(queue))
    diff = abs(len(live_playlist) - len(queue))
    if diff != 0:
        print(f'Queue and playlist are not the same length! They differ by {diff}.')

    for i in range(max_len):
        live_vid = live_playlist[i] or {}
        queue_vid = queue[i] or {}
        if live_vid["video_id"] != queue_vid["video_id"]:
            print(f'Diff found: [{live_vid["video_id"]}] / {queue_vid["video_id"]} / {queue_vid["order"]}')
            # TODO: Resolve edge cases that cause diffs


def _get_live_playlist(playlist_id):
    """
    Gets the current live playlist.

    :param playlist_id:
    :return:
    """
    live_playlist = operations.list_videos_in_playlist(playlist_id)
    video_objects = []

    for video in live_playlist:
        video_id = video.get('snippet').get('resourceId').get('videoId')
        publish_date = video.get('snippet').get('publishedAt') or video.get('contentDetails').get(
            'videoPublishedAt')
        video_objects.append({'video_id': video_id, 'date': publish_date})

    return video_objects


def _delete_videos(playlist_id, delete_ids):
    """
    Delete the given list of videos out of the playlist

    :param playlist_id:
    :param delete_ids:
    :return:
    """

    print(f'{len(delete_ids)} videos to delete')
    for vid in delete_ids:
        if not _counter_ok():
            break

        if utils.dry_run:
            print(f'[{vid}] / Delete')
        else:
            operations.delete_video_from_playlist(playlist_id, vid)


def _insert_videos_to_playlist(playlist_id, queue, insert_ids):
    """
    Insert missing videos in the live playlist

    :param playlist_id:
    :param queue:
    :param insert_ids:
    :return:
    """

    live_playlist = _get_live_playlist(playlist_id)
    order_map = {v['video_id']: v['order'] for v in queue}
    insert_videos = [v for v in queue if v['video_id'] in insert_ids]
    insert_videos.sort(key=lambda v: v['order'])

    # Iterate in reverse chronological order
    # Most of the time, we'll be adding new videos to the "bottom" of the list
    i = len(live_playlist) - 1
    while i >= 0:
        if not live_playlist:
            break
        if not _counter_ok():
            break

        video_id = live_playlist[i]['video_id']
        live_playlist_order = order_map[video_id]
        current_vid = insert_videos[-1]
        if live_playlist_order < current_vid['order']:
            if utils.dry_run:
                print(f'[{current_vid["video_id"]}] / {current_vid["order"]} / Insert at {i}')
            else:
                operations.insert_video(playlist_id, video_id, i)
            insert_videos.pop()
            break
        i -= 1

    # The remaining videos go earlier in the queue, so we insert them at the top
    _insert_queue_at_top(playlist_id, insert_videos)


def _insert_queue_at_top(playlist_id, queue):
    """
    Inserts from the queue into the top of the playlist

    :param playlist_id:
    :param queue:
    :return:
    """

    queue.sort(key=lambda v: v['order'], reverse=True)
    for video in queue:
        print(f'Insertion point not found for {video["video_id"]} / {video["order"]}, adding to top of playlist')
        if not _counter_ok():
            break
        operations.insert_video(playlist_id, video['video_id'], 0)


def _remove_duplicates(playlist_id):
    live_playlist = _get_live_playlist(playlist_id)
    live_playlist.sort(key=lambda v: v['video_id'])
    for i in range(len(live_playlist) - 1):
        if live_playlist[i]['video_id'] == live_playlist[i + 1]['video_id']:
            operations.delete_duplicate_videos_from_playlist(playlist_id, live_playlist[i]['video_id'])


def _counter_ok():
    """
    Checks whether the we've hit the global limit set at the top of the file

    :return:
    """

    global counter

    counter += 1
    if counter > LIMIT:
        confirm = input(f'Limit hit. Continue? ')
        if confirm == 'y':
            counter = 0
            return True
        else:
            return False

    return True
