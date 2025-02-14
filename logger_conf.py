from pathlib import Path
import logging
import logging.config
import yaml


BASE_DIR = Path(__file__).parent

def get_logger(name):
    """Функция возвращает экземляр объекта логирования считывающий конфигурацию из yaml файла."""
    log_dir = BASE_DIR / 'logs'
    if not log_dir.exists():
        log_dir.mkdir()
    config_file = BASE_DIR / 'logger_config.yml'
    with open(config_file, 'r') as yml:
        config = yaml.load(yml, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
    logger = logging.getLogger(name)
    return logger