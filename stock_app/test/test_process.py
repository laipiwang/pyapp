import pandas as pd
import unittest
import numpy as np
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

    def test_empty_data(self):
        # 測試空數據和 None
        self.assertIsNone(self.processor.process(None),
                          "測試回傳:None input沒有回傳None")
        self.assertIsNone(
                self.processor.process(pd.DataFrame()),
                "測試回傳:空資料沒有回傳None"
                          )

    def test_missing_columns(self):
        # 測試缺少必要欄位
        df_missing_close = pd.DataFrame({'Volume': [100]})
        self.assertIsNone(self.processor.process(df_missing_close),
                          "測試回傳:找不到Volume所以回傳None")

        data_close = self.Data.drop(columns=['Close'])
        result = self.processor.process(data_close)
        self.assertIsNone(result,
                          "測試回傳:找不到收盤價所以回傳None")

    def test_valid_data_processing(self):
        # 測試正常數據
        result = self.processor.process(self.Data)
        self.assertIsNotNone(result,
                             "測試正常數據:應該回傳資料框")
        self.assertGreater(len(result), 0,
                           "測試正常數據:處理過的資料空不應該為空")

        # list_col = ['MA' + f'{i}' for i in self.processor.list_of_ma]
        list_col = ['MA5', 'MA20', 'MA60', 'MA120', 'Returns', 'Volume_MA5']
        for col in list_col:
            self.assertIn(col, result.columns,
                          f"沒有找到{col}在處理過的數據裡")

    def test_dropna_removal(self):
        # 測試 dropna 是否能正確移除空值
        self.Data.loc[2, 'Close'] = None  # 將某個數值設為 NaN
        result = self.processor.process(self.Data)
        self.assertNotIn(None, result['Close'].values,
                         "測試回傳:收盤價裡面的空值應該要被移除")

    def test_invalid_data_handling(self):
        # 測試無效數據
        df_invalid = pd.DataFrame({
            'Date': ['2023-01-01'] * 5,
            'Close': [None] * 5,
            'Volume': [1] * 5
        })
        self.assertIsNone(self.processor.process(df_invalid),
                          "測試回傳:收盤價裡面的無效值應該被移除"
                          )


if __name__ == "__main__":
    unittest.main()
