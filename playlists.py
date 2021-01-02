import database
import googleapiclient.errors
import pyrfc3339
import os
import time
import youtube

from dotenv import load_dotenv

load_dotenv()

youtube_client = None


def main():
    value = input("Reset queue y/n:\n")
    if value == 'y':
        database.mark_all_videos_unprocessed()

    value = input("Generate playlist y/n:\n")
    if value == 'y':
        generate_playlist()

    value = input("Process video queue y/n:\n")
    if value == 'y':
        insert_all_videos()

    value = input("Dump queue y/n:\n")
    if value == 'y':
        database.print_queue()

    value = input("Print created playlists y/n:\n")
    if value == 'y':
        database.print_created_playlist_table()


def generate_playlist():
    authorize()
    playlist_id = create_playlist()
    content_items = youtube.list_all_videos_for_range(youtube_client=youtube_client,
                                                      channel_id=os.getenv('CHANNEL_ID'),
                                                      start_date=os.getenv('START_DATE'),
                                                      end_date=os.getenv('END_DATE'))
    video_ids = []
    processed_playlists = set()
    for item in content_items:
        print(item.get('id').get('videoId'))

        item_id = item.get('id')
        video_id = item_id.get('videoId')

        # Skip processing if it already is in there
        video_row = database.get_video_from_queue(video_id)
        if video_row is not None:
            print(f'Video [{video_row[0]}] already processed')
            continue

        # If the video is in a playlist and the playlist isn't one we skip, get all the items in that playlist
        video_playlist = database.get_video_in_playlist(video_id)
        if video_playlist is not None and video_playlist[1] not in database.SKIP_PLAYLISTS:
            if video_playlist[1] not in processed_playlists:
                print(f'Processing playlist [{video_playlist[1]}]')
                processed_playlists.add(video_playlist[1])
                maybe_log_playlist_out_of_range(item_id.get('videoId'))
                playlist_videos = list_all_videos_in_playlist(video_playlist[1])
                video_ids.extend(playlist_videos)
            else:
                print(f'Skipping playlist [{video_playlist[1]}]')
        else:
            print(f'Queueing video [{video_id}]')
            date = item.get('snippet').get('publishedAt')
            video_ids.append((video_id, get_order_string(date, 0)))
    store_videos_for_playlist(playlist_id, video_ids)


def create_playlist():
    playlist_row = database.get_created_playlist(os.getenv('START_DATE'), os.getenv('END_DATE'))
    if playlist_row is not None:
        print(f'Using existing playlist [{playlist_row[0]}]')
        return playlist_row[0]
    playlist_id = youtube.create_playlist(youtube_client=youtube_client, title=os.getenv('PLAYLIST_TITLE'),
                                          description=os.getenv('PLAYLIST_DESCRIPTION'), tags=['Game Grumps'])
    database.store_created_playlist(playlist_id, os.getenv('START_DATE'), os.getenv('END_DATE'))
    return playlist_id


def list_all_videos_in_playlist(playlist_id):
    authorize()
    response_items = youtube.list_all_videos_in_playlist(youtube_client, playlist_id)
    created_date = database.get_existing_playlist(playlist_id)[1]

    videos = []
    counter = 0
    for result in response_items:
        video_id = result.get('snippet').get('resourceId').get('videoId')
        videos.append((video_id, get_order_string(created_date, counter)))
        counter += 1
    return videos


def store_videos_for_playlist(playlist_id, video_ids):
    # Video_ids is a tuple containing the id and the creation date
    id_list = [(video_id[0], playlist_id, video_id[1], False) for video_id in video_ids]
    database.store_videos_to_add(id_list)


def insert_all_videos():
    limit = int(input("Limit:\n"))
    dry_run = (limit == 0)
    print(limit == 0)
    if not dry_run:
        authorize()
    queue = database.get_video_queue()

    for row in queue:
        if not dry_run:
            print('.', end='', sep='')
            time.sleep(1)

        video_id = row[0]
        playlist_id = row[1]
        playlist_order = row[2]
        playlist = database.get_video_playlist(playlist_id)

        index = len(playlist)
        for date in reversed(playlist):
            index -= 1
            if date[0] <= playlist_order:
                break

        playlist.insert(index, (date[0], video_id))
        if not dry_run:
            try:
                youtube.insert_video_into_playlist(youtube_client, video_id, playlist_id, index)
            except googleapiclient.errors.HttpError as err:
                code = err.resp.status
                if code == 404:
                    print(f'\n[{code}] Video [{video_id}] not found, it may be private')
                    print(err)
                else:
                    raise err
            database.mark_video_processed(video_id)
    if dry_run:
        print(playlist)
    print('')


# UTILS ###############################################################################################################
def maybe_log_playlist_out_of_range(video_id):
    video = database.get_video_in_playlist(video_id)
    if video is None:
        return

    playlist = database.get_existing_playlist(video[1])
    if playlist is None:
        return

    playlist_time = pyrfc3339.parse(playlist[1])
    start_date = pyrfc3339.parse(os.getenv('START_DATE'))
    if playlist_time < start_date:
        print(
            f'Video [{video_id}] is in an old playlist. Consider updating playlist for {playlist_time.isoformat()}')


def get_order_string(date, num):
    return f'{date}~{"{:0>3d}".format(num)}'


def authorize():
    global youtube_client

    if youtube_client is None:
        youtube_client = youtube.get_youtube_client()


if __name__ == "__main__":
    main()
