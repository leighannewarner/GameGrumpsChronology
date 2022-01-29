import youtube_utils as utils


def list_videos_in_playlist(youtube_client, playlist_id):
    """
    Lists all the videos in a given playlist.

    :param youtube_client: An authorized YouTube client
    :param playlist_id:
    :return:
    """
    pagination_token = None
    videos = []

    while True:
        print('.', end='', sep='')

        response = _list_videos_in_playlist_internal(youtube_client, playlist_id, pagination_token)
        if not response:
            break
        videos.extend(response.get('items'))
        pagination_token = response.get('nextPageToken')
        if not pagination_token:
            break

    return videos


def _list_videos_in_playlist_internal(youtube_client, playlist_id, pagination_token):
    """
    Perform list request to the YouTube API

    :param youtube_client:
    :param playlist_id:
    :param pagination_token:
    :return:
    """

    request = youtube_client.playlistItems().list(
        part=['id', 'snippet', 'contentDetails'],
        maxResults=50,
        playlistId=playlist_id,
        pageToken=pagination_token
    )
    response = utils.execute_request(request)
    return response
