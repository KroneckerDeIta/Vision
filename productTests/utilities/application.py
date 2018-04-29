import json
import os
import re

from productTests import settings
import subprocess
import tempfile


####################################################################################################
class Application(object):
    """ Class used to create and perform actions on an application. """
    ################################################################################################
    def __init__(self, entries=None):
        self.__url = settings.application_endpoint
        self.__process = None

        self.__start_command = Application.__get_environment_variable('APPLICATION_START_COMMAND')
        self.__stop_command = Application.__get_environment_variable('APPLICATION_STOP_COMMAND')
        self.__settings_path = Application.__get_environment_variable('VISION_SETTINGS_PATH')

        with open(self.__settings_path, 'r') as settings_file:
            self.__original_content = settings_file.read()

        self.__update_entries(entries)
        self.__update_database_name()

    ################################################################################################
    @staticmethod
    def __get_environment_variable(variable):
        """ Returns the environment variable, raises if not set. """
        result = os.environ[variable]
        if not result:
            raise Exception(variable + " environment variable not set.")
        return result

    ################################################################################################
    def __update_entries(self, entries=None):
        """ If entries are provided creates a temporary entries file, and changes the
        settings.py file to look at this file. """
        if entries:
            self.__entries_json = tempfile.NamedTemporaryFile()
            with open(self.__entries_json.name, 'w') as entries_json:
                json.dump(entries, entries_json)
            os.environ['VISION_ENTRIES_JSON'] = self.__entries_json.name

    ################################################################################################
    def __update_database_name(self):
        """ Updates the DATABASE_NAME variable in settings.py. """
        # Hard coded database that is already setup.
        self.update_settings("DATABASE_NAME", '"visiondb"')

    ################################################################################################
    def start(self, reset_database=True):
        """ Starts the application.

        Args: reset_database (bool): Whether the database should be restarted.
        """
        start_command = self.__start_command
        if reset_database:
            start_command += " -r"
        with open(os.devnull, 'wb') as dev_null:
            self.__process = subprocess.Popen(start_command, shell=True, stdout=dev_null,
                                              stderr=subprocess.STDOUT)

    ################################################################################################
    def stop(self):
        """ Stops the application. """
        with open(os.devnull, 'wb') as dev_null:
            subprocess.call(self.__stop_command, shell=True, stdout=dev_null,
                            stderr=subprocess.STDOUT)
        self.__process.kill()

    ################################################################################################
    def get_url(self):
        """ Gets the URL for the application. """
        return self.__url

    ################################################################################################
    def restore_settings(self):
        """ Restores the settings file to the state it was in when this Application object was
        created. """
        with open(self.__settings_path, 'w') as settings_file:
            settings_file.write(self.__original_content)

    ################################################################################################
    def update_settings(self, variable, value):
        """ Updates the settings.py file.

        Args:
            variable: The variable to update.
            value: The value to set the variable to.
        """
        with open(self.__settings_path, 'r+') as settings_file:
            content = settings_file.read()
            settings_file.seek(0)
            content = re.sub(r'^('+variable+' *= *).*$', r'\g<1>'+value, content,
                             flags=re.MULTILINE)
            settings_file.write(content)
            settings_file.truncate()
