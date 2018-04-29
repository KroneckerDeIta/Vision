import json
import tornado.web
import traceback

from . import authorization
import configuration.settings as settings
from database import connector

__author__ = "Thomas Henry Reeve"
""" Module for handling requests to entries. """

logger = settings.setup_custom_logger(__name__)


####################################################################################################
class UserSettingsHandler(tornado.web.RequestHandler):
    """ Handles requests to entries. """
    ################################################################################################
    def _handle_request_exception(self, exc):
        """ . """
        # Log the exception otherwise we won't see it!
        logger.error(traceback.format_exc())
        # Call the import traceback parent handler.
        UserSettingsHandler._handle_request_exception(self, exc)

    ################################################################################################
    def get(self):
        """ Handles getting user settings requests. """
        try:
            access_token = authorization.get_access_token(self.request)
            user_settings = self.application.database_connector.generate_settings_dictionary(
                access_token)
            self.set_status(200)
            self.write(json.dumps({"data": user_settings}))
        except connector.InvalidAccessTokenException as error:
            logger.error(traceback.format_exc())
            self.set_status(401)
            self.write(json.dumps(str(error)))