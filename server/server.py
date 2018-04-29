import MySQLdb
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
import tornado.web

import configuration.settings as settings
# Set up the logging configuration.
from database import connector
from handlers import entries, update, index, authorization, user_settings

__author__ = "Thomas Henry Reeve"
""" Initialises the Vision database. """

logger = settings.setup_custom_logger(__name__)

define("reset_database", default=False, type=bool, help="Whether the database should be reset.")


####################################################################################################
def start_server():
    """ Starts the server using command line options and entries in the settings file. """
    options.parse_command_line()

    database_connection = MySQLdb.connect(host=settings.DATABASE_HOST,
                                          user=settings.DATABASE_USER,
                                          passwd=settings.DATABASE_PASSWORD)
    database_connector = connector.DatabaseConnector(database_connection)

    database_exists = database_connector.does_database_exist(settings.DATABASE_NAME)

    if not database_exists or options.reset_database:
        if database_exists:
            database_connector.drop_database(settings.DATABASE_NAME)
        database_connector.create_database(settings.DATABASE_NAME)
        database_connector.use_database(settings.DATABASE_NAME)

        database_connector.create_users_table()
        database_connector.create_scores_table(settings.country_codes)
        database_connector.create_access_table()

    # Regardless of whether we reset the database we still need to use the database.
    database_connector.use_database(settings.DATABASE_NAME)

    # Setup the app.
    application = tornado.web.Application([
        (r'/constants.js()', tornado.web.StaticFileHandler, {"path": "dist/constants.js"}),
        (r'/assets/(.*)', tornado.web.StaticFileHandler, {"path": "dist/assets"}),
        (r'/fonts/(.*)', tornado.web.StaticFileHandler, {"path": "dist/fonts"}),
        (r'/images/(.*)', tornado.web.StaticFileHandler, {"path": "dist/images"}),
        (r'/api/token', authorization.TokenHandler),
        (r'/api/register', authorization.RegisterHandler),
        (r'/api/settings', user_settings.UserSettingsHandler),
        (r'/api/entries', entries.EntriesHandler),
        (r'/api/entries/(.*)', entries.EntryHandler),
        (r'/update', update.UpdateHandler),
        (r'/.*', index.IndexHandler)
    ])

    application.database_connector = database_connector

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(settings.PORT)

    logger.info("Starting Server")

    tornado.ioloop.IOLoop.current().start()


####################################################################################################
if __name__ == '__main__':
    start_server()
