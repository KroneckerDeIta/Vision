import sys
import uuid

sys.path.append('../..')

import configuration.settings as settings


""" This module contains the DatabaseTestUtilities class, which is used for checking properties of
the database. """
__author__ = "Thomas Reeve"


####################################################################################################
def sequences_to_dictionary(sequence, index):
    """ Converts a sequence of sequences to a dictionary, where the dictionary key is the entry at
    index in the subsequence, i.e. if index = 1 then:
    [[1, "45"], [2, "46"]]
    becomes
    {
        "45": [1, "45"],
        "46": [2, "46"]
    }
    
    Args:
        sequence: Sequence of sequences.
        index: Index in the subsequence to use as the key in the dictionary.

    Returns:
        The dictionary.
    """
    return {
        sequence[i][index]: sequence[i] for i in range(len(sequence))
    }


####################################################################################################
def check_users_table(database_connection, database_name, tester):
    """ Checks the users table.
    
    Args:
        database_connection (object): The database connector.
        database_name (str): The name of the database we are checking in.
        tester (unittest.TestCase): The unittest.TestCase object.
    """
    cursor = database_connection.cursor()

    cursor.execute("SHOW COLUMNS FROM users")
    columns_info = cursor.fetchall()

    tester.assertEqual(6, len(columns_info))

    columns_dict = sequences_to_dictionary(columns_info, 0)
    
    username_type = 'varchar(%s)' % settings.MAX_USERNAME_LENGTH
    tester.assertSequenceEqual(('username', username_type, 'NO', 'PRI', None, ''),
                               columns_dict["username"])

    password_type = 'varchar(%s)' % settings.PASSWORD_HASH_LENGTH
    tester.assertSequenceEqual(('password', password_type, 'NO', '', None, ''),
                               columns_dict["password"])

    refresh_token_type = 'varchar(%s)' % settings.UUID_LENGTH
    tester.assertSequenceEqual(('refresh_token', refresh_token_type, 'YES', '', None, ''),
                               columns_dict["refresh_token"])

    refresh_token_expiry_type = 'datetime'
    tester.assertSequenceEqual(('refresh_token_expiry', refresh_token_expiry_type, 'YES', '', None,
                                ''),
                               columns_dict["refresh_token_expiry"])

    activated_type = 'tinyint(1)'
    tester.assertSequenceEqual(('activated', activated_type, 'NO', '', '0', ''),
                               columns_dict["activated"])

    theme_type = 'varchar(%s)' % settings.THEME_LENGTH
    tester.assertSequenceEqual(('theme', theme_type, 'NO', '', 'ocean', ''),
                               columns_dict["theme"])

    schema_query = """
        SELECT *
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE `TABLE_SCHEMA` = '%s' AND
              `TABLE_NAME` = 'users'
    """ % (database_name, )
    cursor.execute(schema_query)
    users_schema = cursor.fetchall()

    tester.assertEqual(1, len(users_schema))
    schema_dict = sequences_to_dictionary(users_schema, 6)

    expected_schema = ('def', 'UNITTEST_DATABASE', 'PRIMARY', 'def', 'UNITTEST_DATABASE',
                       'users', 'username', 1, None, None, None, None)
    tester.assertSequenceEqual(expected_schema, schema_dict["username"])


