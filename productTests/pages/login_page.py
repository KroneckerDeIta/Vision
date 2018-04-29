""" Methods that interact with the login page and cover both logging in and registering a user. """


####################################################################################################
def select_to_register(driver):
    """ On the login page select to register instead of login.

    Args:
        :param driver: The webdriver instance.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
    """
    driver.find_element_by_id("register-text-id").click()


####################################################################################################
def enter_username(driver, username):
    """ Enter the username.

    Args:
        :param driver: The webdriver instance.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
        :param username: The username of the user to register.
        :type username: str
    """
    input_field = driver.find_element_by_id("username-input-id")
    input_field.clear()
    input_field.send_keys(username)


####################################################################################################
def enter_password(driver, password):
    """ Enter the password.

    Args:
        :param driver: The webdriver instance.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
        :param password: The password of the user to register.
        :type password: str
    """
    input_field = driver.find_element_by_id("password-input-id")
    input_field.clear()
    input_field.send_keys(password)


####################################################################################################
def enter_confirm_password(driver, password):
    """ Enter the confirm password.

    Args:
        :param driver: The webdriver instance.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
        :param password: The password of the user to register.
        :type password: str
    """
    input_field = driver.find_element_by_id("confirm-password-input-id")
    input_field.clear()
    input_field.send_keys(password)


####################################################################################################
def confirm_registration(driver):
    """ Confirm the registration of the user.

    Args:
        :param driver: The webdriver instance.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
    """
    driver.find_element_by_id("login-confirmation-button-id").click()


####################################################################################################
def confirm_login(driver):
    """ Confirm the login of the user.

    Args:
        :param driver: The webdriver instance.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
    """
    driver.find_element_by_id("login-confirmation-button-id").click()
