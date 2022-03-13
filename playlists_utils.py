import youtube_utils

youtube_client = None
dry_run = None


def authorize():
    """
    Retrieves a youtube client, if one hasn't been created already.

    :return:
    """
    global youtube_client

    if youtube_client is None:
        youtube_client = youtube_utils.get_youtube_client()


def dry_run_prompt():
    global dry_run

    if dry_run is not None:
        return

    confirm = input('Dry Run y/n: ')
    dry_run = confirm == 'y'


def reset_dry_run_prompt():
    global dry_run
    dry_run = None
