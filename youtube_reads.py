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

    print('\n')
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


def list_playlists_on_channel(youtube_client, channel_id):
    """
    List playlists on a given Youtube channel.

    :param youtube_client:
    :param channel_id:
    :return:
    """

    pagination_token = None
    playlists = []

    while True:
        print('.', end='', sep='')

        response = _list_playlists_on_channel_internal(youtube_client, channel_id, pagination_token)
        playlists.extend(response.get('items'))
        pagination_token = response.get('nextPageToken')
        if not pagination_token:
            break

    return playlists


def _list_playlists_on_channel_internal(youtube_client, channel_id, pagination_token):
    """
    Perform list request to the YouTube API

    :param youtube_client:
    :param channel_id:
    :param pagination_token:
    :return:
    """

    request = youtube_client.playlists().list(
        part=['id', 'snippet'],
        maxResults=50,
        channelId=channel_id,
        pageToken=pagination_token
    )
    return utils.execute_request(request)
