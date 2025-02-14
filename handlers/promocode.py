from handlers.login import login
from handlers.get_item import get_chest, activated_items, select_character
from exceptions.exception import InvalidEmail

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from handlers.driver import get_driver
from logger_conf import get_logger

logger = get_logger("logger")


def activate_promocode(root, text_box, character, promocodes, chest_list, locked_list):
    driver, wait = get_driver()
    try:
        text_box.insert("end", 'Переходим по ссылке https://pwonline.ru\n')
        logger.info("Переходим по ссылке https://pwonline.ru")
        root.update_idletasks()
        driver.get('https://pwonline.ru')
        start_page = driver.current_window_handle
        flag = login(account=character, driver=driver, wait=wait, text_box=text_box, root=root)
        if not flag:
            raise InvalidEmail
        driver.switch_to.window(start_page)

        for promocode in promocodes:
            text_box.insert("end", f'Активация промокода {promocode}\n')
            logger.info(f"Активация промокода {promocode}")
            root.update_idletasks()
            driver.get(f'https://pwonline.ru/pin/{promocode}')
            activate_btn = wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'pin_code_input')))
            activate_btn.send_keys('', Keys.ENTER)

        text_box.insert("end", 'Переходим на страницу передачи предметов\n')
        logger.info(f"Переходим на страницу передачи предметов")
        root.update_idletasks()
        driver.get('https://pwonline.ru/promo_items.php')
        chest_flag = get_chest(
            driver=driver,
            root=root,
            text_box=text_box,
            chest_list=chest_list
        )
        if not chest_flag:
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
            return True
    except InvalidEmail:
        text_box.insert("end", 'Необходимо ввести адрес резервной эл.почты\n\n\n')
        logger.info(f"Необходимо ввести адрес резервной эл.почты. {character.nickname}")
        root.update_idletasks()
        driver.quit()
        return False
    except Exception as e:
        log_msg = f"Не опознанная ошибка: {character.nickname}"
        text_box.insert("end", log_msg)
        logger.error(log_msg)
        driver.quit()
        return False

