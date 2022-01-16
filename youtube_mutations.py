import youtube_utils as utils


def create_playlist(youtube_client=None, title='', description='', tags=[]):
    """
    Creates a playlist on the authorized YouTube account.

    :param youtube_client: An authorized youtube client
    :param title: The title of the playlist
    :param description: The description of the playlist
    :param tags: Playlist tags
    :return:
    """
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
