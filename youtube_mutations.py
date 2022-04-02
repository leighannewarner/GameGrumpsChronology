import youtube_utils as utils


def create_playlist(youtube_client=None, title='', description='', tags=None):
    """
    Creates a playlist on the authorized YouTube account.

    :param youtube_client: An authorized youtube client
    :param title: The title of the playlist
    :param description: The description of the playlist
    :param tags: Playlist tags
    :return:
    """
    if tags is None:
        tags = []
    request = youtube_client.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    response = utils.execute_request(request)
    return response.get('id')


def delete_video_from_playlist(youtube_client=None, video_id='', playlist_id=''):
    get_request = youtube_client.playlistItems().list(
        part="id",
        playlistId=playlist_id,
        videoId=video_id
    )
    result = utils.execute_request(get_request)

    for item in result.get('items'):
        update_request = youtube_client.playlistItems().delete(id=item.get('id'))
        utils.execute_request(update_request)


def delete_duplicate_videos_from_playlist(youtube_client=None, video_id='', playlist_id=''):
    get_request = youtube_client.playlistItems().list(
        part="id",
        playlistId=playlist_id,
        videoId=video_id
    )
    result = utils.execute_request(get_request)

    # Remove all but the first item
    items = result.get('items')
    for i in range(1, len(items)):
        update_request = youtube_client.playlistItems().delete(id=items[i].get('id'))
        utils.execute_request(update_request)


def insert_video_into_playlist(youtube_client=None, video_id='', playlist_id='', position=0):
    request = youtube_client.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "position": position,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        })
    utils.execute_request(request)


def update_video_in_playlist(youtube_client=None, video_id='', playlist_id='', position=0):
    get_request = youtube_client.playlistItems().list(
        part="id",
        playlistId=playlist_id,
        videoId=video_id
    )
    result = utils.execute_request(get_request)

    for item in result.get('items'):
        request = youtube_client.playlistItems().update(
            part="snippet",
            body={
                "id": item.get('id'),
                "snippet": {
                    "playlistId": playlist_id,
                    "position": position,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            })
        utils.execute_request(request)

