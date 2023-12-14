from peewee import (SqliteDatabase, Model,
                    PrimaryKeyField, CharField,
                    ForeignKeyField, TextField,
                    ManyToManyField, BooleanField)


db = SqliteDatabase('helper.db')


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db
        order_by = 'id'


class TypeAuthModel(BaseModel):
    name = CharField()
    tech_name = CharField()

    class Meta:
        db_table = 'Type_Auth'

    def __str__(self):
        return f"{self.name}"


class ServerModel(BaseModel):
    name = CharField()

    class Meta:
        db_table = 'Servers'

    def __str__(self):
        return f"{self.name}"


class CharacterModel(BaseModel):
    nickname = CharField(unique=True)
    server = ForeignKeyField(ServerModel)
    email = CharField()
    password = CharField()
    type_auth = ForeignKeyField(TypeAuthModel)

    class Meta:
        db_table = 'Characters'

    def __str__(self):
        return f"{self.nickname}   |  {self.server}"

    @staticmethod
    def get_labels() -> tuple:
        labels = (
            "Ник персонажа",
            ("Сервер", ServerModel),
            "Email",
            "Пароль",
            ("Тип Авторизации", TypeAuthModel)
        )
        return labels

    @staticmethod
    def get_title():
        return "Мои персонажи"

    @classmethod
    def get_fields(cls):
        fields = ("nickname", ("server", ServerModel), "email", "password", ("type_auth", TypeAuthModel))
        return fields


class BlockItemModel(BaseModel):
    item_name = TextField()
    is_active = BooleanField(default=True)

    class Meta:
        db_table = 'Block_Item'

    def __str__(self):
        return f"Название итема: {self.item_name}   |  Активно: {self.get_status()}"

    def get_status(self):
        return "Да" if self.is_active else "Нет"

    @staticmethod
    def get_labels() -> tuple:
        labels = ("Имя объекта", "Статус")
        return labels

    @staticmethod
    def get_title():
        return "Блок-лист для перевода"

    @classmethod
    def get_fields(cls):
        fields = ("item_name", "is_active")
        return fields


class ChestItemModel(BaseModel):
    chest_name = TextField()
    item_chest_name = TextField()

    class Meta:
        db_table = 'Chest_Item'

    def __str__(self):
        return f"Сундук: {self.chest_name}   |   Итем: {self.item_chest_name}"

    @staticmethod
    def get_labels() -> tuple:
        labels = ("Название сундука", "Название итема \nиз сундука")
        return labels

    @staticmethod
    def get_title():
        return "Сундуки с фикс выбором"

    @classmethod
    def get_fields(cls):
        fields = ("chest_name", "item_chest_name")
        return fields


with db:
    tables = [
        ServerModel, CharacterModel,
        ChestItemModel, BlockItemModel, TypeAuthModel
        ]

    db.create_tables(tables)
    block_item_list = [
        {'item_name': 'золотой амулет'},
        {'item_name': 'Королевские особые пирожки'},
        {'item_name': 'Дар из прошлого'},
        {'item_name': 'золотого идола'},
        {'item_name': 'Запечатанная грамота Лиги'},
        {'item_name': 'Королевское особое печенье'},
    ]

    chest_dict = [
        {'chest_name': 'божеств','item_chest_name': 'Джу'},
    ]

    servers = [
        {'name': 'Саргас'},
        {'name': 'Скорпион'},
        {'name': 'Гиперион'},
        {'name': 'Фафнир'},
    ]

    type_auth = [
        {'name': 'Почта Mail.ru', 'tech_name': 'mail'},
        {'name': 'Логин и пароль', 'tech_name': 'straight'},
    ]

    for item in block_item_list:
        BlockItemModel.get_or_create(**item)

    for item in chest_dict:
        ChestItemModel.get_or_create(**item)

    for item in type_auth:
        TypeAuthModel.get_or_create(**item)

    for item in servers:
        ServerModel.get_or_create(**item)
