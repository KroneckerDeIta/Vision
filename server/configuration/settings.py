import json
import logging
import os
import sys

__author__ = "Thomas Henry Reeve"

if getattr(sys, 'frozen', False):
    CONFIGURATION_DIRECTORY = os.path.dirname(sys.executable)
else:
    CONFIGURATION_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


####################################################################################################
def setup_custom_logger(name):
    """ Setup a custom logger.

    Args:
        name (str): The name of the module you are setting the logger up for.

    Returns:
        A logger.
    """

    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # Use logging.StreamHandler() to log to stdout and logging.FileHandler() to log to a file.
    handler = logging.StreamHandler(stream=sys.stdout)
    # handler = logging.FileHandler(filename="/tmp/Vision.log")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


####################################################################################################
# Password salting configuration. Changing these values will invalidate the passwords in the
# database.
PASSWORD_SALTING_ROUNDS = 10000
PASSWORD_SALTING_SIZE = 16
# Should be plenty to store the type of theme.
THEME_LENGTH = 100

####################################################################################################
# The port number on which to access the Vision web page (note this will be mapped through to a
# different port number on the host machine as this will run in a Docker container).
PORT = 15555
CLEAR_DATABASE = False

####################################################################################################
# The Database configuration.
DATABASE_USER = "vision"
DATABASE_PASSWORD = "visionpass"
DATABASE_NAME = "visiondb"
DATABASE_HOST = "localhost"

MAX_USERNAME_LENGTH = 20
PASSWORD_HASH_LENGTH = 2000  # Far greater than the string generated by passlib.hash.

MAXIMUM_SCORE = 10

UPDATE_TIMEOUT = 10000  # Update every 10 seconds. We don't need to update too often.

UUID_LENGTH = 36  # The length of a UUID. Used for access or refresh token.

REFRESH_EXPIRY_SECONDS = 60 * 24 * 60 * 60  # The refresh token will last for 60 days.

ACCESS_EXPIRY_SECONDS = 24 * 60 * 60  # The access token will last for a day.

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

####################################################################################################
# The information about the entries.
# This variable will be populated by the server using an entries json file.
# The score will be updated based on the value in the database.
ENTRIES_JSON = os.path.join(CONFIGURATION_DIRECTORY, "entries.json")
with open(ENTRIES_JSON, 'r') as entries_json_file:
    entries = json.load(entries_json_file)

####################################################################################################
country_codes = [entry["id"] for entry in entries]

####################################################################################################
# The default settings. The settings will be updated based on values in the database on get
# requests.
user_settings = [
    {
        "id" : "1",
        "type" : "settings",
        "attributes" : {
            "setting": "theme",
            "value": "ocean"
        }
    }
];
