from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc


def get_driver():
    options = uc.ChromeOptions()
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False}
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    options.add_experimental_option("prefs", prefs)
    # options.add_argument('--headless')
    driver = uc.Chrome(use_subprocess=True, options=options)
    wait = WebDriverWait(driver, 10)

    return driver, wait