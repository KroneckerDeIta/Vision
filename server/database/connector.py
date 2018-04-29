from configuration import settings

import copy
import datetime
from passlib.hash import pbkdf2_sha256
import re
import sys
import time
import uuid

from handlers import update

sys.path.append('..')

""" This module contains the DatabaseConnector class, which is used for interacting with a
database. """
__author__ = "Thomas Reeve"


####################################################################################################
class InvalidAccessTokenException(Exception):
    """ Exception that is thrown when the access token is invalid. """
    ################################################################################################
    def __init__(self, message):
        """ Constructor.

        Args:
            message (str): Message to add to exception.
        """
        super(InvalidAccessTokenException, self).__init__(message)


####################################################################################################
class DatabaseConnector(object):
    """ DatabaseConnector objects are used to interact with databases. It uses a mysql connect
    object to do this. Methods in this class are mostly helper methods, if you want to contrust your
    own SQL query strings, with arguments, use the sql_query method. """
    ################################################################################################
    def __init__(self, mysql_connection):
        """ Constructor.
        
        Args:
            mysql_connection: MySQL connection object.
        """
        self.__mysql_connection = mysql_connection

    ################################################################################################
    def execute(self, *args, **kwargs):
        """ Calls the execute method directly on the MySQL connection object.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            MySQLCursor: The MySQL cursor.
        """
        cursor = self.__mysql_connection.cursor()
        cursor.execute(*args, **kwargs)
        self.__mysql_connection.commit()
        return cursor
    
    ################################################################################################
    def get_current_database(self):
        """ Get the name of the current database.
        
        Returns:
            str: The current database.
        """
        cursor = self.execute("SELECT DATABASE()")
        return cursor.fetchone()[0]

    ################################################################################################
    def get_all_databases(self):
        """ Gets the names of all the databases.
        
        Returns:
            list(str): The names of all the databases.
        """
        cursor = self.execute("SHOW DATABASES")
        databases = []
        for row in cursor.fetchall():
            databases.append(row[0])
        return databases

    ################################################################################################
    def does_database_exist(self, name):
        """ Checks if the database exists.

        Args:
            name (str): The database name.

        Returns:
            True if database exists. False otherwise.
        """
        databases = self.get_all_databases()
        return name in databases

    ################################################################################################
    def create_database(self, name):
        """ Creates a database with name.

        Args:
            name (str): The name of the new database.
        """
        self.execute("CREATE DATABASE %s" % name)

    ################################################################################################
    def drop_database(self, name):
        """ Drops a database with name.

        Args:
            name (str): The name of the database to drop.
        """
        self.execute("DROP DATABASE `%s`" % name)

    ################################################################################################
    def use_database(self, name):
        """ Use a database with name.

        Args:
            name (str): The name of the database to use.
        """
        self.execute("USE `%s`" % name)

    ################################################################################################
    def create_users_table(self):
        """ Creates the users table, which contains all the information about a user. """
        command = """
            CREATE TABLE users (
            username VARCHAR(%s) NOT NULL,
            password VARCHAR(%s) NOT NULL,
            refresh_token VARCHAR(%s) NULL,
            refresh_token_expiry DATETIME NULL,
            activated BOOLEAN NOT NULL DEFAULT FALSE,
            theme VARCHAR(%s) NOT NULL DEFAULT 'ocean',
            PRIMARY KEY (username)
            )
        """ % (settings.MAX_USERNAME_LENGTH,
               settings.PASSWORD_HASH_LENGTH,
               settings.UUID_LENGTH,
               settings.THEME_LENGTH)

        self.execute(command)

    ################################################################################################
    def create_access_table(self):
        """ Creates the access table, which contains tokens and access expiry. """
        command = """
            CREATE TABLE access (
            username VARCHAR(%s) NOT NULL,
            access_token VARCHAR(%s) NOT NULL,
            access_token_expiry DATETIME NOT NULL,
            PRIMARY KEY (username),
            FOREIGN KEY (username) REFERENCES users(username)
            )
        """ % (settings.MAX_USERNAME_LENGTH,
               settings.UUID_LENGTH)
        self.execute(command)

    ################################################################################################
    def create_scores_table(self, columns):
        """ Creates the scores table.
        
        Args:
            columns: Sequence of strings that are the column names.
        """

        columns_string = ''.join("`" + c + "` INT NOT NULL DEFAULT -1," for c in columns)

        command = """
            CREATE TABLE scores (
            username VARCHAR(%s) NOT NULL,
            %s
            PRIMARY KEY (username),
            FOREIGN KEY (username) REFERENCES users(username)
            )
        """ % (settings.MAX_USERNAME_LENGTH,
               columns_string)
        self.execute(command)

    ################################################################################################
    def user_exists(self, username):
        """ Checks the users table to see if the user exists.

        Args:
            username (str): The user's username.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        select_command = """
            SELECT * FROM users WHERE username = %s
        """
        select_params = (username, )
        cursor = self.execute(select_command, select_params)
        return len(cursor.fetchall()) == 1

    ################################################################################################
    @staticmethod
    def generate_token():
        """ Generates an access or refresh token (a UUID).

        Returns:
            str: A token (UUID).
        """
        return uuid.uuid4()

    ################################################################################################
    @staticmethod
    def calculate_expiry(expiry_time_seconds):
        """ Gets the expiry time.

        Args:
            expiry_time_seconds (int): The number of seconds from now until expiry.

        Returns:
            int: The expiry time in the following format: %Y-%m-%d %H:%M:%S.
        """
        expiry_time_seconds = time.time() + expiry_time_seconds
        return time.strftime(settings.DATETIME_FORMAT, time.localtime(expiry_time_seconds))

    ################################################################################################
    @staticmethod
    def hash_and_salt_password(password):
        """ Salts and hashes a password.

        Args:
            password (str): The password to salt and hash.

        Returns:
           The salted and hashed password.
        """
        return pbkdf2_sha256.using(rounds=settings.PASSWORD_SALTING_ROUNDS,
                                   salt_size=settings.PASSWORD_SALTING_SIZE).hash(password)

    ################################################################################################
    @staticmethod
    def is_alphanumeric(string_to_check):
        """ Checks the string to see if it is alphanumeric.

        Args:
            string_to_check (str): The string to check.

        Returns:
            bool: True if string is alphanumeric, False otherwise.
        """
        return re.match('^[0-9a-zA-Z]+$', string_to_check) is not None

    ################################################################################################
    @staticmethod
    def is_printable(string_to_check):
        """ Checks the string to see if it is printable.

        Args:
            string_to_check (str): The string to check.

        Returns:
            bool: True if string is printable, False otherwise.
        """
        return re.match('^[\x20-\x7E]+$', string_to_check) is not None

    ################################################################################################
    @staticmethod
    def is_username_and_password_valid(username, password):
        """ Returns if the password is valid.

        Args:
            username (str): The user's username.
            password (str): The password to validate.

        Returns:
            tuple(bool, string): Tuple where first value is True if the password is valid, False
            otherwise, and the second value is a message explaining if the username or password is
            invalid (that is to be sent to the client).
        """
        valid = True
        invalid_message = None

        if username is None:
            valid = False
            invalid_message = "Username cannot be None."
        elif password is None:
            valid = False
            invalid_message = "Password cannot be None."
        elif username == "":
            valid = False
            invalid_message = "Username cannot be empty."
        elif password == "":
            valid = False
            invalid_message = "Password cannot be empty."
        elif len(username) > settings.MAX_USERNAME_LENGTH:
            valid = False
            invalid_message = "Username too long (max: " + str(settings.MAX_USERNAME_LENGTH) + \
                              " characters)."
        elif not DatabaseConnector.is_alphanumeric(username):
            valid = False
            invalid_message = "Username should be alphanumeric."
        elif not DatabaseConnector.is_printable(password):
            valid = False
            invalid_message = "Invalid character in password."

        return valid, invalid_message

    ################################################################################################
    def register_user(self, username, password):
        """ Registers the user. Rows are added to the users, scores and access tables.
        
        Args:
            username (str): The user's username.
            password (str): The user's password.

        Raises:
            LookupError: If the user does not exist.
            ValueError: If the username and/or password is invalid.
        """

        if self.user_exists(username):
            raise LookupError("User: '" + username + "' already exists.")
        else:
            valid, message = DatabaseConnector.is_username_and_password_valid(username, password)
            if valid:
                self.__insert_user(username, password)
                self.__insert_scores(username)
            else:
                raise ValueError(message)

    ################################################################################################
    def login_user(self, username, password):
        """ Logs the user in.

        Args:
            username (str): The user's username.
            password (str): The user's password.

        Raises:
            ValueError: If the username and/or password is invalid.
        """
        try:
            refresh_token, _ = self.__get_refresh_token_and_expiry(username)
        except LookupError:
            # We want to make the message more generic to follow OWASP guidelines.
            raise ValueError("Cannot login. Username/password is incorrect.")

        select_command = """
            SELECT password FROM users WHERE username = %s
        """
        select_params = (username, )
        cursor = self.execute(select_command, select_params)
        database_password = cursor.fetchone()[0]
        if not pbkdf2_sha256.verify(password, database_password):
            raise ValueError("Cannot login. Username/password is incorrect.")
        else:
            if refresh_token is None:
                # The only way we should be able to get in here is if the refresh token expired.
                # In the future we might want to check the user has been sending valid requests.
                # For now just reactivate the user.
                self.activate_user(username)
            else:
                access_token, _ = self.__get_access_token_and_expiry(username)
                if access_token is None:
                    self.insert_access(username)
                    access_token, _ = self.__get_access_token_and_expiry(username)
                self.extend_access_expiry(username, access_token)

    ################################################################################################
    def __insert_user(self, username, password):
        """ Inserts the user into the users table.

        Args:
            username (str): The user's username.
            password (str): The user's password.
        """
        hashed_and_salted_password = DatabaseConnector.hash_and_salt_password(password)

        insert_command = """
            INSERT INTO users (username, password)
            VALUES (%s, %s)
        """
        insert_params = (username, hashed_and_salted_password)
        self.execute(insert_command, insert_params)
        self.activate_user(username)

    ################################################################################################
    def __insert_scores(self, username):
        """ Inserts a scores row to the scores table, all of the scores will be initialised to -1.

        Args:
             username (str): The user's username.
        """
        insert_command = """
            INSERT INTO scores (username)
            VALUES (%s)
        """
        insert_params = (username, )
        self.execute(insert_command, insert_params)

    ################################################################################################
    def insert_access(self, username):
        """ Inserts an access row to the access table.

        Args:
            username (str): The user's username.
        """
        access_token = DatabaseConnector.generate_token()
        access_token_expiry = self.__calculate_access_expiry(username)

        insert_command = """
            INSERT INTO access (access_token, access_token_expiry, username)
            VALUES (%s, %s, %s)
        """
        insert_params = (access_token, access_token_expiry, username)
        self.execute(insert_command, insert_params)

    ################################################################################################
    def delete_user(self, username):
        """ Removes a user. Deletes rows from the users, scores and access tables.

        Args:
            username (str): The user's username.

        Raises:
            LookupError: If the user does not exist.
        """

        if not self.user_exists(username):
            raise LookupError("User: '" + username + "' does not exist.")
        else:
            self.delete_access(username)
            self.__delete_scores(username)
            self.__delete_user(username)

    ################################################################################################
    def __delete_user(self, username):
        """ Deletes the user from the users table.

        Args:
            username (str): The user's username.
        """
        delete_command = """
            DELETE FROM users WHERE username = %s
        """
        delete_params = (username, )
        self.execute(delete_command, delete_params)

    ################################################################################################
    def delete_access(self, username):
        """ Deletes an access row from the access table.

        Args:
            username (str): The user's username.
        """
        delete_command = """
            DELETE FROM access WHERE username = %s
        """
        delete_params = (username, )
        self.execute(delete_command, delete_params)
        update.close_connections(username=username, reason="Session Expired")

    ################################################################################################
    def __delete_scores(self, username):
        """ Deletes an access row from the access table.

        Args:
            username (str): The user's username.
        """
        delete_command = """
            DELETE FROM scores WHERE username = %s
        """
        delete_params = (username, )
        self.execute(delete_command, delete_params)

    ################################################################################################
    def get_username(self, access_token):
        """ Gets the username from the access token.

        Args:
            access_token (str): The user's access token.

        Returns:
            str: The user's username.

        Raises:
            InvalidAccessTokenException: If access token does not exist.
        """
        select_command = """
            SELECT `username` FROM access WHERE `access_token` = %s
        """
        select_params = (access_token, )
        cursor = self.execute(select_command, select_params)

        rows = cursor.fetchall()

        if len(rows) == 1:
            return rows[0][0]
        else:
            raise InvalidAccessTokenException("Access token is invalid.")

    ################################################################################################
    def update_score(self, access_token, column, score):
        """ Update the score in the scores table.

        Args:
            access_token (str): The user's access token.
            column (str): The name of the column to update in the scores table.
            score (int): The score.

        Raises:
            Exception: If the access token is invalid.
            ValueError: If the score is not in the correct range.
        """
        username = self.get_username(access_token)
        if score < 0 or score > settings.MAXIMUM_SCORE:
            raise ValueError("Score " + str(score) + " not in [0," + str(settings.MAXIMUM_SCORE) +
                             "].")
        else:
            update_command = 'UPDATE scores SET `' + column + '` = %s WHERE username = %s'
            update_params = (score, username)
            self.execute(update_command, update_params)

    ################################################################################################
    def get_access_information(self, username):
        """ Get the access information for the user.

        Args:
            username (str): The user's username.

        Returns:
            dict: Dictionary containing
            {
                "access_token": <UUID string>,
                "access_token_expiry": <date/time in string format: "%Y-%m-%d %H:%M:%S">,
                "refresh_token": <UUID string>
            }
        """
        refresh_token, _ = self.__get_refresh_token_and_expiry(username)
        access_token, access_token_expiry = self.__get_access_token_and_expiry(username)

        return {
            "access_token": str(access_token),
            "access_token_expiry": str(access_token_expiry),
            "refresh_token": str(refresh_token),
            "username": username
        }

    ################################################################################################
    def __get_access_token_and_expiry(self, username):
        """ Gets the access token and access token's expiry for the user.

        Args:
            username (str): The user's username.

        Raises:
            LookupError: If the user does not exist.
            Exception: If the account has been deactivated.
        """
        if not self.user_exists(username):
            raise LookupError("User: '" + username + "' does not exist.")
        elif not self.is_user_activated(username):
            raise Exception("Account has been deactivated.")
        else:
            select_command = """
                SELECT `access_token`, `access_token_expiry` FROM access WHERE username = %s
            """
            select_params = (username, )
            cursor = self.execute(select_command, select_params)

            rows = cursor.fetchall()

            if len(rows) == 1:
                token = rows[0][0]
                token_expiry = rows[0][1]

                if datetime.datetime.now() < token_expiry:
                    return token, token_expiry
                else:
                    self.delete_access(username)

        return None, None

    ################################################################################################
    def __get_refresh_token_and_expiry(self, username):
        """ Gets the refresh token and refresh token's expiry for the user.

        Args:
            username (str): The user's username.

        Returns:
            tuple(str, datetime): The refresh token and the expiry.

        Raises:
            LookupError: If the user does not exist.
            Exception: If the account has been deactivated.
        """

        if not self.user_exists(username):
            raise LookupError("User: '" + username + "' does not exist.")
        elif not self.is_user_activated(username):
            raise Exception("Account has been deactivated.")
        else:
            select_command = """
                SELECT `refresh_token`, `refresh_token_expiry` FROM users WHERE username = %s
            """
            select_params = (username, )
            cursor = self.execute(select_command, select_params)

            rows = cursor.fetchall()

            token = rows[0][0]
            token_expiry = rows[0][1]

            if datetime.datetime.now() < token_expiry:
                return token, token_expiry
            else:
                self.delete_access(username)
                self.remove_refresh_data(username)
                return None, None

    ################################################################################################
    def __is_token_valid(self, username, token_type, expected_token):
        """ Checks if the token is valid.

        Args:
            username (str): The user's username.
            token_type (str): The type of token ("Access" or "Refresh").
            expected_token (str): The expected token to check against the token in the database.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        valid = True

        if token_type == "Access":
            token, token_expiry = self.__get_access_token_and_expiry(username)
        elif token_type == "Refresh":
            token, token_expiry = self.__get_refresh_token_and_expiry(username)

        if token is None or token != expected_token:
            valid = False

        return valid

    ################################################################################################
    def is_refresh_token_valid(self, username, refresh_token):
        """ Returns if the refresh token is valid.

        Args:
            username (str): The user's username.
            refresh_token (str): The refresh token the client has sent.

        Returns:
            bool: True if refresh token is valid, False otherwise.
        """
        return self.__is_token_valid(username, "Refresh", refresh_token)

    ################################################################################################
    def is_access_token_valid(self, username, access_token):
        """ Returns if the access token is valid.

        Args:
            username (str): The user's username.
            access_token (str): The access token the client has sent.

        Returns:
            bool: True if access token is valid, False otherwise.
        """
        return self.__is_token_valid(username, "Access", access_token)

    ################################################################################################
    def is_user_activated(self, username):
        """ Checks if the user's account is activated, by checking there is a refresh token.

        Args:
            username (str): The user's username.

        Raises:
            LookupError: If the user doesn't exist.
        """
        if not self.user_exists(username):
            raise LookupError("User: '" + username + "' does not exist.")

        select_command = """
            SELECT `activated` FROM users WHERE username = %s
        """
        select_params = (username, )
        cursor = self.execute(select_command, select_params)
        return cursor.fetchone()[0]

    ################################################################################################
    def deactivate_user(self, username):
        """ Deactivates the user's account by removing their refresh token, and removing entries
        from the access token.

        Args:
            username (str): The user's username.
        """
        update_command = 'UPDATE users ' \
                         'SET `refresh_token` = NULL, ' \
                         '    `refresh_token_expiry` = NULL, ' \
                         '    `activated` = FALSE ' \
                         'WHERE username = %s'
        update_params = (username, )
        self.execute(update_command, update_params)

        self.delete_access(username)

    ################################################################################################
    def remove_refresh_data(self, username):
        """ Removes the refresh data for the user, the user is not deactivated though.

        Args:
            username (str): The user's username.
        """
        update_command = 'UPDATE users ' \
                         'SET `refresh_token` = NULL, ' \
                         '    `refresh_token_expiry` = NULL ' \
                         'WHERE username = %s'
        update_params = (username, )
        self.execute(update_command, update_params)

    ################################################################################################
    def activate_user(self, username):
        """ Reactivates the user's account by adding a refresh token, and adding an access token
        to the access table.

        Args:
            username (str): The user's username.
        """
        refresh_token = DatabaseConnector.generate_token()
        refresh_token_expiry = DatabaseConnector.calculate_expiry(settings.REFRESH_EXPIRY_SECONDS)
        update_command = 'UPDATE users ' \
                         'SET `refresh_token` = %s,' \
                         '    `refresh_token_expiry` = %s, ' \
                         '    `activated` = TRUE ' \
                         'WHERE username = %s'
        update_params = (refresh_token, refresh_token_expiry, username)
        self.execute(update_command, update_params)

        self.insert_access(username)

    ################################################################################################
    def __calculate_access_expiry(self, username):
        """ Calculates the access expiry that should be set in the access table.

        Args:
            username (str): The user's username.
        """
        refresh_token, refresh_token_expiry = self.__get_refresh_token_and_expiry(username)
        if refresh_token is None:
            raise Exception("Cannot extend access token's expiry as refresh token has expired.")

        _, current_access_token_expiry = self.__get_access_token_and_expiry(username)

        expiry = DatabaseConnector.calculate_expiry(settings.ACCESS_EXPIRY_SECONDS)
        datetime_expiry = datetime.datetime.strptime(expiry, settings.DATETIME_FORMAT)

        if current_access_token_expiry is not None:
            datetime_expiry = max(datetime_expiry, current_access_token_expiry)

        # We do not change the access token's expiry if the current expiry is greater than what
        # we will extend it to.
        return str(min(refresh_token_expiry, datetime_expiry))

    ################################################################################################
    def extend_access_expiry(self, username, expected_access_token):
        """ Extends the access token's expiry.

        Args:
            username (str): The user's username.
            expected_access_token (str): The access token sent by the client.
        """
        if self.is_access_token_valid(username, expected_access_token):
            update_command = 'UPDATE access SET `access_token_expiry` = %s WHERE username = %s'
            update_params = (self.__calculate_access_expiry(username), username)
            self.execute(update_command, update_params)
        else:
            raise ValueError("Access token is invalid.")

    ################################################################################################
    def generate_results_dictionary(self, columns):
        """ Generates the results dictionary.

        Args:
            columns: The columns to get the results for in the scores dictionary.

        Returns:
            dict: Dictionary of results in the following form:
            {
                "<column-name>": {
                    "results": {
                        -1: <number-of-times-this-number-appears-in-scores-for-column-name>,
                        ...
                    }
                }, ...
            }
        """
        select_columns = ''.join("`" + c + "`," for c in columns).rstrip(',')
        select_command = "SELECT " + select_columns + " FROM scores"
        cursor = self.execute(select_command)
        rows = cursor.fetchall()

        maximum_score = settings.MAXIMUM_SCORE

        def default_scores(): return dict((score, 0) for score in range(-1, maximum_score + 1))

        results = dict((column, default_scores()) for column in columns)

        for row in rows:
            for index, column in enumerate(columns):
                results[column][row[index]] += 1

        return results

    ################################################################################################
    def get_entry(self, access_token, entry_id):
        """ Gets the entry.

        :param access_token: The access token the client has sent.
        :type access_token: str
        :param entry_id: The ID of the entry to get.
        :type entry_id: str
        :return The entry.
        """

        if entry_id not in settings.country_codes:
            raise ValueError("Entry ID is invalid.")

        username = self.get_username(access_token)

        entry = next(e for e in settings.entries if e["id"] == entry_id)
        entry_copy = copy.deepcopy(entry)

        # We are able to inject entry_id directly below as we check it is in the country_codes.
        select_command = "SELECT `" + entry_id + "` FROM scores WHERE username = %s"
        select_params = (username, )
        cursor = self.execute(select_command, select_params)

        score = cursor.fetchone()[0]

        entry["attributes"]["score"] = score
        return entry

    ################################################################################################
    def generate_entries_dictionary(self, access_token):
        """ Generates the entries dictionary.

        Args:
            access_token (str): The access token the client has sent.

        Returns:
            str: The entries dictionary.
        """
        username = self.get_username(access_token)

        entries_copy = copy.deepcopy(settings.entries)

        select_command = "SELECT * FROM scores WHERE username = %s"
        select_params = (username, )
        cursor = self.execute(select_command, select_params)

        column_names = [c[0] for c in cursor.description]
        user_scores = dict(zip(column_names, cursor.fetchone()))

        for entry in entries_copy:
            entry_id = entry["id"]
            entry["attributes"]["score"] = user_scores[entry_id]

        return entries_copy

    ################################################################################################
    def generate_settings_dictionary(self, access_token):
        """ Generates the settings dictionary.

        Args:
            access_token (str): The access token the client has sent.

        Returns:
            str: The entries dictionary.
        """
        username = self.get_username(access_token)

        user_settings_copy = copy.deepcopy(settings.user_settings)

        select_command = "SELECT theme FROM users WHERE username = %s"
        select_params = (username, )
        cursor = self.execute(select_command, select_params)

        column_names = [c[0] for c in cursor.description]
        database_settings = dict(zip(column_names, cursor.fetchone()))

        for setting in user_settings_copy:
            setting["attributes"]["value"] = database_settings[setting["attributes"]["setting"]]

        return user_settings_copy
