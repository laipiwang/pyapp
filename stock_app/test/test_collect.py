# 數據收集模組測試
import unittest
import os
import shutil
from stock_app.src.collect import Collector


class TestCollect(unittest.TestCase):
    tear_count = 1  # 靜態變量，用於計算清理次數

    def setUp(self):
        """初始化測試數據"""
        self.collector = Collector()
        self.stock_num = "2357"  # 股票代碼，不需要 .TW 後綴，類中會自動處理
        self.test_data_dir = "data"

    def test_collection(self):
        """測試數據收集功能"""
        # 收集數據
        df = self.collector.collect(
            self.stock_num,
            start_date="2023-08-01",
            end_date="2024-10-10"
        )
        print(df)
        # 確認數據不為 None
        self.assertIsNotNone(df)
        # 確認數據不為空
        self.assertGreater(len(df), 0)
        # 確認文件已保存
        # file_path = os.path.join(self.test_data_dir, f"{self.stock_num}.csv")
        file_path = os.path.join("stock_app", "data", f"{self.stock_num}.csv")
        self.assertTrue(os.path.exists(file_path))
        # 確認是否包含成交量
        if 'Volume' in df.columns:
            print("成功收集到成交量數據")
        else:
            print("未找到成交量數據")

    def test_info_get(self):
        """測試股票信息獲取功能"""
        info = self.collector.get_info(self.stock_num)
        # 確認返回值是字典
        self.assertIsInstance(info, dict)
        # 確認包含必須的鍵
        self.assertIn('name', info)
        self.assertIn('industry', info)
        print("成功獲取股票信息")

    def tearDown(self):
        """清理測試過程中生成的文件和資料夾"""
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)  # 遞歸刪除資料夾
        print(f"清空資料夾第 {TestCollect.tear_count} 次")
        TestCollect.tear_count += 1


if __name__ == "__main__":
    unittest.main()
