import requests
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from logger import get_logger
from config import CATALOG_URL, TOTAL_THREADS
import time


class Parser:
    def __init__(self, proxy_manager, user_agent_manager):
        self.proxy_manager = proxy_manager
        self.user_agent_manager = user_agent_manager
        self.logger = get_logger()
        self.session = self._create_session()


    def _create_session(self):
        """
        Создает и настраивает сессию requests с общими заголовками и прокси.
        Это позволяет использовать одни и те же настройки во всех запросах.
        """
        session = requests.Session()
        user_agent = self.user_agent_manager.get_random_user_agent()
        proxy = self.proxy_manager.get_random_proxy()

        session.headers.update({"User-Agent": user_agent})
        if proxy:
            session.proxies.update({"http": proxy, "https": proxy})

        self.logger.info(f"🔧 Создана сессия с User-Agent: {user_agent} и прокси: {proxy}")
        return session


    def _get_response(self, url, timeout=15):
        """Выполняет GET-запрос с логированием и обработкой ошибок."""
        self.logger.info(f"🌐 Отправка запроса: {url}")
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            elapsed_time = time.time() - start_time
            self.logger.info(f"✅ Успешный ответ (Статус: {response.status_code}, Время: {elapsed_time:.2f}s)")
            return response
        except requests.Timeout:
            self.logger.error(f"⏳ Таймаут при запросе: {url}")
        except requests.RequestException as e:
            self.logger.error(f"❌ Ошибка при запросе {url}: {e}")
        return None

    def get_last_page(self):
        """Определяет количество страниц каталога."""
        self.logger.info(f"🔍 Запрос количества страниц: {CATALOG_URL}")
        response = self._get_response(CATALOG_URL, timeout=10)

        if not response:
            self.logger.warning("⚠️ Используем значение по умолчанию: 1 страница")
            return 1

        tree = html.fromstring(response.content)
        page_numbers = [int(num) for num in tree.xpath('//a[contains(@href, "?PAGEN_1=")]/text()') if num.isdigit()]
        last_page = max(page_numbers) if page_numbers else 1
        self.logger.info(f"📄 Найдено страниц: {last_page}")
        return last_page

    def parse_catalog_page(self, page_num):
        """Парсит товары с указанной страницы каталога."""
        url = f"{CATALOG_URL}?PAGEN_1={page_num}"
        response = self._get_response(url)

        if not response:
            self.logger.warning(f"⚠️ Пропуск страницы {page_num} из-за ошибки запроса")
            return []

        content = response.content.decode("utf-8")
        tree = html.fromstring(content)
        products = tree.xpath('//a[contains(@class, "catalog-item") and contains(@class, "js-catalog-item")]')
        self.logger.info(f"🔎 Страница {page_num}: Найдено товаров: {len(products)}")

        items = [self.extract_product_info(product, page_num) for product in products]
        self.logger.info(f"✅ Страница {page_num} обработана. Собрано товаров: {len(items)}")
        return items

    def extract_product_info(self, product, page_num):
        """Извлекает информацию о товаре из HTML-элемента."""
        try:
            name = product.xpath('.//div[contains(@class, "carusel-wrap-line-center-item-list-item-name")]/span/text()')
            price = product.xpath('.//span[contains(@class, "carusel-wrap-line-center-item-list-item-price")]/text()')
            old_price = product.xpath(
                './/span[contains(@class, "carusel-wrap-line-center-item-list-item-price-old")]/i/text()')
            img_url = product.xpath('.//img[contains(@class, "first_img_s")]/@src')
            product_url = product.xpath('./@href')

            product_info = {
                "Название": name[0].strip() if name else "-",
                "Цена": price[0].strip() if price else "-",
                "Старая цена": old_price[0].strip() if old_price else "Нет старой цены",
                "Изображение": img_url[0] if img_url else "Нет изображения",
                "Ссылка": product_url[0] if product_url else "Нет ссылки"
            }

            self.logger.debug(f"📦 (Страница {page_num}) Обработан товар: {product_info}")
            return product_info
        except Exception as e:
            self.logger.error(f"❌ Ошибка при парсинге товара на странице {page_num}: {e}")
            return {
                "Название": "Ошибка парсинга",
                "Цена": "-",
                "Старая цена": "-",
                "Изображение": "-",
                "Ссылка": "-"
            }

    def parse_all_pages(self):
        """Парсит все страницы каталога с многопоточностью."""
        self.logger.info("🚀 Запуск парсинга всех страниц...")
        last_page = self.get_last_page()
        self.logger.info(f"📄 Всего страниц для обработки: {last_page}")
        all_items = []

        with ThreadPoolExecutor(max_workers=TOTAL_THREADS) as executor:
            futures = {executor.submit(self.parse_catalog_page, page): page for page in range(1, last_page + 1)}

            for future in as_completed(futures):
                page = futures[future]
                try:
                    start_time = time.time()
                    items = future.result()
                    elapsed_time = time.time() - start_time
                    all_items.extend(items)
                    self.logger.info(
                        f"✅ Страница {page} завершена. Время: {elapsed_time:.2f}s. Собрано товаров: {len(items)}")
                except Exception as e:
                    self.logger.error(f"❌ Ошибка при обработке страницы {page}: {e}")

        self.logger.info(f"🏁 Парсинг завершен. Всего собрано товаров: {len(all_items)}")
        return all_items