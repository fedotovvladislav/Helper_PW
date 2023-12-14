from handlers.login import login
from handlers.get_item import get_chest, activated_items, select_character
from exceptions.exception import InvalidEmail
from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from handlers.driver import get_driver


def activate_promocode(root, text_box, character, promocodes, chest_list, locked_list):
    driver, wait = get_driver()
    try:
        text_box.insert("end", 'Переходим по ссылке https://pwonline.ru\n')
        root.update_idletasks()
        driver.get('https://pwonline.ru')
        start_page = driver.current_window_handle
        flag = login(account=character, driver=driver, wait=wait, text_box=text_box, root=root)
        if not flag:
            raise InvalidEmail
        driver.switch_to.window(start_page)

        for promocode in promocodes:
            text_box.insert("end", f'Активация промокода {promocode}\n')
            root.update_idletasks()
            driver.get(f'https://pwonline.ru/pin/{promocode}')
            activate_btn = wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'pin_code_input')))
            activate_btn.send_keys('', Keys.ENTER)

        text_box.insert("end", 'Переходим на страницу передачи предметов\n')
        root.update_idletasks()
        driver.get('https://pwonline.ru/promo_items.php')
        get_chest(
            driver=driver,
            root=root,
            text_box=text_box,
            chest_list=chest_list
        )
        activated_items(
            driver=driver,
            text_box=text_box,
            root=root,
            locked_list=locked_list
        )
        select_character(
            driver=driver,
            character=character,
            text_box=text_box,
            root=root
        )
        driver.quit()
    except InvalidEmail:
        text_box.insert("end", 'Необходимо ввести адрес резервной эл.почты\n\n\n')
        root.update_idletasks()
        sleep(300)
        driver.quit()
    finally:
        return True