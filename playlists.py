import database
import googleapiclient.errors
import os
import time
import youtube
import sqlite3

from dotenv import load_dotenv

load_dotenv()

youtube_client = None


def main():
    while True:
        print('[0] Update playlists')
        print('[1] Insert videos')
        print('[2] Create playlist')
        input_value = input('Option: ')

        if input_value == '0':
            update_all_playlists()
        elif input_value == '1':
            insert_all_videos()
        elif input_value == '2':
            confirm = input('Create historical y/n: ')
            if confirm == 'y':
                create_playlist('2012-01-00T12:00:00Z', '2013-06-25T17:59:59Z', 'JonTron Era - Game Grumps Chronology')
                create_playlist('2013-06-25T18:00:00Z', '2013-12-31T11:59:59Z', '2013 - Game Grumps Chronology')
                create_playlist('2014-01-00T12:00:00Z', '2014-12-31T11:59:59Z', '2014 - Game Grumps Chronology')
                create_playlist('2015-01-00T12:00:00Z', '2015-12-31T11:59:59Z', '2015 - Game Grumps Chronology')
                create_playlist('2016-01-00T12:00:00Z', '2016-12-31T11:59:59Z', '2016 - Game Grumps Chronology')
                create_playlist('2017-01-00T12:00:00Z', '2017-12-31T11:59:59Z', '2017 - Game Grumps Chronology')
                create_playlist('2018-01-00T12:00:00Z', '2018-12-31T11:59:59Z', '2018 - Game Grumps Chronology')
                create_playlist('2019-01-00T12:00:00Z', '2019-12-31T11:59:59Z', '2019 - Game Grumps Chronology')
                create_playlist('2020-01-00T12:00:00Z', '2020-12-31T11:59:59Z', '2020 - Game Grumps Chronology')

            confirm = input('Create from env y/n: ')
            if confirm == 'y':
                create_playlist_from_env()
        else:
            break

    print('Done.')


def update_all_playlists():
    try:
        database.remove_skipped_playlists()
        database.insert_videos(list_all_uploads())
        database.insert_playlists(list_all_playlists())
    except sqlite3.OperationalError as err:
        print(err)

    for playlist in database.list_existing_playlists():
        try:
            database.update_video_status(list_all_videos_in_playlist(playlist['playlist_id']))
        except sqlite3.OperationalError as err:
            print(f'\nError processing [{playlist["playlist_id"]}]: {err}')

    playlists = database.get_created_playlists()
    for playlist in playlists:
        update_playlist(playlist['id'], playlist['start_date'], playlist['end_date'])


def update_playlist(playlist_id, start_date, end_date):
    videos_in_range = database.get_videos_for_range(start_date, end_date)

    video_ids = []
    for video in videos_in_range:
        video_id = video['video_id']
        created_playlist_id = video['created_playlist_id']
        playlist_order = video['playlist_order']
        processed = video['processed']

        # Skip processing if it already is in there
        if created_playlist_id or processed:
            continue

        print(f'Queueing video [{video_id}]')
        video_ids.append({'video_id': video_id, 'playlist_order': playlist_order})
    store_videos_for_playlist(playlist_id, video_ids)


def create_playlist_from_env():
    create_playlist(os.getenv('START_DATE'), os.getenv('END_DATE'), os.getenv('PLAYLIST_TITLE'))


def create_playlist(start_date, end_date, title):
    playlist_id = database.get_created_playlist_id(start_date, end_date)
    if playlist_id is not None:
        print(f'Using existing playlist [{playlist_id}]')
        return
    authorize()
    playlist_id = youtube.create_playlist(youtube_client=youtube_client, title=title,
                                          description=os.getenv('PLAYLIST_DESCRIPTION'), tags=['Game Grumps'])
    database.store_created_playlist(playlist_id, start_date, end_date)


def store_videos_for_playlist(playlist_id, video_ids):
    # Video_ids is a tuple containing the id and the creation date
    if len(video_ids) == 0:
        return

    id_list = [{'video_id': video_id['video_id'], 'created_playlist_id': playlist_id, 'processed': False}
               for video_id in video_ids]
    database.store_videos_to_add(id_list)


