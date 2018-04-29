# Test imports.
import utilities

from datetime import datetime
from mock import patch, MagicMock
import MySQLdb
import sys
import unittest

sys.path.append('../..')

# Source imports.
import database.connector as connector
import configuration.settings as settings

""" This module contains the DatabaseConnector class, which is used for interacting with a
database. """
__author__ = "Thomas Reeve"


####################################################################################################
class DatabaseConnectorTests(unittest.TestCase):
    """ Unit tests for the DatabaseConnector class. """
    ################################################################################################
    def setUp(self):
        """ Method run before every test. """
        self.database_name = "UNITTEST_DATABASE"

        self.database_connection = MySQLdb.connect(host=settings.DATABASE_HOST,
                                                   user=settings.DATABASE_USER,
                                                   passwd=settings.DATABASE_PASSWORD)
        self.subject = connector.DatabaseConnector(self.database_connection)

        if self.subject.does_database_exist(self.database_name):
            raise Exception("Database " + self.database_name + " already exists.")

        self.subject.create_database(self.database_name)
        self.subject.use_database(self.database_name)

    ################################################################################################
    def tearDown(self):
        """ Method run after every test. """
        self.subject.drop_database(self.database_name)

    ################################################################################################
    def test_get_database_name(self):
        """ Test getting the database name. """
        self.assertEqual(self.database_name, self.subject.get_current_database())

    ################################################################################################
    def test_does_database_exist(self):
        """ Test does database exist. """
        self.assertTrue(self.subject.does_database_exist(self.database_name))
        self.assertFalse(self.subject.does_database_exist("not_a_database"))

    ################################################################################################
    def test_create_users_table(self):
        """ Test the creation of the users table. """
        self.subject.create_users_table()

        utilities.check_users_table(self.database_connection, self.database_name, self)

    ################################################################################################
    def test_create_access_table(self):
        """ Test the creation of the access table. """
        self.subject.create_users_table()  # Need to add users table for foreign key constraint.
        self.subject.create_access_table()

        utilities.check_users_table(self.database_connection, self.database_name, self)
        utilities.check_access_table(self.database_connection, self.database_name, self)

    ################################################################################################
    def test_create_scores_table(self):
        """ Test the creation of the scores table. """
        self.subject.create_users_table() # Need to add users table for foreign key constraint.
        scores_columns = ["1-1", "1-2", "1-3"]
        self.subject.create_scores_table(scores_columns)

        utilities.check_users_table(self.database_connection, self.database_name, self)
        utilities.check_scores_table(self.database_connection, self.database_name, self,
                                     scores_columns)

    ################################################################################################
    def test_generate_token(self):
        """ Test the generate_token static method in DatabaseConnector. """
        access_token = connector.DatabaseConnector.generate_token()
        utilities.check_is_uuid(self, access_token)

    ################################################################################################
    def test_calculate_expiry(self):
        """ Test the calculate_expiry static method in DatabaseConnector. """
        with patch('database.connector.time.time') as mock_time:
            mock_time.return_value = 4
            expiry = connector.DatabaseConnector.calculate_expiry(3)

        self.assertEqual("1970-01-01 01:00:07", expiry)

    ################################################################################################
    def test_hash_and_salt_password(self):
        """ Test the hash_and_salt_password static method in DatabaseConnector. """
        salting_rounds = 3
        salting_size = 5
        # Unicode characters from the keyboard that are not allowed:
        # - U+00A3
        # - U+00AC
        password = "135AFNcbr!\"$%^&*(){};'#:@~,./<>?|\\`/*"

        with patch('database.connector.settings') as mock_settings:
            mock_settings.PASSWORD_SALTING_ROUNDS = salting_rounds
            mock_settings.PASSWORD_SALTING_SIZE = salting_size

            # Check we can call the real pbkdf2_sha256.hash method without an error thrown.
            result = connector.DatabaseConnector.hash_and_salt_password(password)
            # Check the length is what we say it is in the settings.
            self.assertEqual(68, len(result))

            with patch('database.connector.pbkdf2_sha256.using') as mock_using:
                mock_return = "hashed_and_salted_password"
                mock_hash = MagicMock()
                mock_hash.hash.return_value = mock_return
                mock_using.return_value = mock_hash
                result = connector.DatabaseConnector.hash_and_salt_password(password)
                mock_using.assert_called_once_with(rounds=salting_rounds,
                                                   salt_size=salting_size)
                mock_hash.hash.assert_called_once_with(password)
                self.assertEqual(mock_return, result)

    ################################################################################################
    def test_register_user(self):
        """ Test registering a user adds entries to the users, scores and access tables. """
        utilities.create_tables(self.subject, ["1"])

        expected_username = "dave"
        expected_password = "password"
        expected_hashed_and_salted_password = "password1"
        access_expiry = self.subject.calculate_expiry(10000)
        refresh_expiry = self.subject.calculate_expiry(20000)
        expected_uuid = "7acb7e47-d8af-4b94-b096-2f5f7e1f99c7"

        with patch('database.connector.pbkdf2_sha256.using') as mock_using:
            mock_hash = MagicMock()
            mock_hash.hash.return_value = expected_hashed_and_salted_password
            mock_using.return_value = mock_hash
            with patch('database.connector.uuid.uuid4') as mock_uuid4:
                mock_uuid4.return_value = expected_uuid
                with patch('database.connector.DatabaseConnector.calculate_expiry') as mock_expiry:
                    def mock_expiry_return(expiry):
                        if expiry == settings.ACCESS_EXPIRY_SECONDS:
                            return access_expiry
                        elif expiry == settings.REFRESH_EXPIRY_SECONDS:
                            return refresh_expiry

                    mock_expiry.side_effect = mock_expiry_return

                    self.subject.register_user(expected_username, expected_password)

                    mock_using.assert_called_once_with(rounds=settings.PASSWORD_SALTING_ROUNDS,
                                                       salt_size=settings.PASSWORD_SALTING_SIZE)
                    mock_hash.hash.assert_called_once_with(expected_password)

        # Note that the access and refresh token would be different, but as we are mocking the
        # return of uuid.uuid4 above they will be the same.
        expected_data = {
            "users": {
                "primary_key": "username",
                "data": [
                    {
                        "username": expected_username,
                        "password": expected_hashed_and_salted_password,
                        "refresh_token": expected_uuid,
                        "refresh_token_expiry": datetime.strptime(refresh_expiry,
                                                                  settings.DATETIME_FORMAT),
                        "activated": True,
                        "theme": "ocean"
                    }
                ]
            },
            "scores": {
                "primary_key": "username",
                "data": [
                    {
                        "username": expected_username,
                        "1": -1
                    }
                ]
            },
            "access": {
                "primary_key": "username",
                "data": [
                    {
                        "access_token": expected_uuid,
                        "access_token_expiry": datetime.strptime(access_expiry,
                                                                 settings.DATETIME_FORMAT),
                        "username": expected_username
                    }
                ]
            }
        }

        utilities.check_data_in_tables(self.database_connection, self, expected_data)

    ################################################################################################
    def test_cannot_register_the_same_user(self):
        """ Test cannot add the same user twice. """
        utilities.create_tables(self.subject, ["1"])

        self.subject.register_user("dave", "pass")

        with self.assertRaises(LookupError) as lookup_error:
            self.subject.register_user("dave", "pass")
        self.assertEqual("User: 'dave' already exists.", str(lookup_error.exception))

    ################################################################################################
    def test_register_user_for_invalid_username_and_password(self):
        """ Test register user for invalid username and passwords. """
        utilities.create_tables(self.subject, ["1"])

        with self.assertRaises(ValueError) as value_error:
            self.subject.register_user(None, "password")
        self.assertEqual("Username cannot be None.", str(value_error.exception))

        with self.assertRaises(ValueError) as value_error:
            self.subject.register_user("username", None)
        self.assertEqual("Password cannot be None.", str(value_error.exception))

        with self.assertRaises(ValueError) as value_error:
            self.subject.register_user("", "password")
        self.assertEqual("Username cannot be empty.", str(value_error.exception))

        with self.assertRaises(ValueError) as value_error:
            self.subject.register_user("username", "")
        self.assertEqual("Password cannot be empty.", str(value_error.exception))

        with self.assertRaises(ValueError) as value_error:
            self.subject.register_user("u" * (settings.MAX_USERNAME_LENGTH + 1), "password")
        self.assertEqual("Username too long (max: " + str(settings.MAX_USERNAME_LENGTH) +
                         " characters).", str(value_error.exception))

        with self.assertRaises(ValueError) as value_error:
            self.subject.register_user("&", "password")
        self.assertEqual("Username should be alphanumeric.", str(value_error.exception))

        with self.assertRaises(ValueError) as value_error:
            self.subject.register_user("username", "\x19")
        self.assertEqual("Invalid character in password.", str(value_error.exception))

        with self.assertRaises(ValueError) as value_error:
            self.subject.register_user("username", "\x7F")
        self.assertEqual("Invalid character in password.", str(value_error.exception))

    ################################################################################################
    def test_register_user_access_expiry_does_not_exceed_refresh_expiry(self):
        """ Test register user access expiry does not exceed refresh expiry. """
        utilities.create_tables(self.subject, ["1"])

        username = "username"

        with patch('database.connector.settings.ACCESS_EXPIRY_SECONDS') as mock_settings:
            mock_settings.ACCESS_EXPIRY_SECONDS = 20000
            mock_settings.REFRESH_EXPIRY_SECONDS = 10000
            self.subject.register_user(username, "password")

        self.assertEqual(utilities.get_refresh_expiry(self.database_connection, username),
                         utilities.get_access_expiry(self.database_connection, username))

    ################################################################################################
    def test_delete_user(self):
        """ Test deleting a user from the users table. """
        utilities.create_tables(self.subject, ["1", "2"])

        expected_user_1 = "dave"
        mock_uuid_1 = "7acb7e47-d8af-4b94-b096-2f5f7e1f99c7"
        expected_user_2 = "steve"
        mock_uuid_2 = "eae5fd6e-180a-45c8-849a-1c9d2e5f83e7"

        with patch('database.connector.uuid.uuid4') as mock_uuid4:
            mock_uuid4.return_value = mock_uuid_1
            self.subject.register_user(expected_user_1, "password")
        with patch('database.connector.uuid.uuid4') as mock_uuid4:
            mock_uuid4.return_value = mock_uuid_2
            self.subject.register_user(expected_user_2, "password")

        expected_data = {
            "users": {
                "primary_key": "username",
                "data": [
                    {
                        "username": expected_user_1,
                        "refresh_token": mock_uuid_1,
                        "activated": True
                    },
                    {
                        "username": expected_user_2,
                        "refresh_token": mock_uuid_2,
                        "activated": True
                    }
                ]
            },
            "scores": {
                "primary_key": "username",
                "data": [
                    {
                        "username": expected_user_1,
                        "1": -1,
                        "2": -1
                    },
                    {
                        "username": expected_user_2,
                        "1": -1,
                        "2": -1
                    }
                ]
            },
            "access": {
                "primary_key": "username",
                "data": [
                    {
                        "access_token": mock_uuid_1,
                        "username": expected_user_1
                    },
                    {
                        "access_token": mock_uuid_2,
                        "username": expected_user_2
                    }
                ]
            }
        }

        utilities.check_data_in_tables(self.database_connection, self, expected_data)

        self.subject.delete_user(expected_user_2)

        expected_data = {
            "users": {
                "primary_key": "username",
                "data": [
                    {
                        "username": expected_user_1,
                        "refresh_token": mock_uuid_1,
                        "activated": True
                    }
                ]
            },
            "scores": {
                "primary_key": "username",
                "data": [
                    {
                        "username": expected_user_1,
                        "1": -1,
                        "2": -1
                    }
                ]
            },
            "access": {
                "primary_key": "username",
                "data": [
                    {
                        "access_token": mock_uuid_1,
                        "username": expected_user_1
                    }
                ]
            }
        }

        utilities.check_data_in_tables(self.database_connection, self, expected_data)

        self.subject.delete_user(expected_user_1)

        utilities.check_number_of_rows_in_table(self.database_connection, self, "users", 0)
        utilities.check_number_of_rows_in_table(self.database_connection, self, "scores", 0)
        utilities.check_number_of_rows_in_table(self.database_connection, self, "access", 0)

    ################################################################################################
    def test_cannot_delete_user_that_does_not_exist(self):
        """ Test cannot delete a user that doesn't exist. """
        utilities.create_tables(self.subject, ["1"])

        with self.assertRaises(LookupError) as lookup_error:
            self.subject.delete_user("not_a_user")
        self.assertEqual("User: 'not_a_user' does not exist.", str(lookup_error.exception))

    ################################################################################################
    def test_get_username_from_access_token(self):
        """ Test get username from access token. """
        utilities.create_tables(self.subject, ["1"])

        with self.assertRaises(connector.InvalidAccessTokenException) as exception:
            self.subject.get_username("not_a_UUID")
        self.assertEqual("Access token is invalid.", str(exception.exception))

        username = "username"

        self.subject.register_user(username, "password")

        access_token = self.subject.get_access_information(username)["access_token"]

        self.assertEqual(username, self.subject.get_username(access_token))

    ################################################################################################
    def test_adding_scores_to_the_scores_table(self):
        """ Test adding a score to the scores table. """
        utilities.create_tables(self.subject, ["1", "2", "3"])

        username = "dave"
        self.subject.register_user(username, "password")
        access_token = self.subject.get_access_information(username)["access_token"]

        with patch('database.connector.settings') as mock_settings:
            mock_settings.MAXIMUM_SCORE = 10

            self.subject.update_score(access_token, "1", 0)
            self.subject.update_score(access_token, "2", 5)
            self.subject.update_score(access_token, "3", 10)

        expected_data = {
            "scores": {
                "primary_key": "username",
                "data": [
                    {
                        "username": username,
                        "1": 0,
                        "2": 5,
                        "3": 10
                    }
                ]
            }
        }

        utilities.check_data_in_tables(self.database_connection, self, expected_data)

    ################################################################################################
    def test_adding_a_score_when_access_token_is_incorrect(self):
        """ Test adding a score when the access token is incorrect. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        self.subject.register_user(username, "password")

        with self.assertRaises(connector.InvalidAccessTokenException) as exception:
            self.subject.update_score("not_a_UUID", "1", 0)
        self.assertEqual("Access token is invalid.", str(exception.exception))

    ################################################################################################
    def test_adding_a_score_when_column_does_not_exist(self):
        """ Test adding a score when the column for a user does not exist. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        self.subject.register_user(username, "password")

        with patch('database.connector.settings') as mock_settings:
            mock_settings.MAXIMUM_SCORE = 10

            # "GR" has not been added to the scores columns.
            with self.assertRaises(MySQLdb.OperationalError) as operational_error:
                access_token = self.subject.get_access_information(username)["access_token"]
                self.subject.update_score(access_token, "2", 5)
            expected_message = "Unknown column '2' in 'field list'"
            self.assertEqual(expected_message, operational_error.exception.args[1])

    ################################################################################################
    def test_adding_scores_outside_allowed_range(self):
        """ Test adding scores outside the allowed range. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        self.subject.register_user(username, "password")
        access_token = self.subject.get_access_information(username)["access_token"]

        with patch('database.connector.settings') as mock_settings:
            mock_settings.MAXIMUM_SCORE = 5

            with self.assertRaises(ValueError) as value_error:
                self.subject.update_score(access_token, "1", -1)
            self.assertEqual("Score -1 not in [0,5].", str(value_error.exception))

            with self.assertRaises(ValueError) as value_error:
                self.subject.update_score(access_token, "1", 6)
            self.assertEqual("Score 6 not in [0,5].", str(value_error.exception))

    ################################################################################################
    def test_cannot_check_user_is_activated_if_user_does_not_exist(self):
        """ Test cannot check user is activated if the user does not exist. """
        utilities.create_tables(self.subject, ["1"])

        with self.assertRaises(LookupError) as lookup_error:
            self.subject.is_user_activated("username")
        self.assertEqual("User: 'username' does not exist.", str(lookup_error.exception))

    ################################################################################################
    def test_deactivating_a_users_account(self):
        """ Test deactivating a user's account. """
        utilities.create_tables(self.subject, ["1"])

        deactivated_username = "dave"
        other_username = "steve"
        mock_uuid = "7acb7e47-d8af-4b94-b096-2f5f7e1f99c7"

        self.subject.register_user(deactivated_username, "password")

        with patch('database.connector.uuid.uuid4') as mock_uuid4:
            mock_uuid4.return_value = mock_uuid
            self.subject.register_user(other_username, "password")

        self.subject.deactivate_user(deactivated_username)
        self.assertFalse(self.subject.is_user_activated(deactivated_username))

        expected_data = {
            "users": {
                "primary_key": "username",
                "data": [
                    {
                        "username": deactivated_username,
                        "refresh_token": None,
                        "activated": False
                    },
                    {
                        "username": other_username,
                        "refresh_token": mock_uuid
                    }
                ]
            },
            "access": {
                "primary_key": "username",
                "data": [
                    {
                        "access_token": mock_uuid,
                        "username": other_username
                    }
                ]
            }
        }

        utilities.check_data_in_tables(self.database_connection, self, expected_data)

    ################################################################################################
    def test_reactivating_a_users_account(self):
        """ Test reactivating a user's account. """
        utilities.create_tables(self.subject, ["1"])

        reactivated_username = "dave"
        mock_uuid = "7acb7e47-d8af-4b94-b096-2f5f7e1f99c7"

        self.subject.register_user(reactivated_username, "password")
        self.subject.deactivate_user(reactivated_username)

        with patch('database.connector.uuid.uuid4') as mock_uuid4:
            mock_uuid4.return_value = mock_uuid
            self.subject.activate_user(reactivated_username)

        self.assertTrue(self.subject.is_user_activated(reactivated_username))

        expected_data = {
            "users": {
                "primary_key": "username",
                "data": [
                    {
                        "username": reactivated_username,
                        "refresh_token": mock_uuid,
                        "activated": True
                    }
                ]
            },
            "access": {
                "primary_key": "username",
                "data": [
                    {
                        "access_token": mock_uuid,
                        "username": reactivated_username
                    }
                ]
            }
        }

        utilities.check_data_in_tables(self.database_connection, self, expected_data)

    ################################################################################################
    def test_get_access_information(self):
        """ Test getting the access information. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        # Set the expiry to 10 seconds.
        expected_expiry = self.subject.calculate_expiry(10000)
        expected_uuid = "7acb7e47-d8af-4b94-b096-2f5f7e1f99c8"

        with patch('database.connector.uuid.uuid4') as mock_uuid4:
            mock_uuid4.return_value = expected_uuid
            with patch('database.connector.DatabaseConnector.calculate_expiry') as mock_expiry:
                mock_expiry.return_value = expected_expiry
                self.subject.register_user(username, "password")
                mock_expiry.assert_called_with(settings.ACCESS_EXPIRY_SECONDS)

        access_information = self.subject.get_access_information(username)
        self.assertEqual(expected_uuid, access_information["refresh_token"])
        self.assertEqual(expected_uuid, access_information["access_token"])
        self.assertEqual(expected_expiry, access_information["access_token_expiry"])
        self.assertEqual(username, access_information["username"])

    ################################################################################################
    def test_is_refresh_token_valid(self):
        """ Test is the refresh token valid. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        expected_uuid = "7acb7e47-d8af-4b94-b096-2f5f7e1f99c8"
        other_uuid = "eae5fd6e-180a-45c8-849a-1c9d2e5f83e7"

        with self.assertRaises(LookupError) as lookup_error:
            self.subject.is_refresh_token_valid(username, expected_uuid)
        self.assertEqual("User: 'dave' does not exist.", str(lookup_error.exception))

        with patch('database.connector.uuid.uuid4') as mock_uuid4:
            mock_uuid4.return_value = expected_uuid
            self.subject.register_user(username, "password")

        self.assertTrue(self.subject.is_refresh_token_valid(username, expected_uuid))

        self.assertFalse(self.subject.is_refresh_token_valid(username, other_uuid))

        self.subject.deactivate_user(username)
        with self.assertRaises(Exception) as exception:
            self.subject.is_refresh_token_valid(username, expected_uuid)
        self.assertEqual("Account has been deactivated.", str(exception.exception))

        with patch('database.connector.uuid.uuid4') as mock_uuid4:
            mock_uuid4.return_value = expected_uuid
            self.subject.activate_user(username)
        expired_refresh_time = self.subject.calculate_expiry(-10000)
        utilities.set_refresh_expiry(self.database_connection, username, expired_refresh_time)
        self.assertFalse(self.subject.is_refresh_token_valid(username, expected_uuid))

        expected_data = {
            "users": {
                "primary_key": "username",
                "data": [
                    {
                        "username": username,
                        "refresh_token": None,
                        "refresh_token_expiry": None,
                        "activated": True
                    }
                ]
            }
        }

        utilities.check_data_in_tables(self.database_connection, self, expected_data)

    ################################################################################################
    def test_is_access_token_valid(self):
        """ Test is access token valid. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        expected_uuid = "7acb7e47-d8af-4b94-b096-2f5f7e1f99c8"
        another_uuid = "eae5fd6e-180a-45c8-849a-1c9d2e5f83e7"

        with self.assertRaises(LookupError) as lookup_error:
            self.subject.is_access_token_valid(username, expected_uuid)
        self.assertEqual("User: 'dave' does not exist.", str(lookup_error.exception))

        with patch('database.connector.uuid.uuid4') as mock_uuid4:
            mock_uuid4.return_value = expected_uuid
            self.subject.register_user(username, "password")

        self.assertTrue(self.subject.is_access_token_valid(username, expected_uuid))

        self.subject.deactivate_user(username)
        with self.assertRaises(Exception) as exception:
            self.subject.is_access_token_valid(username, expected_uuid)
        self.assertEqual("Account has been deactivated.", str(exception.exception))

        self.subject.activate_user(username)
        self.assertFalse(self.subject.is_access_token_valid(username, another_uuid))

        # Set the expiry to be the epoch.
        utilities.set_access_expiry(self.database_connection, username, "1970-01-01 01:00:00")

        self.assertFalse(self.subject.is_access_token_valid(username, expected_uuid))

        # Check the entry has been deleted from the access table as it was after the expiry.
        utilities.check_number_of_rows_in_table(self.database_connection, self, "access", 0)

    ################################################################################################
    def test_extend_access_token(self):
        """ Test extending the access token. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"

        access_expiry = self.subject.calculate_expiry(10000)
        refresh_expiry = self.subject.calculate_expiry(30000)
        extended_access_expiry = self.subject.calculate_expiry(20000)

        self.subject.register_user(username, "password")

        utilities.set_access_expiry(self.database_connection, username, access_expiry)
        utilities.set_refresh_expiry(self.database_connection, username, refresh_expiry)

        access_token = self.subject.get_access_information(username)["access_token"]

        with patch('database.connector.DatabaseConnector.calculate_expiry') as mock_expiry:
            mock_expiry.return_value = extended_access_expiry
            self.subject.extend_access_expiry(username, access_token)

        access_token_expiry = self.subject.get_access_information(username)["access_token_expiry"]

        self.assertEqual(extended_access_expiry, access_token_expiry)

    ################################################################################################
    def test_cannot_extend_access_expiry(self):
        """ Test when you cannot extend the access expiry. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"

        with self.assertRaises(LookupError) as lookup_error:
            self.subject.extend_access_expiry(username, "")
        self.assertEqual("User: 'dave' does not exist.", str(lookup_error.exception))

        self.subject.register_user(username, "password")
        # Now we test we cannot extend the access expiry when we have deleted the access token.
        access_token = self.subject.get_access_information(username)["access_token"]
        self.subject.delete_access(username)
        with self.assertRaises(ValueError) as value_error:
            self.subject.extend_access_expiry(username, access_token)
        self.assertEqual("Access token is invalid.", str(value_error.exception))

        self.subject.activate_user(username)
        access_token = self.subject.get_access_information(username)["access_token"]
        expired_refresh_time = self.subject.calculate_expiry(-10000)
        utilities.set_refresh_expiry(self.database_connection, username, expired_refresh_time)

        with self.assertRaises(Exception) as exception:
            self.subject.extend_access_expiry(username, access_token)
        self.assertEqual("Cannot extend access token's expiry as refresh token has expired.",
                         str(exception.exception))

    ################################################################################################
    def test_deleting_and_inserting_access_token(self):
        """ Test adding an access token. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        expected_expiry = self.subject.calculate_expiry(10000)
        add_user_token = "7acb7e47-d8af-4b94-b096-2f5f7e1f99c8"
        new_access_token = "eae5fd6e-180a-45c8-849a-1c9d2e5f83e7"

        with patch('database.connector.uuid.uuid4') as mock_uuid4:
            mock_uuid4.return_value = add_user_token
            self.subject.register_user(username, "password")

        with patch('database.connector.DatabaseConnector.calculate_expiry') as mock_expiry:
            mock_expiry.return_value = expected_expiry
            with patch('database.connector.uuid.uuid4') as mock_uuid4:
                mock_uuid4.return_value = new_access_token

                self.subject.delete_access(username)

                utilities.check_number_of_rows_in_table(self.database_connection, self, "access", 0)

                self.subject.insert_access(username)

                expected_data = {
                    "access": {
                        "primary_key": "username",
                        "data": [
                            {
                                "access_token": new_access_token,
                                "username": username
                            }
                        ]
                    }
                }

                utilities.check_data_in_tables(self.database_connection, self, expected_data)

                # Check an IntegrityError is thrown if an access entry already exists.
                with self.assertRaises(MySQLdb.IntegrityError) as integrity_error:
                    self.subject.insert_access(username)
                expected_message = "Duplicate entry 'dave' for key 'PRIMARY'"
                self.assertEqual(expected_message, str(integrity_error.exception.args[1]))

    ################################################################################################
    def test_cannot_insert_access_when_user_does_not_exist(self):
        """ Test cannot insert access when the user does not exist. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        with self.assertRaises(LookupError) as lookup_error:
            self.subject.insert_access(username)
        self.assertEqual("User: 'dave' does not exist.", str(lookup_error.exception))

    ################################################################################################
    def test_delete_access_when_user_does_not_exist(self):
        """ Test cannot delete access when the user does not exist. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        # Note no exception will be thrown if the user does not exist.
        self.subject.delete_access(username)

    ################################################################################################
    def test_login_user(self):
        """ Test login user. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        password = "password"
        other_password = "other_password"

        with self.assertRaises(ValueError) as value_error:
            self.subject.login_user(username, password)
        self.assertEqual("Cannot login. Username/password is incorrect.",
                         str(value_error.exception))

        self.subject.register_user(username, password)
        # Check an exception is not raised when the user logs in.
        self.subject.login_user(username, password)

        self.subject.deactivate_user(username)
        with self.assertRaises(Exception) as exception:
            self.subject.login_user(username, password)
        self.assertEqual("Account has been deactivated.", str(exception.exception))

        self.subject.activate_user(username)
        with self.assertRaises(ValueError) as value_error:
            self.subject.login_user(username, other_password)
        self.assertEqual("Cannot login. Username/password is incorrect.",
                         str(value_error.exception))

    ################################################################################################
    def test_login_creates_a_new_refresh_token_when_it_expires(self):
        """ Test login creates a new refresh token when it expires. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        password = "password"

        register_token = "7acb7e47-d8af-4b94-b096-2f5f7e1f99c8"
        login_token = "eae5fd6e-180a-45c8-849a-1c9d2e5f83e7"
        login_expiry = self.subject.calculate_expiry(10000)

        with patch('database.connector.uuid.uuid4') as mock_uuid4:
            mock_uuid4.return_value = register_token
            self.subject.register_user(username, password)

        expired_refresh_time = self.subject.calculate_expiry(-10000)
        utilities.set_refresh_expiry(self.database_connection, username, expired_refresh_time)

        with patch('database.connector.DatabaseConnector.calculate_expiry') as mock_expiry:
            mock_expiry.return_value = login_expiry
            with patch('database.connector.uuid.uuid4') as mock_uuid4:
                mock_uuid4.return_value = login_token
                self.subject.login_user(username, password)

        expected_data = {
            "users": {
                "primary_key": "username",
                "data": [
                    {
                        "username": username,
                        "refresh_token": login_token,
                        "refresh_token_expiry": datetime.strptime(login_expiry,
                                                                  settings.DATETIME_FORMAT),
                        "activated": True
                    }
                ]
            },
            "access": {
                "primary_key": "username",
                "data": [
                    {
                        "access_token": login_token,
                        "access_token_expiry": datetime.strptime(login_expiry,
                                                                 settings.DATETIME_FORMAT),
                        "username": username
                    }
                ]
            }
        }

        utilities.check_data_in_tables(self.database_connection, self, expected_data)

    ################################################################################################
    def test_login_creates_an_access_token(self):
        """ Test login creates an access token. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        password = "password"
        login_token = "eae5fd6e-180a-45c8-849a-1c9d2e5f83e7"
        login_expiry = self.subject.calculate_expiry(10000)

        with patch('database.connector.DatabaseConnector.calculate_expiry') as mock_expiry:
            mock_expiry.return_value = login_expiry
            self.subject.register_user(username, password)

        self.subject.delete_access(username)

        with patch('database.connector.DatabaseConnector.calculate_expiry') as mock_expiry:
            mock_expiry.return_value = login_expiry
            with patch('database.connector.uuid.uuid4') as mock_uuid4:
                mock_uuid4.return_value = login_token
                self.subject.login_user(username, password)

        expected_data = {
            "access": {
                "primary_key": "username",
                "data": [
                    {
                        "access_token": login_token,
                        "access_token_expiry": datetime.strptime(login_expiry,
                                                                 settings.DATETIME_FORMAT),
                        "username": username
                    }
                ]
            }
        }

        utilities.check_data_in_tables(self.database_connection, self, expected_data)

    ################################################################################################
    def test_login_extends_access_token_expiry(self):
        """ Test login extends the access token expiry. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        password = "password"
        access_expiry = self.subject.calculate_expiry(10000)
        refresh_expiry = self.subject.calculate_expiry(30000)
        extended_access_expiry = self.subject.calculate_expiry(20000)

        self.subject.register_user(username, password)

        utilities.set_access_expiry(self.database_connection, username, access_expiry)
        utilities.set_refresh_expiry(self.database_connection, username, refresh_expiry)

        with patch('database.connector.DatabaseConnector.calculate_expiry') as mock_expiry:
            mock_expiry.return_value = extended_access_expiry
            self.subject.login_user(username, password)

        expected_data = {
            "access": {
                "primary_key": "username",
                "data": [
                    {
                        "access_token_expiry": datetime.strptime(extended_access_expiry,
                                                                 settings.DATETIME_FORMAT),
                        "username": username
                    }
                ]
            }
        }

        utilities.check_data_in_tables(self.database_connection, self, expected_data)

    ################################################################################################
    def test_cannot_extend_access_expiry_beyond_the_refresh_expiry(self):
        """ Test cannot extend access expiry beyond the refresh expiry. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        # Set the expiry to 10 seconds time
        refresh_expiry = self.subject.calculate_expiry(10000)
        access_expiry = self.subject.calculate_expiry(20000)

        with patch('database.connector.DatabaseConnector.calculate_expiry') as mock_expiry:
            mock_expiry.return_value = refresh_expiry
            self.subject.register_user(username, "password")

        access_token = self.subject.get_access_information(username)["access_token"]

        with patch('database.connector.DatabaseConnector.calculate_expiry') as mock_expiry:
            mock_expiry.return_value = access_expiry
            self.subject.extend_access_expiry(username, access_token)

        access_token_expiry = self.subject.get_access_information(username)["access_token_expiry"]

        self.assertEqual(refresh_expiry, access_token_expiry)

    ################################################################################################
    def test_do_not_extend_access_expiry_if_current_expiry_is_larger(self):
        """ Test we do not extend the access expiry if the current expiry is larger. """
        utilities.create_tables(self.subject, ["1"])

        username = "dave"
        password = "password"
        current_access_expiry = self.subject.calculate_expiry(20000)
        refresh_expiry = self.subject.calculate_expiry(30000)
        sooner_access_expiry = self.subject.calculate_expiry(10000)

        self.subject.register_user(username, password)

        utilities.set_access_expiry(self.database_connection, username, current_access_expiry)
        utilities.set_refresh_expiry(self.database_connection, username, refresh_expiry)

        with patch('database.connector.DatabaseConnector.calculate_expiry') as mock_expiry:
            mock_expiry.return_value = sooner_access_expiry
            self.subject.login_user(username, password)

        expected_data = {
            "access": {
                "primary_key": "username",
                "data": [
                    {
                        "access_token_expiry": datetime.strptime(current_access_expiry,
                                                                 settings.DATETIME_FORMAT),
                        "username": username
                    }
                ]
            }
        }

        utilities.check_data_in_tables(self.database_connection, self, expected_data)

    ################################################################################################
    def test_get_results_dictionary(self):
        """ Test getting the results dictionary. """
        country_codes = ["1", "2", "3"]

        utilities.create_tables(self.subject, country_codes)

        username_1 = "username1"
        username_2 = "username2"
        username_3 = "username3"
        password = "password"

        self.subject.register_user(username_1, password)
        access_token_1 = self.subject.get_access_information(username_1)["access_token"]
        self.subject.register_user(username_2, password)
        access_token_2 = self.subject.get_access_information(username_2)["access_token"]
        self.subject.register_user(username_3, password)
        access_token_3 = self.subject.get_access_information(username_3)["access_token"]

        with patch('database.connector.settings') as mock_settings:
            mock_settings.MAXIMUM_SCORE = 10

            self.subject.update_score(access_token_1, "1", 3)
            self.subject.update_score(access_token_1, "2", 10)

            self.subject.update_score(access_token_2, "1", 3)
            self.subject.update_score(access_token_2, "3", 5)
            self.subject.update_score(access_token_2, "2", 5)

            self.subject.update_score(access_token_3, "1", 0)

        with patch('database.connector.settings') as mock_settings:
            mock_settings.MAXIMUM_SCORE = 10

            mock_settings.entries = [
                {
                    "id": "1"
                },
                {
                    "id": "2"
                },
                {
                    "id": "3"
                }
            ]

            results = self.subject.generate_results_dictionary(country_codes)

        expected_results = {
            "1": {
                -1: 0, 0: 1, 1: 0, 2: 0, 3: 2, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0
            },
            "2": {
                -1: 1, 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0, 8: 0, 9: 0, 10: 1
            },
            "3": {
                -1: 2, 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0
            }
        }

        self.assertEqual(expected_results, results)

    ################################################################################################
    def test_get_entry(self):
        """ Test get entry. """
        country_codes = ["1"]

        utilities.create_tables(self.subject, country_codes)

        username = "dave"
        password = "password"

        self.subject.register_user(username, password)

        access_token = self.subject.get_access_information(username)["access_token"]

        with patch('database.connector.settings') as mock_settings:
            mock_settings.country_codes = ["1"]

            mock_settings.entries = [
                {
                    "id": "1",
                    "attributes": {}
                }
            ]

            result_entry = self.subject.get_entry(access_token, "1")

        expected_entry = {
            "id": "1",
            "attributes": {
                "score": -1
            }
        }

        self.assertEqual(expected_entry, result_entry)

    ################################################################################################
    def test_get_entry_when_entry_id_is_not_valid(self):
        """ Test get entry when if is not valid. """
        country_codes = ["1"]

        utilities.create_tables(self.subject, country_codes)

        username = "dave"
        password = "password"

        self.subject.register_user(username, password)

        access_token = self.subject.get_access_information(username)["access_token"]

        with patch('database.connector.settings') as mock_settings:
            mock_settings.country_codes = ["1"]

            mock_settings.entries = [
                {
                    "id": "1",
                    "attributes": {}
                }
            ]

            injection_string = "; select * from access;"

            with self.assertRaises(ValueError) as value_error:
                self.subject.get_entry(access_token, injection_string)
            self.assertEqual("Entry ID is invalid.", str(value_error.exception))

    ################################################################################################
    def test_generate_entries_dictionary(self):
        """ Test generate_entries_dictionary. """
        country_codes = ["1", "2", "3"]

        utilities.create_tables(self.subject, country_codes)

        username = "dave"
        password = "password"

        self.subject.register_user(username, password)

        access_token = self.subject.get_access_information(username)["access_token"]

        self.subject.update_score(access_token, "1", 7)
        self.subject.update_score(access_token, "2", 10)

        with patch('database.connector.settings') as mock_settings:
            mock_settings.MAXIMUM_SCORE = 10

            mock_settings.entries = [
                {
                    "id": "1",
                    "attributes": {}
                },
                {
                    "id": "2",
                    "attributes": {}
                },
                {
                    "id": "3",
                    "attributes": {}
                }
            ]

            result_entries = self.subject.generate_entries_dictionary(access_token)

        expected_entries = [
            {
                "id": "1",
                "attributes": {
                    "score": 7
                }
            },
            {
                "id": "2",
                "attributes": {
                    "score": 10
                }
            },
            {
                "id": "3",
                "attributes": {
                    "score": -1
                }
            }
        ]

        self.assertEqual(expected_entries, result_entries)

    ################################################################################################
    def test_generate_settings_dictionary(self):
        """ Test generate_settings_dictionary. """
        country_codes = ["1"]

        utilities.create_tables(self.subject, country_codes)

        username = "dave"
        password = "password"

        self.subject.register_user(username, password)

        access_token = self.subject.get_access_information(username)["access_token"]

        with patch('database.connector.settings') as mock_settings:
            mock_settings.user_settings = [
                {
                    "id" : "1",
                    "type" : "settings",
                    "attributes" : {
                        "setting": "theme",
                        "value": "ocean"
                    }
                }
            ];

            settings = self.subject.generate_settings_dictionary(access_token)

        expected_settings = [
            {
                "id" : "1",
                "type" : "settings",
                "attributes" : {
                    "setting": "theme",
                    "value": "ocean"
                }
            }
        ]

        self.assertEqual(expected_settings, settings)


####################################################################################################
if __name__ == '__main__':
    unittest.main()
