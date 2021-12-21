import database_utils
import unittest
from unittest.mock import patch, Mock


class DatabaseUtilsTest(unittest.TestCase):

    def test_order_string(self):
        """
        Test the order string function
        """
        self.assertEqual(database_utils.get_order_string("2012-01-00T12:00:00Z", 0), "2012-01-00T12:00:00Z~0000")

    @patch('sqlite3.connect')
    def test_execute(self, connect):
        """
        Test execution of a query
        """

        expected_result = ['result 1', 'result 2']
        connect_mock = Mock()
        cursor_mock = Mock()
        connect.return_value = connect_mock
        connect_mock.cursor.return_value = cursor_mock
        cursor_mock.fetchall.return_value = expected_result

        query = 'a test query'
        values = {'value': 'a value'}

        actual_result = database_utils.execute(query, values)

        connect.assert_called_once_with('playlists.db')
        connect_mock.commit.assert_called_once()
        connect_mock.close.assert_called_once()

        cursor_mock.execute.assert_called_once_with(query, values)

        self.assertEqual(actual_result, expected_result)

    @patch('sqlite3.connect')
    def test_execute_one(self, connect):
        """
        Test execution of a query, then retrieves the first result
        """

        expected_result = ['result 1', 'result 2']
        connect_mock = Mock()
        cursor_mock = Mock()
        connect.return_value = connect_mock
        connect_mock.cursor.return_value = cursor_mock
        cursor_mock.fetchall.return_value = expected_result

        query = 'a test query'
        values = {'value': 'a value'}

        actual_result = database_utils.execute_one(query, values)

        connect.assert_called_once_with('playlists.db')
        connect_mock.commit.assert_called_once()
        connect_mock.close.assert_called_once()

        cursor_mock.execute.assert_called_once_with(query, values)

        self.assertEqual(actual_result, expected_result[0])

    @patch('sqlite3.connect')
    def test_execute_many(self, connect):
        """
        Test execution of many queries through the sqlite3.execute_many function
        """

        connect_mock = Mock()
        cursor_mock = Mock()
        connect.return_value = connect_mock
        connect_mock.cursor.return_value = cursor_mock

        query = 'a test query'
        values = {'value': 'a value'}

        database_utils.execute_many(query, values)

        connect.assert_called_once_with('playlists.db')
        connect_mock.commit.assert_called_once()
        connect_mock.close.assert_called_once()

        cursor_mock.executemany.assert_called_once_with(query, values)


if __name__ == '__main__':
    unittest.main()
