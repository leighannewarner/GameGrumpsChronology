import googleapiclient.discovery
import google_auth_oauthlib.flow
import os
import database

from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CLIENT_SECRETS_FILE = "client_secret.json"


# UTILS ###############################################################################################################
def authorize():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    return flow.run_console()


def get_youtube_client():
    return googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=authorize())


# LISTS ###############################################################################################################
def list_all_playlists_for_channel(youtube_client, channel_id):
    pagination_token = None
    playlists = []

    while True:
        print('.', end='', sep='')

        response = list_playlists_for_channel(youtube_client, channel_id, pagination_token)
        playlists.extend(response.get('items'))
        pagination_token = response.get('nextPageToken')
        if not pagination_token:
            break

    return playlists


def list_playlists_for_channel(youtube_client, channel_id, pagination_token):
    request = youtube_client.playlists().list(
        part=['id', 'snippet'],
        maxResults=50,
        channelId=channel_id,
        pageToken=pagination_token
    )
    return request.execute()


def list_all_videos_in_playlist(youtube_client, playlist_id):
    pagination_token = None
    videos = []

    while True:
        print('.', end='', sep='')

        response = list_videos_in_playlist(youtube_client, playlist_id, pagination_token)
        videos.extend(response.get('items'))
        pagination_token = response.get('nextPageToken')
        if not pagination_token:
            break

    return videos


def list_videos_in_playlist(youtube_client, playlist_id, pagination_token):
    response = None
    try:
        request = youtube_client.playlistItems().list(
            part=['id', 'snippet', 'contentDetails'],
            maxResults=50,
            playlistId=playlist_id,
            pageToken=pagination_token
        )
        response = request.execute()
    except googleapiclient.errors.HttpError as err:
        code = err.resp.status
        if code == 403:
            print(f'\n[{code}] Out of quota')
            print(err)
            return response
        else:
            raise err
    return response


def list_all_videos_for_range(youtube_client=None, channel_id=None, start_date=None, end_date=None):
    pagination_token = None
    content = []

    while True:
        print('.', end='', sep='')

        response = list_videos_for_range(youtube_client=youtube_client, channel_id=channel_id, start_date=start_date,
                                         end_date=end_date, pagination_token=pagination_token)
        content.extend(response.get('items'))
        pagination_token = response.get('nextPageToken')
        if not pagination_token:
            break

    print('')
    return content


def list_videos_for_range(youtube_client=None, channel_id=None, start_date=None, end_date=None, pagination_token=None):
    request = youtube_client.search().list(
        part=['id', 'snippet'],
        maxResults=50,
        type=['video'],
        order="date",
        channelId=channel_id,
        publishedAfter=start_date,
        publishedBefore=end_date,
        pageToken=pagination_token
    )
    return request.execute()


def get_videos_in_list(youtube_client=None, video_ids=[]):
    request = youtube_client.videos().list(
        part="id,snippet",
        id=video_ids
    )
    return request.execute()


# MODIFICATION ########################################################################################################
def create_playlist(youtube_client=None, title='', description='', tags=[]):
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
    response = request.execute()
    return response.get('id')


def insert_video_into_playlist(youtube_client, video_id, playlist_id, playlist_order, dry_run):
    index = get_insertion_index(youtube_client, playlist_id, playlist_order)
    if dry_run:
        print(f'INDEX: {video_id} / {index}')
        return
    request = youtube_client.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "position": index,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        })
    request.execute()
    database.mark_video_processed(video_id)


def get_insertion_index(youtube_client, playlist_id, playlist_order):
    pagination_token = None
    counter = 0
    while True:
        response = list_videos_in_playlist(youtube_client, playlist_id, pagination_token)
        if response is None:
            raise Exception('Received None response, you\'re probably out of quota')
        pagination_token = response.get('nextPageToken')

        for result in response.get('items'):
            video_id = result.get('snippet').get('resourceId').get('videoId')
            row = database.get_video_row(video_id)
            if playlist_order <= row['playlist_order']:
                return result.get('snippet').get('position')

        if not pagination_token:
            break

    return None


def delete_video_from_playlist(youtube_client, video_id, playlist_id):
    get_request = youtube_client.playlistItems().list(
        part="id",
        playlistId=playlist_id,
        videoId=video_id
    )
    result = get_request.execute()
    for item in result.get('items'):
        update_request = youtube_client.playlistItems().delete(
            id=item.get('id'))
        update_request.execute()
