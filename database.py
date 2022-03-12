import database_utils as utils
import database_tables as tables
import database_mutations as mutate
import database_reads as read


def main():
    done = False

    while not done:
        print('[0] Delete database')
        print('[1] Create database')
        print('[2] Backup database')
        print('===================')
        print('[3] Find video')
        print('[4] Find playlist')
        print('[5] Print created playlists')
        print('[6] Print queue')
        print('===================')
        print('[7] Reset video')
        print('[8] Reset existing playlist videos')
        print('[9] Reset created playlist videos')
        input_value = input('\nOption: ')

        if input_value == '0':
            delete_database()
        elif input_value == '1':
            create_database()
        elif input_value == '2':
            backup_database()
        elif input_value == '3':
            find_video()
        elif input_value == '4':
            find_playlist()
        elif input_value == '5':
            print_created_playlist_table()
        elif input_value == '6':
            print_queue()
        elif input_value == '7':
            reset_video()
        elif input_value == '8':
            reset_existing_playlist()
        elif input_value == '9':
            reset_created_playlist()
        else:
            done = True
        print('')

    print('Done.')


# TABLE MANAGEMENT ###################################################################################################
def delete_database():
    """
    Drops the entire database.

    :return:
    """

    confirm = input('Delete database y/n: ')
    if confirm == 'y':
        tables.drop_database()
        print('Database deleted')


def create_database():
    """
    Initializes a new database.

    :return:
    """

    tables.init()
    print('Database created')


def backup_database():
    """
    Creates a new database backup, prefixed by the current date.

    :return:
    """

    tables.backup()
    print('Backup created')


# PRINT ###############################################################################################################
def find_video():
    """
    Prints the contents of a video row.

    :return:
    """

    video_id = input('Video ID: ')
    print(read.get_video_row(video_id))


def find_playlist():
    """
    Prints the contents of an existing playlist row.

    :return:
    """

    playlist_id = input('Playlist ID: ')
    print(read.get_existing_playlist_row(playlist_id))


def print_created_playlist_table():
    """
    Prints the created playlist table.

    :return:
    """

    for row in utils.execute('''SELECT * FROM created_playlists'''):
        print(row)


def print_queue():
    """
    Prints a list of unprocessed videos.

    :return:
    """

    for row in read.get_video_queue():
        print(row)


# DATA MANAGEMENT #####################################################################################################
def reset_video():
    """
    Resets a single video.

    :return:
    """

    video_id = input('Video ID: ')
    mutate.mark_video_unprocessed(video_id)
    mutate.remove_video_from_created_playlist(video_id)


def reset_existing_playlist():
    """
    Resets all videos in an existing playlist.

    :return:
    """

    playlist_id = input('Playlist ID: ')
    mutate.mark_playlist_unprocessed(playlist_id)
    mutate.remove_playlist_from_created_playlist(playlist_id)


def reset_created_playlist():
    """
    Resets all videos in a created playlist.

    :return:
    """

    playlist_id = input('Playlist ID: ')
    mutate.mark_created_playlist_unprocessed(playlist_id)
    mutate.remove_all_from_created_playlist(playlist_id)


if __name__ == "__main__":
    main()