####################################################################################################
def check_access_table(database_connection, database_name, tester):
    """ Checks the access table.
    
    Args:
        database_connection (object): The database connector.
        database_name (str): The name of the database we are checking in.
        tester (unittest.TestCase): The unittest.TestCase object.
    """
    cursor = database_connection.cursor()

    cursor.execute("SHOW COLUMNS FROM access")
    columns_info = cursor.fetchall()

    tester.assertEqual(3, len(columns_info))

    columns_dict = sequences_to_dictionary(columns_info, 0)

    username_type = 'varchar(%s)' % settings.MAX_USERNAME_LENGTH
    tester.assertSequenceEqual(('username', username_type, 'NO', 'PRI', None, ''),
                               columns_dict["username"])

    access_token_type = 'varchar(%s)' % settings.UUID_LENGTH
    tester.assertSequenceEqual(('access_token', access_token_type, 'NO', '', None, ''),
                               columns_dict["access_token"])

    tester.assertSequenceEqual(('access_token_expiry', 'datetime', 'NO', '', None, ''),
                               columns_dict["access_token_expiry"])

    schema_query = """
        SELECT *
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE `TABLE_SCHEMA` = '%s' AND
              `TABLE_NAME` = 'access'
    """ % (database_name, )
    cursor.execute(schema_query)
    access_schema = cursor.fetchall()

    tester.assertEqual(2, len(access_schema))
    schema_dict = sequences_to_dictionary(access_schema, 2)

    expected_primary_schema = ('def', 'UNITTEST_DATABASE', 'PRIMARY', 'def', 'UNITTEST_DATABASE',
                               'access', 'username', 1, None, None, None, None)
    tester.assertSequenceEqual(expected_primary_schema, schema_dict["PRIMARY"])

    expected_username_schema = ('def', 'UNITTEST_DATABASE', 'access_ibfk_1', 'def',
                                'UNITTEST_DATABASE', 'access', 'username', 1, 1,
                                'UNITTEST_DATABASE', 'users', 'username')
    tester.assertSequenceEqual(expected_username_schema, schema_dict["access_ibfk_1"])


####################################################################################################
def check_scores_table(database_connection, database_name, tester, columns):
    """ Checks the scores table.
    
    Args:
        database_connection (object): The database connector.
        database_name (str): The name of the database we are checking in.
        tester (unittest.TestCase): The unittest.TestCase object.
        columns: Sequence of strings that are the column names. 
    """
    cursor = database_connection.cursor()

    cursor.execute("SHOW COLUMNS FROM scores")
    columns_info = cursor.fetchall()

    tester.assertEqual(1 + len(columns), len(columns_info))

    columns_dict = sequences_to_dictionary(columns_info, 0)

    for column in columns:
        tester.assertSequenceEqual((column, 'int(11)', 'NO', '', '-1', ''), columns_dict[column])

    username_type = 'varchar(%s)' % settings.MAX_USERNAME_LENGTH
    tester.assertSequenceEqual(('username', username_type, 'NO', 'PRI', None, ''),
                                columns_dict["username"])

    schema_query = """
        SELECT *
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE `TABLE_SCHEMA` = '%s' AND
              `TABLE_NAME` = 'scores'
    """ % (database_name, )
    cursor.execute(schema_query)
    scores_schema = cursor.fetchall()

    tester.assertEqual(2, len(scores_schema))
    schema_dict = sequences_to_dictionary(scores_schema, 2)

    expected_primary_schema = ('def', 'UNITTEST_DATABASE', 'PRIMARY', 'def', 'UNITTEST_DATABASE',
                               'scores', 'username', 1, None, None, None, None)
    tester.assertSequenceEqual(expected_primary_schema, schema_dict["PRIMARY"])

    expected_foreign_schema = ('def', 'UNITTEST_DATABASE', 'scores_ibfk_1', 'def',
                               'UNITTEST_DATABASE', 'scores', 'username', 1, 1,
                               'UNITTEST_DATABASE', 'users', 'username')
    tester.assertSequenceEqual(expected_foreign_schema, schema_dict["scores_ibfk_1"])


####################################################################################################
def check_is_uuid(tester, string):
    """ Checks the string is a version 4 UUID.

    Args:
        tester (unittest.TestCase): The unittest.TestCase object.
        string (str): The string to check to see if it is a UUID.

    Returns:
        bool: True if a uuid, False otherwise.
    """
    is_uuid = True
    try:
        uuid.UUID(str(string))
    except ValueError:
        is_uuid = False

    tester.assertTrue(is_uuid)


