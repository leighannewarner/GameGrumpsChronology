import unittest
import playlist_config
import playlists_utils as utils
import playlist_operations as operations
import youtube_reads as youtube_read
import playlist_process_uploads as process_uploads
import json
from unittest.mock import patch


@patch('database_reads.get_video_row')
@patch('database_mutations.insert_videos')
@patch('youtube_reads.list_videos_in_playlist')
@patch('playlists_utils.authorize')
@patch('playlists_utils.dry_run_prompt')
class PlaylistOperationsTest(unittest.TestCase):
    NUM_UPLOADS_PLAYLISTS = len(playlist_config.UPLOADS_PLAYLISTS)

    def test_process_uploads_filters_processed(self, dry_run_prompt, authorize, list_videos_in_playlist, insert_videos,
                                               get_video_row):
        utils.dry_run = False
        get_video_row.return_value = ['abc123', None, 'ghi789', 'abc123', 'def456', None]
        video_response = [
            json.loads(
                '''{"snippet": {"resourceId": {"videoId": "abc123"}},
                "contentDetails": {"videoPublishedAt": "2012-06-20T22:45:24.000Z"}}'''),
            json.loads(
                '''{"snippet": {"resourceId": {"videoId": "def456"}},
                "contentDetails": {"videoPublishedAt": "2012-07-20T22:45:24.000Z"}}'''),
            json.loads(
                '''{"snippet": {"resourceId": {"videoId": "ghi789"}},
                "contentDetails": {"videoPublishedAt": "2012-08-20T22:45:24.000Z"}}'''),
        ]
        list_videos_in_playlist.return_value = video_response

        process_uploads.process()

        dry_run_prompt.assert_called_once()
        self.assertEqual(list_videos_in_playlist.call_count, len(playlist_config.UPLOADS_PLAYLISTS))
        authorize.assert_called()
        self.assertEqual(get_video_row.call_count, 3 * self.NUM_UPLOADS_PLAYLISTS)
        self.assertEqual(insert_videos.call_count, 1)

    def test_process_uploads_dry_run(self, dry_run_prompt, authorize, list_videos_in_playlist, insert_videos,
                                     get_video_row):
        utils.dry_run = True
        get_video_row.return_value = None
        video_response = [
            json.loads(
                '''{"snippet": {"resourceId": {"videoId": "abc123"}},
                "contentDetails": {"videoPublishedAt": "2012-06-20T22:45:24.000Z"}}'''),
            json.loads(
                '''{"snippet": {"resourceId": {"videoId": "def456"}},
                "contentDetails": {"videoPublishedAt": "2012-07-20T22:45:24.000Z"}}'''),
            json.loads(
                '''{"snippet": {"resourceId": {"videoId": "ghi789"}},
                "contentDetails": {"videoPublishedAt": "2012-08-20T22:45:24.000Z"}}'''),
        ]
        list_videos_in_playlist.return_value = video_response

        process_uploads.process()

        dry_run_prompt.assert_called_once()
        self.assertEqual(list_videos_in_playlist.call_count, self.NUM_UPLOADS_PLAYLISTS)
        authorize.assert_called()
        self.assertEqual(get_video_row.call_count, 3 * self.NUM_UPLOADS_PLAYLISTS)
        insert_videos.assert_not_called()

    def test_process_uploads_inserts_video(self, dry_run_prompt, authorize, list_videos_in_playlist, insert_videos,
                                           get_video_row):
        utils.dry_run = False
        get_video_row.return_value = None
        video_response = [
            json.loads(
                '''{"snippet": {"resourceId": {"videoId": "abc123"}},
                "contentDetails": {"videoPublishedAt": "2012-06-20T22:45:24.000Z"}}'''),
        ]
        list_videos_in_playlist.return_value = video_response

        process_uploads.process()

        insert_videos.assert_called_with([{'video_id': 'abc123', 'date': '2012-06-20T22:45:24.000Z',
                                           'playlist_order': '2012-06-20T22:45:24.000Z~0000'},
                                          {'video_id': 'abc123', 'date': '2012-06-20T22:45:24.000Z',
                                           'playlist_order': '2012-06-20T22:45:24.000Z~0000'}])


if __name__ == '__main__':
    unittest.main()
