from productTests.pages import login_page


####################################################################################################
def with_credentials(driver, username, password):
    """ Registers a user with credentials.

    Args:
        :param driver: The webdriver instance.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
        :param username: The username of the user to register.
        :type username: str
        :param password: The password of the user to register.
        :type password: str
    """
    login_page.select_to_register(driver)
    login_page.enter_username(driver, username)
    login_page.enter_password(driver, password)
    login_page.enter_confirm_password(driver, password)
    login_page.confirm_registration(driver)
