import tornado.web

__author__ = "Thomas Henry Reeve"
""" Module for rendering the index page. """


####################################################################################################
class IndexHandler(tornado.web.RequestHandler):
    ################################################################################################
    @tornado.web.asynchronous
    def get(self):
        self.render("../dist/index.html")
