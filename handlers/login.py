from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException as TES


def login_mail(driver, login_page, account, wait, root, text_box):
    try:
        text_box.insert("end", f'Начало авторизации Mail. Персонаж {account.nickname}\n')
        root.update_idletasks()
        driver.switch_to.window(driver.window_handles[-1])
        search_btn = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'ph-social-btn_mailru')))
        search_btn.click()
        driver.switch_to.window(driver.window_handles[-1])
        input_email = wait.until(EC.presence_of_element_located(
            (By.NAME, 'username')))
        input_email.send_keys(account.email, Keys.ENTER)
        driver.implicitly_wait(10)
        input_pwd = wait.until(EC.presence_of_element_located(
            (By.NAME, 'password')))
        input_pwd.send_keys(account.password, Keys.ENTER)
        driver.switch_to.window(login_page)
        resume_btn = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'ph-btn_main')))
        resume_btn.click()
        text_box.insert("end", 'Авторизация Mail успешно завершена\n')
        root.update_idletasks()
        return True
    except TES:
        driver.switch_to.window(driver.window_handles[-1])
        text = 'Это точно вы?'
        if text in driver.page_source:
            return False


def login_straight(account, wait, root, text_box):
    text_box.insert("end", f'Начало авторизации на сайте. Персонаж {account.nickname}\n')
    root.update_idletasks()
    input_email = wait.until(EC.presence_of_element_located(
        (By.NAME, 'login')))
    input_pwd = wait.until(EC.presence_of_element_located(
        (By.NAME, 'password')))
    input_email.send_keys(account.email)
    input_pwd.send_keys(account.password)
    login_btn = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'gtm_login_btn')))
    login_btn.click()
    resume_btn = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'ph-btn_main')))
    resume_btn.click()
    text_box.insert("end", 'Авторизация на сайте успешно завершена\n')
    root.update_idletasks()


def login(account, driver, wait, root, text_box):
    driver.switch_to.window(driver.window_handles[0])
    login_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CLASS_NAME, "login-button")))
    login_btn.click()
    login_page = driver.window_handles[1]
    driver.switch_to.window(login_page)
    if account.type_auth.tech_name == 'mail':
        return login_mail(driver, login_page, account, wait, root, text_box)
    elif account.type_auth.tech_name == 'straight':
        return login_straight(account, wait, root, text_box)