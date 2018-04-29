from random import randint
import time
import unittest

from productTests.steps import register, login, logout
from productTests.utilities import application, generate_entries, webdriver
from productTests.utilities.server_user import ServerUser

####################################################################################################
class TestAuthentication(unittest.TestCase):
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
        """ Tests that a user can register, logout, login, and finally logout. """
        username = "Dave"
        password = "password"

        register.with_credentials(self.__driver, username, password)

        #user = ServerUser("Pete", "password")
        #user.get_entries()
        # for j in range(0, 10000):
        #     identifier = randint(0, 24)
        #     score = randint(0, 10)
        #     user.update_score(identifier, score)

        logout.of_application(self.__driver)

        login.with_credentials(self.__driver, username, password)
        logout.of_application(self.__driver)


####################################################################################################
if __name__ == '__main__':
    unittest.main()
