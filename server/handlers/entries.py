import json
import tornado.escape
import tornado.web
import traceback

from . import authorization
from . import update
import configuration.settings as settings
from database import connector

__author__ = "Thomas Henry Reeve"
""" Module for handling requests to entries. """

logger = settings.setup_custom_logger(__name__)


####################################################################################################
class EntriesHandler(tornado.web.RequestHandler):
    """ Handles requests to entries. """
    ################################################################################################
    def _handle_request_exception(self, exc):
        """ Handles a request exception. """
        # Log the exception otherwise we won't see it!
        logger.error(traceback.format_exc())
        # Call the import traceback parent handler.
        EntriesHandler._handle_request_exception(self, exc)

    ################################################################################################
    def get(self):
        """ Handles getting all entries requests. """
        try:
            access_token = authorization.get_access_token(self.request)
            entries = self.application.database_connector.generate_entries_dictionary(access_token)
            self.set_status(200)
            self.write(json.dumps({"data": entries}))
        except connector.InvalidAccessTokenException as error:
            logger.error(traceback.format_exc())
            self.set_status(401)
            self.write(json.dumps(str(error)))


####################################################################################################
class EntryHandler(tornado.web.RequestHandler):
    """ Handles requests to an entry. """
    ################################################################################################
    def _handle_request_exception(self, exc):
        """ . """
        # Log the exception otherwise we won't see it!
        logger.error(traceback.format_exc())
        # Call the import traceback parent handler.
        EntryHandler._handle_request_exception(self, exc)

    ################################################################################################
    def get(self, sub_path):
        """ Gets a single entry.

        :param sub_path: The path after the path defined in the routes containing the entry ID.
        :type sub_path: str
        """
        try:
            access_token = authorization.get_access_token(self.request)
            entry_id = sub_path
            entry = self.application.database_connector.get_entry(access_token, entry_id)
            self.set_status(200)
            self.write(json.dumps({"data": entry}))
        except connector.InvalidAccessTokenException as error:
            logger.error(traceback.format_exc())
            self.set_status(401)
            self.write(json.dumps(str(error)))

    ################################################################################################
    def patch(self, sub_path):
        """ Updates the score for the entry.

        :param sub_path: The path after the path defined in the routes containing the entry ID.
        :type sub_path: str
        """
        try:
            access_token = authorization.get_access_token(self.request)
            entry_id = sub_path
            
            if entry_id not in settings.country_codes:
                self.set_status(404)
                return

            request = tornado.escape.json_decode(self.request.body)
            if request["update"] == "score":
                new_score = request["score"]

                self.application.database_connector.update_score(access_token, entry_id, new_score)
                self.set_status(200)

                results = self.application.database_connector.generate_results_dictionary([entry_id])

                update.broadcast_message(json.dumps({
                    "type": "results",
                    "results": results
                }))

                update.broadcast_message(json.dumps({
                    "type": "scoreUpdate",
                    "scoreUpdate": {
                        "id": entry_id,
                        "score": new_score
                    }
                }), access_token)
            else:
                self.set_status(500)
                self.write("Unknown update type")
        except connector.InvalidAccessTokenException as error:
            logger.error(traceback.format_exc())
            self.set_status(401)
            self.write(json.dumps(str(error)))

