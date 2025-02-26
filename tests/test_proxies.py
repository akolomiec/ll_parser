import unittest
from proxy_manager import ProxyManager

class TestProxyManager(unittest.TestCase):

    def setUp(self):
        self.proxy_manager = ProxyManager()

    def test_load_proxies(self):
        self.assertIsInstance(self.proxy_manager.proxies, list)

    def test_get_random_proxy(self):
        proxy = self.proxy_manager.get_random_proxy()
        if self.proxy_manager.proxies:
            self.assertIn(proxy, self.proxy_manager.proxies)
        else:
            self.assertIsNone(proxy)

if __name__ == '__main__':
    unittest.main()