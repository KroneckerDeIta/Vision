from productTests.pages import side_menu


####################################################################################################
def of_application(driver):
    """ Logs out of the application. This method assumes we need to open the menu first.

    Args:
        :param driver: The webdriver instance.
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
    """
    side_menu.open_menu(driver)
    side_menu.logout(driver)
