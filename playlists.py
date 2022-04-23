import playlist_operations as operations
import playlist_process_uploads as process_uploads
import playlist_insert_videos
import playlists_utils as utils

from dotenv import load_dotenv

load_dotenv()

youtube_client = None


def main():
    done = False
    while not done:
        utils.reset_dry_run_prompt()
        print('[0] Create playlists')
        print('[1] Process playlists')
        print('[2] Insert videos')
        print('[3] Update playlists')
        input_value = input('Option: ')

        if input_value == '0':
            create_playlists()
        elif input_value == '1':
            update_playlists()
        elif input_value == '2':
            insert_videos()
        elif input_value == '3':
            update_playlists()
            insert_videos()
        else:
            done = True
        print('')

    print('\nDone.')


def create_playlists():
    """
    Creates missing playlists based on the CREATED_PLAYLISTS config option in playlist_config.py.

    :return:
    """

    operations.create_playlists()


def update_playlists():
    """
    Process channel uploads to determine their appropriate position and playlist.

    :return:
    """

    process_uploads.process()


def insert_videos():
    """
    Insert videos into the playlists.

    :return:
    """
    playlist_insert_videos.insert()


if __name__ == "__main__":
    main()
