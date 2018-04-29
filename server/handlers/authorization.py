import json
import tornado.web
import traceback

import configuration.settings as settings

__author__ = "Thomas Henry Reeve"
""" Module for handling requests for authorization. """

logger = settings.setup_custom_logger(__name__)


####################################################################################################
def get_access_token(request):
    """ Retrieves the access token from the authorized message that will be sent in request headers.

    Args:
        request: The request that was sent.

    Returns:
        The access token.
    """
    authorization = request.headers.get('authorization')
    return authorization.replace("Bearer ", "", 1)


####################################################################################################
class RegisterHandler(tornado.web.RequestHandler):
    """ Handles requests to register. """
    ################################################################################################
    def _handle_request_exception(self, exc):
        """ Handles a request exception. """
        # Log the exception otherwise we won't see it!
        logger.error(traceback.format_exc())
        # Call the import traceback parent handler.
        RegisterHandler._handle_request_exception(self, exc)

    ################################################################################################
    def post(self):
        """ Handles register requests. The user submits a username and password. """
        username = self.get_argument('username', None, strip=False)
        password = self.get_argument('password', None, strip=False)

        self.register_user(username, password)

    ################################################################################################
    def register_user(self, username, password):
        """ Registers the user.

        Args:
            username (str): The user's username.
            password (str): The user's password.
        """
        try:
            self.application.database_connector.register_user(username, password)
            self.set_status(200)
            access_info = self.application.database_connector.get_access_information(username)
            self.write(json.dumps(access_info))
        except (LookupError, ValueError) as error:
            logger.error(traceback.format_exc())
            self.set_status(400)
            self.write(json.dumps(str(error)))


####################################################################################################
class TokenHandler(tornado.web.RequestHandler):
    """ Handles requests to login. """
    ################################################################################################
    def _handle_request_exception(self, exc):
        """ Handles a request exception. """
        # Log the exception otherwise we won't see it!
        logger.error(traceback.format_exc())
        # Call the import traceback parent handler.
        TokenHandler._handle_request_exception(self, exc)

    ################################################################################################
    def post(self):
        """ Handles token requests. The user submits a username and password. """
        username = self.get_argument('username', None, strip=False)
        password = self.get_argument('password', None, strip=False)

        self.login_user(username, password)

    ################################################################################################
    def login_user(self, username, password):
        """ Logs the user in.

        Args:
            username (str): The user's username.
            password (str): The user's password.
        """
        try:
            self.application.database_connector.login_user(username, password)
            self.set_status(200)
            access_info = self.application.database_connector.get_access_information(username)
            self.write(json.dumps(access_info))
        except ValueError as error:
            logger.error(traceback.format_exc())
            self.set_status(400)
            self.write(json.dumps(str(error)))
