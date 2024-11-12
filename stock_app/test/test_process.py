# 測試數據處理
import pandas as pd
import unittest
from stock_app.src.process import processor


class test_processor(unittest.TestCase):

    def setUp(self):
        data = {
            'Date': pd.date_range(start='2023-01-01', periods=120, freq='D'),
            'Close': [100 + i for i in range(120)],
            'Volume': [1000 + (i * 10 % 500) for i in range(120)]
        }
        self.Data = pd.DataFrame(data)
        self.processor = processor()

    def test_process(self):
        result = self.processor.process(self.Data)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

        list_col = ['MA5', 'MA20', 'MA60', 'MA120', 'Returns', 'Volume_MA5']
        for col in list_col:
            self.assertIn(col, result.columns)

    # 測試Close
    def test_close(self):
        print("測試數據的列名:", self.Data.columns)
        data_close = self.Data.drop(columns=['Close'])
        result = self.processor.process(data_close)
        self.assertIsNone(result)

    def test_empty(self):
        empty_df = pd.DataFrame(columns=['Date', 'Close', 'Volume'])
        result = self.processor.process(empty_df)
        self.assertIsNone(result)

    def test_dropna(self):
        # 測試 dropna 是否能正確移除空值
        self.Data.loc[2, 'Close'] = None  # 將某個數值設為 NaN
        result = self.processor.process(self.Data)
        self.assertNotIn(None, result['Close'].values)


if __name__ == "__main__":
    unittest.main()
