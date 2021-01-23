import database
import googleapiclient.errors
import os
import time
import youtube

from dotenv import load_dotenv

load_dotenv()

youtube_client = None


def main():
    while True:
        print('[0] Generate playlist in .env')
        print('[1] Insert videos')
        print('[2] Generate all playlists')
        input_value = input('Option: ')

        if input_value == '0':
            generate_playlist()
        elif input_value == '1':
            insert_all_videos()
        elif input_value == '2':
            update_all_playlists()
        else:
            break

    print('Done.')


def update_all_playlists():
    playlists = database.get_created_playlists()
    for playlist in playlists:
        update_playlist(playlist[0], playlist[1], playlist[2])


def generate_playlist():
    update_playlist(create_playlist(), os.getenv('START_DATE'), os.getenv('END_DATE'))


def update_playlist(playlist_id, start_date, end_date):
    videos_in_range = database.get_videos_for_range(start_date, end_date)

    video_ids = []
    for video in videos_in_range:
        video_id = video['video_id']
        created_playlist_id = video['created_playlist_id']
        playlist_order = video['playlist_order']

        # Skip processing if it already is in there
        if created_playlist_id is not None:
            continue

        print(f'Queueing video [{video_id}]')
        video_ids.append({'video_id': video_id, 'playlist_order': playlist_order})
    store_videos_for_playlist(playlist_id, video_ids)


def create_playlist():
    playlist_id = database.get_created_playlist_id(os.getenv('START_DATE'), os.getenv('END_DATE'))
    if playlist_id is not None:
        print(f'Using existing playlist [{playlist_id}]')
        return playlist_id
    authorize()
    playlist_id = youtube.create_playlist(youtube_client=youtube_client, title=os.getenv('PLAYLIST_TITLE'),
                                          description=os.getenv('PLAYLIST_DESCRIPTION'), tags=['Game Grumps'])
    database.store_created_playlist(playlist_id, os.getenv('START_DATE'), os.getenv('END_DATE'))
    return playlist_id


def store_videos_for_playlist(playlist_id, video_ids):
    # Video_ids is a tuple containing the id and the creation date
    id_list = [{'video_id': video_id['video_id'], 'created_playlist_id': playlist_id, 'processed': False}
               for video_id in video_ids]
    database.store_videos_to_add(id_list)


def insert_all_videos():
    limit = int(input("Limit: "))
    dry_run = (limit == 0)
    if not dry_run:
        authorize()
    queue = database.get_video_queue()
    print(f'{len(queue)} videos to process')

    counter = 0
    for row in queue:
        if not dry_run:
            print('.', end='', sep='')
            time.sleep(0.5)

        video_id = row['video_id']
        playlist_id = row['playlist_id']
        playlist_order = row['order']
        playlist = database.get_videos_in_created_playlist(playlist_id)

        # Search playlist newest to oldest to find insertion point
        index = len(playlist)
        for item in reversed(playlist):
            index -= 1
            if item['playlist_order'] <= playlist_order:
                break
        playlist.insert(index, (item['playlist_order'], video_id))

        if not dry_run:
            try:
                counter += 1
                youtube.insert_video_into_playlist(youtube_client, video_id, playlist_id, index)
                database.mark_video_processed(video_id)
            except googleapiclient.errors.HttpError as err:
                code = err.resp.status
                if code == 404:
                    print(f'\n[{code}] Video [{video_id}] not found, it may be private')
                    print(err)
                    database.mark_video_processed(video_id)
                else:
                    raise err
        if dry_run:
            print(f'{video_id} / {playlist_order}')
        elif limit <= counter:
            break
    print('')


# UTILS ###############################################################################################################
def authorize():
    global youtube_client

    if youtube_client is None:
        youtube_client = youtube.get_youtube_client()


if __name__ == "__main__":
    main()
