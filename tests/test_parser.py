import unittest
from parser import Parser
from proxy_manager import ProxyManager
from user_agent_manager import UserAgentManager
from lxml import html

class TestParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.proxy_manager = ProxyManager()
        cls.user_agent_manager = UserAgentManager()
        cls.parser = Parser(cls.proxy_manager, cls.user_agent_manager)

    def test_extract_product_info(self):
        sample_html = '''
        <a class="catalog-item js-catalog-item" href="/catalog/item123">
            <div class="carusel-wrap-line-center-item-list-item-name"><span>Тестовый товар</span></div>
            <span class="carusel-wrap-line-center-item-list-item-price">1000 ₽</span>
            <span class="carusel-wrap-line-center-item-list-item-price-old"><i>1200 ₽</i></span>
            <img class="first_img_s" src="/img/test.jpg"/>
        </a>
        '''
        tree = html.fromstring(sample_html)
        product = tree.xpath('//a')[0]
        result = self.parser.extract_product_info(product)

        self.assertEqual(result['Название'], "Тестовый товар")
        self.assertEqual(result['Цена'], "1000 ₽")
        self.assertEqual(result['Старая цена'], "1200 ₽")
        self.assertEqual(result['Изображение'], "/img/test.jpg")
        self.assertEqual(result['Ссылка'], "/catalog/item123")

    def test_get_last_page(self):
        last_page = self.parser.get_last_page()
        self.assertIsInstance(last_page, int)
        self.assertGreaterEqual(last_page, 1)

    def test_parse_catalog_page(self):
        products = self.parser.parse_catalog_page(1)
        self.assertIsInstance(products, list)
        if products:
            self.assertIn("Название", products[0])
            self.assertIn("Цена", products[0])

if __name__ == '__main__':
    unittest.main()