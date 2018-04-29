""" Module which contains a class which represents a user directly interacting with the server. """
import json
import requests

from productTests import settings


####################################################################################################
class ServerUser:
    """ Object which stores information about a server user. """
    ################################################################################################
    def __init__(self, username, password):
        """ Constructor. The user will be registered with the server.

        :param username: The username of the server user.
        :type username: str
        :param password: The password of the server user.
        :type password: str
        """
        self.__username = username
        self.__password = password

        self.__access_token = None
        self.__access_token_expiry = None
        self.__refresh_token = None
        self.__register()

    ################################################################################################
    def __register(self):
        """ Registers the user with the server. """
        params = {
            "username": self.__username,
            "password": self.__password
        }
        response = requests.post(settings.registration_endpoint, data=params)
        json_response = json.loads(response.text)
        self.__access_token = json_response["access_token"]
        self.__access_token_expiry = json_response["access_token_expiry"]
        self.__refresh_token = json_response["refresh_token"]

    ################################################################################################
    def __headers(self):
        """ The headers that are sent with requests. """
        return {
            "Authorization": "Bearer " + self.__access_token
        }

    ################################################################################################
    def get_entries(self):
        """ Gets the entries for the user. """
        response = requests.get(settings.entries_endpoint, headers=self.__headers())
        print("ENTRIES:", response.text)

    ################################################################################################
    def update_score(self, entry_id, score):
        """ Updates the score of an entry. """
        data = {
            "update": "score",
            "score": score
        }
        response = requests.patch(settings.entries_endpoint + "/" + str(entry_id), json=data,
                                  headers=self.__headers())
