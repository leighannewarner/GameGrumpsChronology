from dotenv import load_dotenv
import os
import sqlite3
import time

load_dotenv()

DATABASE_NAME = os.getenv('DATABASE_NAME')
RETRY_LIMIT = int(os.getenv('RETRY_LIMIT'))


def get_order_string(date, num):
    """
    Get a formatted order string based on a date and an index. These strings are sortable to provide playlist order.

    :param date:
    :param num:
    :return:
    """

    return f'{date}~{"{:0>4d}".format(num)}'


def execute(query, values=None):
    """
    Execute the given query with the given values, up to the number of retries specified in the dotenv file. Returns a
    list of all rows.

    :param query:
    :param values:
    :return:
    """

    if values is None:
        values = {}

    def func():
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute(query, values)
        rows = c.fetchall()
        conn.commit()
        conn.close()
        return rows if rows else []

    result = _safely_execute(func)
    return result if result else []


def execute_one(query, values=None):
    """
    Execute the given query with the given values, up to the number of retries specified in the dotenv file, then
    retrieves the first result.

    :param query:
    :param values:
    :return:
    """

    rows = execute(query, values)
    row = rows[0] if rows else None
    return row


def execute_many(query, values=None):
    """
    Execute the given query using "executemany" cursor function.

    :param query:
    :param values:
    :return:
    """

    if values is None:
        values = {}

    def func():
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.executemany(query, values)
        conn.commit()
        conn.close()

    _safely_execute(func)


def _safely_execute(func):
    """
    Handle errors for a function containing a sqlite3 database operation.

    :param func:
    :return:
    """

    attempts = 0
    while attempts < RETRY_LIMIT:
        try:
            return func()
        except sqlite3.OperationalError as err:
            attempts += 1
            if attempts >= RETRY_LIMIT:
                print(err)
                break
        time.sleep(0.5)
