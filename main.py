import requests
from lxml import html
import pandas as pd
import time
import json
import random
import logging

# Пути к файлам и настройки
USER_AGENT_FILE = "useragent.txt"
CSV_FILE = "catalog.csv"
LOG_FILE = "parser.log"

# URL для получения последней страницы каталога
CATALOG_URL = "https://liniilubvi.ru/catalog/"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Записываем INFO, WARNING и ERROR
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),  # Лог в файл
        logging.StreamHandler()  # Вывод в консоль
    ]
)

def load_user_agents(filename=USER_AGENT_FILE):
    """Загружает список User-Agent из JSON-файла"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            ua_list = json.load(f)
            logging.info(f"✅ Загружено {len(ua_list)} User-Agent'ов")
            return [ua["ua"] for ua in ua_list]  # Достаем только строки с User-Agent
    except Exception as e:
        logging.error(f"❌ Ошибка загрузки user-agent'ов: {e}")
        return ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3"]  # Запасной UA

def get_random_user_agent(ua_list):
    """Выбирает случайный User-Agent из списка"""
    return random.choice(ua_list)

# Загружаем список User-Agent'ов один раз при старте
user_agents = load_user_agents()

def get_last_page():
    """Определяет количество страниц в каталоге"""
    headers = {"User-Agent": get_random_user_agent(user_agents)}

    logging.info(f"🌐 Запрашиваем {CATALOG_URL} для определения количества страниц")
    try:
        response = requests.get(CATALOG_URL, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"❌ Ошибка запроса {CATALOG_URL}: {e}")
        return 1

    tree = html.fromstring(response.content)
    page_numbers = tree.xpath('//*[@id="content"]/div[2]/div[4]/div/section/div[3]/div[2]/div/a/text()')
    page_numbers = [int(num) for num in page_numbers if num.isdigit()]

    last_page = max(page_numbers) if page_numbers else 1
    logging.info(f"📌 Определено количество страниц: {last_page}")
    return last_page

def parse_catalog_page(page_num):
    url = f"{CATALOG_URL}?PAGEN_1={page_num}"
    ua = get_random_user_agent(user_agents)
    print(f"📢 Используется User-Agent: {ua}")
    headers = {"User-Agent": ua}

    response = requests.get(url, headers=headers)
    content = response.content.decode('utf-8')


    if response.status_code != 200:
        print(f"❌ Ошибка {response.status_code} при запросе {url}")
        return []

    tree = html.fromstring(content)
    items = []

    for i in range(1, 21):
        try:
            # Гибкий XPath: ищем внутри блока с названием товара
            name_xpath = f'//*[@id="catalog-list"]/a[{i}]//div[contains(@class, "carusel-wrap-line-center-item-list-item-name")]//span/text()'
            name = tree.xpath(name_xpath)

            # XPath для цены
            price_xpath = f'//*[@id="catalog-list"]/a[{i}]//span[contains(@class, "carusel-wrap-line-center-item-list-item-price")]/text()'
            price = tree.xpath(price_xpath)

            if name and price:
                item = {"Название": name[0].strip(), "Цена": price[0].strip()}
                items.append(item)
                print(f"✅ Найден товар: {item}")
            else:
                print(f"⚠ Пропущен элемент {i}: не удалось извлечь данные")

        except Exception as e:
            print(f"❌ Ошибка при обработке элемента {i}: {e}")

    return items


def parse_all_pages():
    """Парсит все страницы каталога"""
    last_page = get_last_page()
    logging.info(f"📌 Начинаем парсинг {last_page} страниц")

    all_items = []
    for page in range(1, last_page + 1):
        logging.info(f"📥 Парсим страницу {page} из {last_page}...")
        items = parse_catalog_page(page)
        all_items.extend(items)
        time.sleep(random.uniform(1, 3))  # Случайная задержка для защиты от блокировки

    logging.info(f"✅ Парсинг завершен. Всего товаров собрано: {len(all_items)}")
    return all_items

def save_to_csv(data, filename=CSV_FILE):
    """ Сохраняем данные в CSV с правильной кодировкой """
    df = pd.DataFrame(data)
    df.to_csv(filename, sep = ';', encoding='cp1251')
    logging.info(f"📂 Данные сохранены в {filename}")

if __name__ == "__main__":
    logging.info("🚀 Запуск парсера")
    data = parse_all_pages()
    save_to_csv(data)
    logging.info("🏁 Работа завершена")
