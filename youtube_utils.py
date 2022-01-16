import googleapiclient.discovery
import google_auth_oauthlib.flow
import os

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CLIENT_SECRETS_FILE = "client_secret.json"


def authorize():
    """
    Authorizes the client to make API calls
    """

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    return flow.run_console()


def get_youtube_client():
    """
    Builds and returns an authorized http client
    """

    return googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=authorize())


def execute_request(request):
    """
    Executes an http request to to the Google API client
    """

    try:
        response = request.execute()
    except googleapiclient.errors.HttpError as err:
        code = err.resp.status
        if code == 403:
            print(f'\n[{code}] Out of quota')
            raise err
        if code == 404:
            print(f'\n[{code}] The item could not be found')
            print(err)
            return None
        else:
            raise err

    return response
