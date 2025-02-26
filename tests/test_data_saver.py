import unittest
import os
import pandas as pd
from data_saver import save_to_csv
from config import CSV_FILE

class TestDataSaver(unittest.TestCase):

    def test_save_to_csv(self):
        test_data = [
            {"Название": "Товар 1", "Цена": "1000 ₽", "Старая цена": "1200 ₽", "Изображение": "url1", "Ссылка": "url1"},
            {"Название": "Товар 2", "Цена": "2000 ₽", "Старая цена": "2500 ₽", "Изображение": "url2", "Ссылка": "url2"}
        ]

        save_to_csv(test_data)
        self.assertTrue(os.path.exists(CSV_FILE), "CSV файл не был создан!")

        df = pd.read_csv(CSV_FILE, sep=';', encoding='utf-8-sig')
        self.assertEqual(len(df), 2, "CSV должен содержать 2 записи")
        self.assertIn("Название", df.columns)
        self.assertEqual(df.iloc[0]['Название'], "Товар 1")

if __name__ == '__main__':
    unittest.main()