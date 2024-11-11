# 數據收集模組測試
import unittest
import os
from stock_app.src.collect import collector


class test_collect(unittest.TestCase):
    tear = 1

    def setUp(self):
        self.collector = collector(data_file="test_data")
        self.stock_num = "2357.TW"

    def test_collection(self):
        DataFrame = self.collector.collection(
            self.stock_num,
            start_date="2023-08-01",
            end_date="2024-10-10"
            )
        # 檢查不為None
        self.assertIsNotNone(DataFrame)
        # 檢查大於0
        self.assertGreater(len(DataFrame), 0)
        file_path = os.path.join("test_data", f"{self.stock_num}.csv")
        self.assertTrue(os.path.exists(file_path))
        if 'Volume' in DataFrame.columns:
            print("成功收集到成交量數據")
        else:
            print("未找到成交量數據")

    def test_info_get(self):
        info = self.collector.info_get(self.stock_num)
        self.assertIsInstance(info, dict)
        self.assertIn('name', info)
        self.assertIn('industry', info)

    def tearDown(self):
        # 清理資料夾
        if os.path.exists("test_data"):
            for file in os.listdir("test_data"):
                os.remove(os.path.join("test_data", file))
            os.rmdir("test_data")
            # 提醒一下自己這邊用self.tear也是可以的
            print(f"清空資料夾第{test_collect.tear}次")
            test_collect.tear += 1


if __name__ == "__main__":
    unittest.main()