def insert_all_videos():
    limit = 250
    # limit = int(input("Limit: "))
    dry_run = False
    # confirm = input('Dry run y/n: ')
    # dry_run = confirm == 'y'
    authorize()
    queue = database.get_video_queue()
    print(f'{len(queue)} videos to process')

    counter = 0
    for row in queue:
        if not dry_run:
            print('.', end='', sep='')
            time.sleep(0.5)

        if limit <= counter:
            break
        counter += 1

        video_id = row['video_id']
        playlist_id = row['playlist_id']
        playlist_order = row['order']

        try:
            youtube.insert_video_into_playlist(youtube_client, video_id, playlist_id, playlist_order, dry_run)
        except googleapiclient.errors.HttpError as err:
            code = err.resp.status
            if code == 404:
                print(f'\n[{code}] Video [{video_id}] not found, it may be private')
                print(err)
            else:
                raise err
    print('')


# UTILS ###############################################################################################################
def authorize():
    global youtube_client

    if youtube_client is None:
        youtube_client = youtube.get_youtube_client()


def list_all_uploads():
    print(f'Retrieving uploads...')

    authorize()
    response_items = youtube.list_all_videos_in_playlist(youtube_client, os.getenv('UPLOADS_PLAYLIST'))

    items = []
    counter = 0
    for result in response_items:
        publish_date = result.get('contentDetails').get('videoPublishedAt')
        video_id = result.get('snippet').get('resourceId').get('videoId')

        # Skip processing if the video is already processed
        if database.get_video_row(video_id) is None:
            counter += 1
            items.append({
                'video_id': video_id, 'date': publish_date,
                'playlist_order': database.get_order_string(publish_date, 0),
            })

    print(f'Processed {counter} videos')
    return items


def list_all_playlists():
    print(f'Listing playlists...')

    authorize()
    response_items = youtube.list_all_playlists_for_channel(youtube_client, os.getenv('CHANNEL_ID'))

    items = []
    counter = 0
    for result in response_items:
        playlist_id = result.get('id')
        if result.get('id') in database.SKIP_PLAYLISTS:
            continue

        # Skip processing if the playlist is already in the db
        if database.get_existing_playlist_row(playlist_id) is None:
            counter += 1
            items.append({'playlist_id': playlist_id})

    print(f'Processed {counter} playlists')
    return items


def list_all_videos_in_playlist(playlist_id):
    authorize()
    response_items = youtube.list_all_videos_in_playlist(youtube_client, playlist_id)

    items = []
    # Loop through until we find the oldest publish date, this should usually be the first one unless the video
    # is private
    oldest_publish_date = None
    for result in response_items:
        oldest_publish_date = result.get('contentDetails').get('videoPublishedAt')
        if oldest_publish_date is not None:
            break

    index = 0
    for result in response_items:
        if result.get('status') == 'private':
            continue

        video_id = result.get('snippet').get('resourceId').get('videoId')

        # Insert videos in the playlist that are missing. Ex: a video that wasn't uploaded to the grumps channel
        if database.get_video_row(video_id) is None:
            database.insert_videos([{
                'video_id': video_id, 'date': oldest_publish_date,
                'playlist_order': database.get_order_string(oldest_publish_date, index)
            }])

        # Iff the playlist has a split and the video was published after the split date, reset the index and
        # publish date
        video_publish_date = result.get('contentDetails').get('videoPublishedAt')
        split = database.PLAYLIST_SPLITS.get(playlist_id)
        video_after_split = split is not None and video_publish_date is not None and video_publish_date >= split
        if split != oldest_publish_date and video_after_split:
            index = 0
            oldest_publish_date = split

        video_row = database.get_video_row(video_id)

        # Add the video + playlist relationship if it doesn't exist
        if video_row['existing_playlist_id'] is None:
            items.append({
                'video_id': video_id, 'existing_playlist_id': playlist_id, 'date': oldest_publish_date,
                'playlist_order': database.get_order_string(oldest_publish_date, index), 'processed': False
            })
            index += 1
            continue

        # Handles when the playlist "split" has been added or changed
        date_is_different = video_row['playlist_order'] != database.get_order_string(oldest_publish_date, index)
        video_from_playlist = video_row['existing_playlist_id'] == playlist_id
        if date_is_different and video_from_playlist:
            if video_row['processed'] and video_row['created_playlist_id']:
                authorize()
                youtube.delete_video_from_playlist(youtube_client, video_id, video_row['created_playlist_id'])
            items.append({
                'video_id': video_id, 'existing_playlist_id': playlist_id, 'date': oldest_publish_date,
                'created_playlist_id': None, 'playlist_order': database.get_order_string(oldest_publish_date, index),
                'processed': False
            })
        index += 1

    return items


if __name__ == "__main__":
    main()
