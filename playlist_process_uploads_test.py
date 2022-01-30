from unittest.mock import patch
import database_mutations
import database_reads
import json
import playlist_config as config
import playlist_process_uploads as process_uploads
import playlists_utils as utils
import unittest
import youtube_reads


class PlaylistOperationsTest(unittest.TestCase):

    def setUp(self):
        self.addCleanup(patch.stopall)

        patch.object(database_reads, 'get_video_row').start()
        patch.object(database_reads, 'get_existing_playlist_row').start()

        patch.object(database_mutations, 'insert_videos').start()
        patch.object(database_mutations, 'insert_existing_playlists').start()

        patch.object(youtube_reads, 'list_videos_in_playlist').start()
        patch.object(youtube_reads, 'list_playlists_on_channel').start()

        patch.object(utils, 'authorize').start()
        patch.object(utils, 'dry_run_prompt').start()

        config.UPLOADS_PLAYLISTS = ['upload_playlist']

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
        youtube_reads.list_videos_in_playlist.return_value = video_response

        playlist_response = [json.loads('''{"id": "pl1"}'''), json.loads('''{"id": "pl2"}''')]
        youtube_reads.list_playlists_on_channel.return_value = playlist_response

    def tearDown(self):
        patch.stopall()

    def test_process_uploads_dry_run(self):
        utils.dry_run = True
        database_reads.get_video_row.return_value = None
        database_reads.get_existing_playlist_row.return_value = None

        process_uploads.process()

        utils.dry_run_prompt.assert_called_once()
        utils.authorize.assert_called()

        self.assertEqual(youtube_reads.list_videos_in_playlist.call_count, 1)
        self.assertEqual(youtube_reads.list_playlists_on_channel.call_count, 1)

        self.assertEqual(database_reads.get_video_row.call_count, 3)
        self.assertEqual(database_reads.get_existing_playlist_row.call_count, 2)

        database_mutations.insert_videos.assert_not_called()
        database_mutations.insert_existing_playlists.assert_not_called()

    def test_process_uploads_filters_processed(self):
        utils.dry_run = False
        database_reads.get_video_row.side_effect = ['abc123', None, 'ghi789', 'abc123', 'def456', None]
        database_reads.get_existing_playlist_row.side_effect = ['pl1', None]

        process_uploads.process()

        utils.dry_run_prompt.assert_called_once()
        utils.authorize.assert_called()

        self.assertEqual(youtube_reads.list_videos_in_playlist.call_count, 1)
        self.assertEqual(youtube_reads.list_playlists_on_channel.call_count, 1)

        self.assertEqual(database_reads.get_video_row.call_count, 3)
        self.assertEqual(database_reads.get_existing_playlist_row.call_count, 2)

        self.assertEqual(database_mutations.insert_videos.call_count, 1)
        self.assertEqual(database_mutations.insert_existing_playlists.call_count, 1)

    def test_process_uploads_inserts_video(self):
        utils.dry_run = False
        database_reads.get_video_row.return_value = None
        database_reads.get_existing_playlist_row.return_value = 'pl1'

        process_uploads.process()

        database_mutations.insert_videos.assert_called_with([{'video_id': 'abc123', 'date': '2012-06-20T22:45:24.000Z',
                                                              'playlist_order': '2012-06-20T22:45:24.000Z~0000'},
                                                             {'video_id': 'def456', 'date': '2012-07-20T22:45:24.000Z',
                                                              'playlist_order': '2012-07-20T22:45:24.000Z~0000'},
                                                             {'video_id': 'ghi789', 'date': '2012-08-20T22:45:24.000Z',
                                                              'playlist_order': '2012-08-20T22:45:24.000Z~0000'}])
        database_mutations.insert_existing_playlists.assert_called_with([])

    def test_process_uploads_insert_existing_playlists(self):
        utils.dry_run = False
        database_reads.get_video_row.return_value = 'abc123'
        database_reads.get_existing_playlist_row.side_effect = ['pl1', None]

        process_uploads.process()

        database_mutations.insert_videos.assert_called_with([])
        database_mutations.insert_existing_playlists.assert_called_with([{'playlist_id': 'pl2'}])


if __name__ == '__main__':
    unittest.main()