####################################################################################################
def create_tables(database_connector, scores_columns):
    """ Creates all the required tables.

    Args:
        database_connector (DatabaseConnector): Connector used to create the tables.
        scores_columns (list(str)): List of columns to put into the scores table.
    """
    database_connector.create_users_table()
    database_connector.create_scores_table(scores_columns)
    database_connector.create_access_table()


####################################################################################################
def check_data_in_tables(database_connection, tester, expected_data):
    """ Checks the data in the database tables.

    Args:
        database_connection (object): The database connector.
        tester (unittest.TestCase): The unittest.TestCase object.
        expected_data: Dictionary of the data that should be in the table. It will take the form
        {
            "<table-name>": {
                "primary_key": <primary-key-name>,
                "table_data": [
                    {
                        "<column-name>": "<column-data>", ...
                    }, ...
                ]
            }
        }
    """
    cursor = database_connection.cursor()

    for table_name in expected_data:
        primary_key = expected_data[table_name]["primary_key"]
        table_data = expected_data[table_name]["data"]

        cursor.execute("SELECT * FROM " + table_name)
        select_columns = [c[0] for c in cursor.description]

        select_rows = cursor.fetchall()
        select_dict = sequences_to_dictionary(select_rows, select_columns.index(primary_key))

        # Check the number of entries in the expected data is the same as the number of rows in the
        # database table.
        check_number_of_rows_in_table(database_connection, tester, table_name, len(table_data))

        for row_data in table_data:
            database_row = select_dict.get(row_data.get(primary_key))
            for column in row_data:
                value = row_data.get(column)
                tester.assertEqual(value, database_row[select_columns.index(column)])


####################################################################################################
def check_number_of_rows_in_table(database_connection, tester, table_name, expected_number):
    """ Checks there are no rows in the users table.

    Args:
        database_connection (object): The database connector.
        tester (object): The unittest.TestCase object.
        table_name (str): The name of the table.
        expected_number (int): The expected number of rows to be in the users table.
    """
    cursor = database_connection.cursor()

    cursor.execute("SELECT * FROM " + table_name)
    tester.assertEqual(expected_number, len(cursor.fetchall()))


####################################################################################################
def get_access_expiry(database_connection, username):
    """ Gets the access expiry for the user.

    Args:
        database_connection (object): The database connector.
        username (str): The user's username.

    Returns:
        datetime: The access expiry.
    """
    cursor = database_connection.cursor()
    select_command = 'SELECT `access_token_expiry` FROM access WHERE username = %s'
    select_params = (username, )
    cursor.execute(select_command, select_params)


####################################################################################################
def set_access_expiry(database_connection, username, expiry):
    """ Sets the access expiry in the access table.

    Args:
        database_connection (object): The database connector.
        username (str): The user's username.
        expiry (str): The expiry in the format: "%Y-%m-%d %H:%M:%S".
    """
    cursor = database_connection.cursor()
    update_command = 'UPDATE access SET `access_token_expiry` = %s WHERE username = %s'
    update_params = (expiry, username)
    cursor.execute(update_command, update_params)


####################################################################################################
def get_refresh_expiry(database_connection, username):
    """ Gets the refresh expiry for the user.

    Args:
        database_connection (object): The database connector.
        username (str): The user's username.

    Returns:
        datetime: The refresh expiry.
    """
    cursor = database_connection.cursor()
    select_command = 'SELECT `refresh_token_expiry` FROM users WHERE username = %s'
    select_params = (username, )
    cursor.execute(select_command, select_params)


####################################################################################################
def set_refresh_expiry(database_connection, username, expiry):
    """ Sets the refresh expiry in the users table.

    Args:
        database_connection (object): The database connector.
        username (str): The user's username.
        expiry (str): The expiry in the format: "%Y-%m-%d %H:%M:%S".
    """
    cursor = database_connection.cursor()
    update_command = 'UPDATE users SET `refresh_token_expiry` = %s WHERE username = %s'
    update_params = (expiry, username)
    cursor.execute(update_command, update_params)

