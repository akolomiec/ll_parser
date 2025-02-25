import requests
from lxml import html
import pandas as pd
import json
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore

# Пути к файлам
USER_AGENT_FILE = "useragent.txt"
PROXY_FILE = "proxies.txt"
CSV_FILE = "catalog.csv"
LOG_FILE = "parser.log"

# URL каталога
CATALOG_URL = "https://liniilubvi.ru/catalog/"


# Количество потоков
TOTAL_THREADS = 2

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def load_user_agents():
    """Загружает список User-Agent из JSON."""
    try:
        with open(USER_AGENT_FILE, "r", encoding="utf-8") as f:
            agents = json.load(f)
            return [ua["ua"] for ua in agents]  # Берем только строки User-Agent
    except Exception as e:
        logging.error(f"❌ Ошибка загрузки User-Agent: {e}")
        return ["Mozilla/5.0"]  # Запасной вариант, если файл сломан

def get_random_user_agent():
    """Выбирает случайный User-Agent из списка."""
    return random.choice(user_agents)


def load_proxies():
    """Загружает список прокси"""
    try:
        with open(PROXY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logging.error(f"❌ Ошибка загрузки прокси: {e}")
        return []

def get_random_user_agent():
    """Выбирает случайный User-Agent"""
    return random.choice(user_agents)

def get_random_proxy():
    """Выбирает случайный прокси (если есть)"""
    return random.choice(proxies) if proxies else None

# Загружаем данные
user_agents = load_user_agents()
proxies = load_proxies()


def get_last_page():
    """Определяет количество страниц"""
    headers = {"User-Agent": get_random_user_agent()}
    proxy = get_random_proxy()
    proxy_dict = {"http": proxy, "https": proxy} if proxy else {}

    logging.info(f"🌐 Определяем количество страниц на {CATALOG_URL}")

    try:
        response = requests.get(CATALOG_URL, headers=headers, proxies=proxy_dict, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"❌ Ошибка запроса: {e}")
        return 1

    tree = html.fromstring(response.content)

    # Находим все элементы пагинации и извлекаем номер страницы
    page_numbers = tree.xpath('//a[contains(@href, "?PAGEN_1=")]/text()')

    # Фильтруем и извлекаем только числа
    page_numbers = [int(num) for num in page_numbers if num.isdigit()]

    last_page = max(page_numbers) if page_numbers else 1
    logging.info(f"📌 Найдено страниц: {last_page}")
    return last_page


def parse_catalog_page(page_num, proxy):
    """Парсит одну страницу каталога"""
    url = f"{CATALOG_URL}?PAGEN_1={page_num}"
    headers = {"User-Agent": get_random_user_agent()}
    proxy_dict = {"http": proxy, "https": proxy} if proxy else {}

    logging.info(f"🌍 Парсим страницу {page_num} через {proxy}")

    try:
        response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"❌ Ошибка при запросе {url}: {e}")
        return []
    content = response.content.decode('utf-8')
    tree = html.fromstring(content)
    items = []

    # Новый XPath для товаров
    products = tree.xpath('//a[contains(@class, "catalog-item") and contains(@class, "js-catalog-item")]')

    for product in products:
        try:
            name = product.xpath('.//div[contains(@class, "carusel-wrap-line-center-item-list-item-name")]/span/text()')
            price = product.xpath('.//span[contains(@class, "carusel-wrap-line-center-item-list-item-price")]/text()')
            old_price = product.xpath('.//span[contains(@class, "carusel-wrap-line-center-item-list-item-price-old")]/i/text()')
            img_url = product.xpath('.//img[contains(@class, "first_img_s")]/@src')
            product_url = product.xpath('.//@href')

            if name and price:
                item = {
                    "Название": name[0].strip(),
                    "Цена": price[0].strip(),
                    "Старая цена": old_price[0].strip() if old_price else "Нет старой цены",
                    "Изображение": img_url[0] if img_url else "Нет изображения",
                    "Ссылка": product_url[0] if product_url else "Нет ссылки"
                }
                items.append(item)
                logging.info(f"✅ Найден товар: {item}")

        except Exception as e:
            logging.error(f"❌ Ошибка парсинга товара: {e}")

    return items


def parse_all_pages():
    """Парсит все страницы в многопотоке"""
    last_page = get_last_page()
    logging.info(f"📌 Начинаем парсинг {last_page} страниц с {TOTAL_THREADS} потоками")

    all_items = []
    with ThreadPoolExecutor(max_workers=TOTAL_THREADS) as executor:
        future_to_page = {executor.submit(parse_catalog_page, page, get_random_proxy()): page for page in range(1, last_page + 1)}

        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                items = future.result()
                all_items.extend(items)
                logging.info(f"📄 Страница {page} обработана, товаров: {len(items)}")
            except Exception as e:
                logging.error(f"❌ Ошибка на странице {page}: {e}")

    logging.info(f"✅ Парсинг завершен. Всего товаров собрано: {len(all_items)}")
    return all_items

def save_to_csv(data):
    """Сохраняет в CSV"""
    df = pd.DataFrame(data)
    df.to_csv(CSV_FILE, sep=";", encoding="cp1251", index=False)
    logging.info(f"📂 Данные сохранены в {CSV_FILE}")

if __name__ == "__main__":
    logging.info("🚀 Запуск парсера")
    data = parse_all_pages()
    save_to_csv(data)
    logging.info("🏁 Работа завершена")
