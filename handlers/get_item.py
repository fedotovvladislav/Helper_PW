from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import NoSuchElementException
from time import sleep


def get_chest(driver, root, text_box, chest_list):
    text_box.insert("end", "Ищем нужные сундуки с функцией активации\n")
    root.update_idletasks()
    elements = driver.find_elements(by=By.CLASS_NAME, value='chest_input_block')
    for element in elements:
        for chest_item in chest_list:
            if chest_item.chest_name in element.text:
                text_box.insert("end", f"Найден сундук {element.text}\n")
                root.update_idletasks()
                exist = element.find_element(by=By.CLASS_NAME, value="chest_activate_red")
                exist.click()
                chests = driver.find_elements(by=By.TAG_NAME, value='label')
                for chest in chests:
                    if chest_item.item_chest_name in chest.text:
                        text_box.insert("end", f"Выбран предмет {chest.text}\n")
                        root.update_idletasks()
                        chest.click()
                        break

                activate = driver.find_element(by=By.CLASS_NAME, value="chest_submit_button")
                activate.click()
                break


def activated_items(driver, text_box, root, locked_list):
    js_code = "$('.items_container input[type=checkbox]').click(function(){\n" \
              'var n = $(".items_container input:checked").length;\nif(n >= 10000000000) {\n' \
              '$(".items_container input[type=checkbox]:not(:checked)").attr("disabled", "disabled");\n' \
              '}\nelse {\n$("input[type=checkbox], input[type=submit]").removeAttr("disabled");\n}\n});\n' \
              "$('.item_input_block').mouseover(function(){\n" \
              "if($(this).find('input[type=checkbox]:not(:checked)').is(':disabled')){\n$('.descr_block').show();\n" \
              '}\nelse {\n' \
              "$('.descr_block').hide();\n" \
              '}\n});\n\n' \
              "var check=document.getElementsByTagName('input');\n" \
              'for(var i=0;i<check.length;i++)\n{\n' \
              "if(check[i].type=='checkbox')\n" \
              '{\ncheck[i].checked=true;\n}\n}\n'
    driver.execute_script(js_code)

    items = driver.find_elements(by=By.CLASS_NAME, value='item_input_block')
    text_box.insert("end", "Убираем итемы из блок листа\n")
    root.update_idletasks()
    for item in items:
        for block_item in locked_list:
            if block_item.item_name in item.text:
                item.click()
    else:
        text_box.insert("end", "Итемы успешно удалены\n")
        root.update_idletasks()


def select_character(driver, character, text_box, root):
    text_box.insert("end", "Выбираем сервер\n")
    root.update_idletasks()
    drop = Select(driver.find_element(by=By.CLASS_NAME, value='js-shard'))
    try:
        drop.select_by_visible_text(text=character.server.name)
    except NoSuchElementException:
        text_box.insert("end", f"Для данного аккаунта сервер {character.server.name} недоступен\n")
        root.update_idletasks()

    drop = Select(driver.find_element(by=By.CLASS_NAME, value='js-char'))
    for opt in drop.options:
        if character.nickname in opt.text:
            drop.select_by_visible_text(text=opt.text)
            text_box.insert("end", f"Выбран персонаж {opt.text}\n")
            root.update_idletasks()
            driver.find_element(by=By.CLASS_NAME, value='go_items').click()
            text_box.insert("end", f"Подарки переведены персонажу {character.nickname} на сервер "
                                   f"{character.server.name}\n\n\n")
            root.update_idletasks()
            break
    else:
        text_box.insert("end", f"Персонаж {character.nickname} не обнаружен\n\n\n")
        root.update_idletasks()
