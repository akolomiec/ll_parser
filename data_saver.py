import pandas as pd
from config import CSV_FILE
from logger import get_logger

def save_to_csv(data):
    logger = get_logger()
    try:
        pd.DataFrame(data).to_csv(CSV_FILE, sep=";", encoding="cp1251", index=False)
        logger.info(f"Данные сохранены в {CSV_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")