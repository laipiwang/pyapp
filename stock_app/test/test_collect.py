# 數據收集模組測試
import unittest
import os
from collect import collector


class test_collect(unittest.TestCase):
    def setUp(self):
        self.collector = collector(data_file="test_data")
        self.stock_num = "0050.TW"

    def test_collection(self):
        DataFrame = self.collector.collection(
            self.stock_num,
            start_date="2023-08-01",
            end_date="2024-10-10"
            )
        # 檢查不為None
        self.assertIsNotNone(DataFrame)
        # 檢查大於0
        self.asserGreater(len(DataFrame), 0)
        file_path = os.path.join("test_data", f"{self.symbol}.csv")
        self.assertTrue(os.path.exists(file_path))

    def tearDown(self):
        # 清理資料夾
        if os.path.exists("test_data"):
            for file in os.listdir("test_data"):
                os.remove(os.path.join("test_data", file))
            os.rmdir("test_data")
