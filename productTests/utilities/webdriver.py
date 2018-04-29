from selenium import webdriver


####################################################################################################
def create(url):
    """ Creates a webdriver.

    Args:
        url: The URL the webdriver will open on startup.
    """
    driver = webdriver.Firefox()
    driver.get(url)
    return driver
