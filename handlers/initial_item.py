from database.models import CharacterModel, ChestItemModel, BlockItemModel


def initial():
    characters = list(CharacterModel)
    chest_list = list(ChestItemModel)
    locked_list = list(BlockItemModel)
    return characters, chest_list, locked_list
