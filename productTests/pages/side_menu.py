""" Methods that interact with the side menu. """


####################################################################################################
def open_menu(driver):
    """ Opens the side menu.  Assumes you are on a page with a side menu.

    Args:
        :param driver: The webdriver instance.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
    """
    driver.find_element_by_id("entries-menu-button").click()


####################################################################################################
def logout(driver):
    """ Logs out of the application. This method assumes we have opened the side menu.

    Args:
        :param driver: The webdriver instance.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
    """
    driver.find_element_by_id("side-menu-logout").click()
