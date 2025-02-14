from customtkinter import (
    CTkFrame, CTkButton, DISABLED, CTk,
    set_appearance_mode, CTkLabel, CTkFont,
    CTkEntry, CTkCheckBox, CTkComboBox, END,
    StringVar, CTkTextbox, CTkProgressBar
)
from CTkListbox import *
from time import sleep

from database.models import *
from handlers.initial_item import initial
from handlers.promocode import activate_promocode
from logger_conf import get_logger

logger = get_logger("logger")


class CustomButton(CTkButton):
    def __init__(self, root, **kw):
        super().__init__(root, corner_radius=30, **kw)
        self.id = None

    def grid(self, padx=5, pady=5, ipadx=20, ipady=20, sticky='ew', **kw):
        super().grid(padx=padx, pady=pady, ipadx=ipadx, ipady=ipady,
                     sticky=sticky, **kw)


class HelperCRUD(CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.view_model = None
        self.current_command = self.main_window
        self.prev_command = None
        self.prev_prev_command = None
        self.font_title = CTkFont(family='Impact', size=25, weight='bold')
        self.font_lable = CTkFont(family='Impact', size=13, weight='bold')
        self.widgets = dict()

    def main_window(self):
        self.widgets["promocode_btn"].grid(row=2, column=2, columnspan=4)
        self.widgets["marathon_btn"].grid(row=3, column=2, columnspan=4)
        self.widgets["characters_btn"].grid(row=4, column=2, columnspan=4)
        self.widgets["settings_btn"].grid(row=5, column=2, columnspan=2)
        self.widgets["quit"].grid(row=5, column=4, columnspan=2)

    def remove_all(self):
        for key, value in self.widgets.items():
            value.grid_remove()
            if isinstance(value, CTkEntry):
                value.delete(0, END)
            elif isinstance(value, CTkListbox) and value.size() > 0:
                value.delete(0, END)
            elif isinstance(value, CTkTextbox):
                value.delete("0.0", "end")

    def next_command(self, command_next=None, *args, default=None, back=False, **kwargs):
        self.remove_all()
        if self.current_command is None:
            self.current_command = self.main_window
        if default is not None:
            self.prev_prev_command = None
            self.current_command = self.prev_command
            self.prev_command = default
            return self.current_command(*args, **kwargs)
        elif back:
            self.current_command = self.prev_command
            self.prev_command = self.prev_prev_command
            self.prev_prev_command = self.main_window
            return self.current_command()
        else:
            self.prev_prev_command = self.prev_command
            self.prev_command = self.current_command
            self.current_command = command_next

        return self.current_command(*args, **kwargs)

    def delete_item_db(self, element, func, *args, **kwargs):
        self.remove_all()
        with db.atomic():
            element.delete_instance()
        return func(*args, **kwargs)

    def update_item_db(self, element):
        new_values = self.new_values()
        with db.atomic():
            self.view_model.update(**new_values).where(self.view_model.id == element.id).execute()
        return self.next_command(back=True)

    def create_item_db(self):
        new_values = self.new_values()
        with db.atomic():
            self.view_model.create(**new_values)
        return self.next_command(back=True)

    def create_or_update_frame(self, element=None):
        self.widgets["title"].configure(text=self.view_model.get_title())
        self.widgets["title"].grid(row=0, column=0, columnspan=8, sticky='nwne')
        list_item = self.view_model.get_labels()
        start_row = round(8 / len(list_item)) - 1
        if element is not None:
            element_value = list(element.__data__.values())
        for index in range(0, len(list_item)):
            if list_item[index] == 'Статус' and element is not None:
                check_var = StringVar(self.root, element.get_status())
                self.widgets[f"entry_{index}"] = CTkCheckBox(
                    self.root, variable=check_var, text='', onvalue="Да", offvalue="Нет")
                self.widgets[f"entry_{index}"].grid(
                    row=start_row + index, column=7, padx=10, ipadx=15)
            elif isinstance(list_item[index], tuple):
                combo_list_db = list(list_item[index][1])
                combo_list = [item.name for item in combo_list_db]
                self.widgets[f"entry_{index}"] = CTkComboBox(
                    self.root, values=combo_list
                )
                self.widgets[f"entry_{index}"].grid(
                    row=start_row + index, column=7, padx=10, ipadx=15)
                if element is not None:
                    variable_str = combo_list[element_value[index + 1] - 1]
                    self.widgets[f"entry_{index}"].set(variable_str)
            elif list_item[index] == 'Статус' and element is None:
                continue
            else:
                self.widgets[f"entry_{index}"] = CTkEntry(self.root)
                self.widgets[f"entry_{index}"].grid(
                    row=start_row + index, column=7, padx=10, ipadx=15)
                if element is not None:
                    self.widgets[f"entry_{index}"].insert(index, str(element_value[index + 1]))

            if isinstance(list_item[index], tuple):
                self.widgets[f"label_{index}"] = CTkLabel(
                    self.root, text=list_item[index][0],
                    text_color="white", font=self.font_lable)
                self.widgets[f"label_{index}"].grid(
                    row=start_row + index, column=3, padx=10, ipadx=15)
            else:
                self.widgets[f"label_{index}"] = CTkLabel(
                    self.root, text=list_item[index],
                    text_color="white", font=self.font_lable)
                self.widgets[f"label_{index}"].grid(
                    row=start_row + index, column=3, padx=10, ipadx=15)

        if element is not None:
            self.widgets["update_btn"] = (
                CustomButton(self.root, text="Изменить",
                             command=lambda: self.update_item_db(
                                 element=element
                             ))
            )
            self.widgets["update_btn"].grid(row=7, column=3)
        else:
            self.widgets["create_btn"] = (
                CustomButton(self.root, text="Добавить",
                             command=self.create_item_db)
            )
            self.widgets["create_btn"].grid(row=7, column=3)
        self.widgets["back_btn"].grid(row=7, column=7)

    def new_values(self):
        keys = self.view_model.get_fields()
        new_values = dict()
        for index in range(len(keys)):
            if keys[index] == 'is_active':
                if self.widgets[f"entry_{index}"].get() == 'Да':
                    new_values[keys[index]] = True
                else:
                    new_values[keys[index]] = False
            elif isinstance(keys[index], tuple):
                element = keys[index][1].get(name=self.widgets[f"entry_{index}"].get())
                new_values[keys[index][0]] = element
            else:
                new_values[keys[index]] = self.widgets[f"entry_{index}"].get()

        return new_values

    def list_view(self, model=None):
        if model is not None:
            self.view_model = model
        self.widgets["title"].configure(text=self.view_model.get_title())
        self.widgets["title"].grid(row=0, column=0, columnspan=8, sticky='nwne')
        self.widgets["back_btn"].grid(
            row=7, column=7, sticky='se')
        list_item = list(self.view_model)
        self.widgets["delete_btn"] = CustomButton(
            self.root, text='Удалить',
            command=lambda: self.delete_item_db(
                list_item[self.widgets["listbox"].curselection()],
                self.list_view
            ))
        self.widgets["update_btn"] = CustomButton(
            self.root, text='Изменить',
            command=lambda: self.next_command(
                command_next=self.create_or_update_frame,
                element=list_item[self.widgets["listbox"].curselection()]
            ))
        if len(list_item) > 0:
            for index in range(0, len(list_item)):
                self.widgets["listbox"].insert(
                    index, list_item[index])
        else:
            self.widgets["listbox"].insert(0, 'Здесь пока ничего нет.')
            self.widgets["delete_btn"].configure(state=DISABLED, cursor='pirate')
            self.widgets["update_btn"].configure(state=DISABLED, cursor='pirate')
        self.widgets["create_btn"] = CustomButton(
            self.root, text='Добавить',
            command=lambda: self.next_command(
                command_next=self.create_or_update_frame
            )
        )
        self.widgets["listbox"].grid(
            row=1, column=1, rowspan=6, columnspan=7, sticky='nsew'
        )
        self.widgets["create_btn"].grid(
            row=7, column=1, sticky='sw')
        self.widgets["update_btn"].grid(
            row=7, column=3, sticky='s')
        self.widgets["delete_btn"].grid(
            row=7, column=5, sticky='s')


class Helper(HelperCRUD):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.widgets = {
            "title": CTkLabel(self.root, bg_color="#1a4876",
                              text_color="white", font=self.font_title),
            "promocode_btn": CustomButton(self.root, text="Ввод промокодов",
                                          command=lambda: self.next_command(command_next=self.promocode_preview)),
            "marathon_btn": CustomButton(self.root, text="Парсинг марафона",
                                         command=lambda: self.next_command(command_next=self.marathon),
                                         state=DISABLED, cursor='pirate'),
            "characters_btn": CustomButton(self.root, text="Мои персонажи",
                                           command=lambda: self.next_command(
                                               command_next=self.list_view,
                                               model=CharacterModel
                                           )),
            "back_btn": CustomButton(self.root, text="Назад",
                                     command=lambda: self.next_command(default=self.main_window)),
            "settings_btn": CustomButton(self.root, text="Настройки",
                                         command=lambda: self.next_command(command_next=self.settings)),
            "block_item_btn": CustomButton(self.root, text='Блок-лист для перевода',
                                           command=lambda: self.next_command(
                                               command_next=self.list_view,
                                               model=BlockItemModel
                                           )),
            "chest_item_btn": CustomButton(self.root, text='Сундуки с фикс выбором',
                                           command=lambda: self.next_command(
                                               command_next=self.list_view,
                                               model=ChestItemModel
                                           )),
            "quit": CustomButton(self.root, text="Выход", command=self.quit),
            "listbox": CTkListbox(self.root),
            "info": CTkLabel(self.root, text_color="white", font=self.font_lable),
            "start_button": CustomButton(self.root, text='Начать'),
            "progressbar": CTkProgressBar(self.root, width=550, height=40, progress_color="#1a4876"),
            "progress_text": CTkTextbox(self.root, width=550, height=400),
            "end_button": CustomButton(
                self.root, text='Завершить',
                command=lambda: self.next_command(command_next=self.main_window)
            ),
        }
        self.main_window()

    def promocode_preview(self):
        self.widgets["title"].configure(text="Ввод промокодов")
        self.widgets["info"].configure(
            text='Введите, пожалуйста, промокод.\n'
                 'Если необходимо ввести несколько\n'
                 'промокодов, введите их через символ ";"\n'
                 'без использования дополнительных пробелов\n\n'
                 'Пример: promocode1;promocode2;promocode3')
        self.widgets["entry"] = CTkEntry(self.root, width=550, height=40)
        self.widgets["info"].grid(row=2, columnspan=8, sticky='nwne')
        self.widgets["entry"].grid(row=4, columnspan=6, sticky='ew')
        self.widgets["start_button"].configure(
            command=lambda: self.next_command(
                command_next=self.start_promo_view,
                promocodes_str=self.widgets["entry"].get()
            )
        )
        self.widgets["start_button"].grid(row=7, column=2, sticky='s')
        self.widgets["back_btn"].grid(
            row=7, column=5, sticky='s')
        self.widgets["title"].grid(row=0, column=0, padx=0, pady=0, columnspan=8, sticky='nwne')

    def marathon(self):
        self.widgets["title"].configure(text="Парсинг марафонов")
        self.widgets["title"].grid(row=0, column=0, padx=0, pady=0, columnspan=8, sticky='nwne')
        self.widgets["back_btn"].grid(
            row=7, column=7, ipadx=5,
            ipady=5, padx=2, pady=2, sticky='se')

    def settings(self):
        self.widgets["title"].configure(text="Настройки")
        self.widgets["title"].grid(
            row=0, column=0, padx=0, pady=0, columnspan=8, sticky='nwne')
        self.widgets["block_item_btn"].grid(row=3, column=2, columnspan=4, sticky='ew')
        self.widgets["chest_item_btn"].grid(row=4, column=2, columnspan=4, sticky='ew')
        self.widgets["back_btn"].grid(
            row=5, column=2, columnspan=4, sticky='ew')

    def start_promo_view(self, promocodes_str):
        self.widgets["title"].grid(row=0, column=0, padx=0, pady=0, columnspan=8, sticky='nwne')
        self.widgets["end_button"].grid(row=7, column=2, sticky='s')
        self.widgets["back_btn"].grid(row=7, column=5, sticky='s')
        self.widgets["progress_text"].grid(row=3, column=0, columnspan=8)
        self.widgets["progressbar"].grid(row=1, column=0, columnspan=8, pady=30, padx=30, sticky='nsew')
        self.root.update_idletasks()
        characters, chest_list, locked_list = initial()
        promocodes_list = promocodes_str.split(";")
        count = len(characters)
        step = 1 / count
        progress_step = 0
        self.widgets["progressbar"].set(0 - step)
        dont_active_list = list()
        for element in characters:
            is_active = activate_promocode(
                root=self.root,
                text_box=self.widgets["progress_text"],
                character=element,
                promocodes=promocodes_list,
                chest_list=chest_list,
                locked_list=locked_list
            )
            if not is_active:
                dont_active_list.append(f"{element.nickname}: {element.email}")
            progress_step += step
            self.widgets["progressbar"].set(progress_step)
            self.root.update_idletasks()

        if len(dont_active_list) > 0:
            log_str = f"Не удалось передать предметы следующим аккаунтам: {'; '.join(dont_active_list)}"
            self.widgets["progress_text"].insert("end", log_str)
            logger.info(log_str)
        else:
            log_str = "Промокод успешно активирован на все аккаунты"
            self.widgets["progress_text"].insert("end", log_str)
            logger.info(log_str)

        self.widgets["progressbar"].stop()


class App(CTk):
    def __init__(self):
        super().__init__()
        self.title('PW Helper')
        self.configure(fg='dark-blue')
        self.geometry("480x600")
        for row in range(8):
            self.grid_rowconfigure(row, weight=1)
            for column in range(8):
                self.grid_columnconfigure(column, weight=1)


set_appearance_mode("dark")
