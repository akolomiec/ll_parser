import random
import json
from config import PROXY_FILE

class ProxyManager:
    def __init__(self):
        self.proxies = self.load_proxies()

    @staticmethod
    def load_proxies():
        try:
            with open(PROXY_FILE, "r", encoding="utf-8") as file:
                return [line.strip() for line in file if line.strip()]
        except Exception as e:
            raise Exception(f"Ошибка загрузки прокси: {e}")

    def get_random_proxy(self):
        return random.choice(self.proxies) if self.proxies else None