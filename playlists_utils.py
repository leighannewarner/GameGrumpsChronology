import youtube

youtube_client = None


def authorize():
    """
    Retrieves a youtube client, if one hasn't been created already.

    :return:
    """
    global youtube_client

    if youtube_client is None:
        youtube_client = youtube.get_youtube_client()
