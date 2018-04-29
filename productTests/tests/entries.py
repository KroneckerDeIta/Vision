import unittest

from productTests.steps import register
from productTests.utilities import application, generate_entries, webdriver


####################################################################################################
class TestEntries(unittest.TestCase):
    """ Tests actions on the login page. """
    ################################################################################################
    def setUp(self):
        """ Creates the application and webdriver. """
        entries = generate_entries.generate_number_of_entries(24)
        self.__application = application.Application(entries)
        self.__application.start()
        self.__driver = webdriver.create(self.__application.get_url())

    ################################################################################################
    def tearDown(self):
        """ Stops the application and webdriver. """
        self.__driver.quit()
        self.__application.stop()

    ################################################################################################
    def test_register_logout_and_login(self):
        """ Tests that a user can enter scores. """
        username = "Dave"
        password = "password"

        register.with_credentials(self.__driver, username, password)


####################################################################################################
if __name__ == '__main__':
    unittest.main()
