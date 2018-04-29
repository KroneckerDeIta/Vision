import datetime
import json
import tornado.websocket
import traceback

import configuration.settings as settings

logger = settings.setup_custom_logger(__name__)


####################################################################################################
clients = {}


####################################################################################################
class UpdateHandler(tornado.websocket.WebSocketHandler):
    ################################################################################################
    def open(self, *args):
        try:
            # Setting this can reduce performance, but messages are sent straight away. We are not
            # sending lots of data so we should be fine.
            self.stream.set_nodelay(True)
            clients[self] = {}
            results = self.application.database_connector.generate_results_dictionary(
                settings.country_codes)

            self.write_message(json.dumps({
                "type": "results",
                "results": results
            }))

            logger.debug("Connection opened.")
        except Exception as err:
            logger.error(traceback.format_exc())
            raise err

    ################################################################################################
    def on_close(self):
        try:
            if self in clients:
                logger.debug("Connection closed.")
                del clients[self]
        except Exception as err:
            logger.error(traceback.format_exc())
            raise err

    ################################################################################################
    def on_message(self, message):
        logger.debug("Websocket message received: " + str(message))

        message_json = json.loads(message)
        access_token = message_json["access_token"]
        username = message_json["username"]

        if self.application.database_connector.is_access_token_valid(username, access_token):
            # We need to update the information about this client so that we can send messages
            # to particular clients and close connections based on the username and
            # access token.
            if "username" not in clients[self]:
                clients[self]["username"] = username
            if "access_token" not in clients[self]:
                clients[self]["access_token"] = access_token

            message_type = message_json["type"]

            if message_type == "refresh_token":
                self.__handle_refresh_token(message_json)
            else:
                logger.warn("Unrecognised type in message: " + str(message))
        else:
            logger.warn("Invalid access token in message: " + str(message))
            close_connections(access_token="Session Expired")

    ################################################################################################
    def __handle_refresh_token(self, message_json):
        refresh_token = message_json["refresh_token"]
        access_token = message_json["access_token"]
        username = message_json["username"]
        if self.application.database_connector.is_refresh_token_valid(username, refresh_token):
            self.application.database_connector.extend_access_expiry(username, access_token)

            access_info = self.application.database_connector.get_access_information(username)

            current_datetime = datetime.datetime.now()
            expiry_datetime = datetime.datetime.strptime(access_info["access_token_expiry"],
                                                         settings.DATETIME_FORMAT)
            expiry_seconds = (expiry_datetime - current_datetime).total_seconds()

            self.write_message(json.dumps({
                "type": "access_token_expiry",
                "access_token_expiry": expiry_seconds
            }))
        else:
            logger.warn("Invalid refresh token in message: " + str(message_json))
            close_connections(access_token=access_token, reason="Session Expired")


####################################################################################################
def broadcast_message(message, access_token=None):
    """ Broadcast a message to all clients.

    Args:
        message (str): The message to broadcast.
        access_token (str): The access token of the client to send the message to, otherwise a
        message will be sent to every client.
    """
    for client in clients:
        client_access_token = clients[client].get("access_token")
        if (access_token is None and client_access_token is not None) or \
                access_token == client_access_token:
            client.write_message(message)


####################################################################################################
def close_connections(username=None, access_token=None, reason=None):
    """ Close connections.

    Args:
        username (str): The username of the clients to close.
        access_token (str): The access_token of the clients to close.
        reason (str): The reason the connections have been closed.
    """
    clients_to_close = set()

    for client in clients:
        client_username = clients[client].get("username")
        client_token = clients[client].get("access_token")

        if client_username is not None and username is not None and client_username == username:
            clients_to_close.add(client)

        if client_token is not None and access_token is not None and client_token == access_token:
            clients_to_close.add(client)

    for client in clients_to_close:
        client.close(reason=reason)
        clients.pop(client)
