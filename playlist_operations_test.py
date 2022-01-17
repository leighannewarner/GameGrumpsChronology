import unittest
import database_reads as database_read
import playlist_config
import playlists_utils as utils
import playlist_operations as operations
from unittest.mock import patch


@patch('database_mutations.insert_created_playlist')
@patch('youtube_mutations.create_playlist', return_value='abc123')
@patch('youtube_utils.authorize')
@patch('playlists_utils.dry_run_prompt')
class PlaylistOperationsTest(unittest.TestCase):

    @patch('database_reads.get_created_playlist_id', return_value=None)
    def test_create_playlists_all_new(self, get_created_playlist_id, dry_run_prompt, authorize, create_playlist,
                                      insert_created_playlist):
        """
        Test the create playlist function. Create all.
        """

        utils.dry_run = False

        operations.create_playlists()

        dry_run_prompt.assert_called_once()
        authorize.assert_called_once()
        self.assertEqual(get_created_playlist_id.call_count, len(playlist_config.CREATED_PLAYLISTS))
        self.assertEqual(create_playlist.call_count, len(playlist_config.CREATED_PLAYLISTS))
        self.assertEqual(insert_created_playlist.call_count, len(playlist_config.CREATED_PLAYLISTS))

    @patch('database_reads.get_created_playlist_id', return_value='abc123')
    def test_create_playlists_all_existing(self, get_created_playlist_id, dry_run_prompt, authorize, create_playlist,
                                           insert_created_playlist):
        """
        Test the create playlist function. Create none.
        """

        utils.dry_run = False

        operations.create_playlists()

        dry_run_prompt.assert_called_once()
        authorize.assert_not_called()
        self.assertEqual(get_created_playlist_id.call_count, len(playlist_config.CREATED_PLAYLISTS))
        create_playlist.assert_not_called()
        insert_created_playlist.assert_not_called()

    @patch('database_reads.get_created_playlist_id', return_value=None)
    def test_create_playlists_one_new(self, get_created_playlist_id, dry_run_prompt, authorize, create_playlist,
                                      insert_created_playlist):
        """
        Test the create playlist function. Create one.
        """

        playlist_ids = ['abc123'] * len(playlist_config.CREATED_PLAYLISTS)
        playlist_ids[0] = None
        print(playlist_ids)
        get_created_playlist_id.side_effect = playlist_ids
        utils.dry_run = False

        operations.create_playlists()

        self.assertEqual(get_created_playlist_id.call_count, len(playlist_config.CREATED_PLAYLISTS))
        create_playlist.assert_called_once()
        insert_created_playlist.assert_called_once()

    @patch('database_reads.get_created_playlist_id', return_value=None)
    def test_create_playlists_dry_run(self, get_created_playlist_id, dry_run_prompt, authorize, create_playlist,
                                      insert_created_playlist):
        """
        Test the create playlist function. Dry run.
        """

        utils.dry_run = True

        operations.create_playlists()

        dry_run_prompt.assert_called_once()
        authorize.assert_not_called()
        get_created_playlist_id.assert_not_called()
        create_playlist.assert_not_called()
        insert_created_playlist.assert_not_called()


if __name__ == '__main__':
    unittest.main()
