import unittest
import pandas as pd
import numpy as np
from stock_app.src.process import Processor


class Test_Processor(unittest.TestCase):
    def setUp(self):
        self.processor = Processor()
        # 創建測試數據
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.test_data = pd.DataFrame({
            'date': dates,
            'open': np.random.randn(len(dates)),
            'high': np.random.randn(len(dates)),
            'low': np.random.randn(len(dates)),
            'close': np.random.randn(len(dates)),
            'volume': np.random.randint(1000, 10000, len(dates))
        })

    def test_empty_data(self):
        """測試空數據"""
        result = self.processor.process(None)
        self.assertIsNone(result, "測試空數據:應該回傳None")

        result = self.processor.process(pd.DataFrame())
        self.assertIsNone(result, "測試空DataFrame:應該回傳None")

    def test_missing_columns(self):
        """測試缺失欄位"""
        # 創建缺少必要欄位的數據
        incomplete_data = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01',
                                  end='2023-12-31',
                                  freq='D'),
            'close': np.random.randn(365)
        })
        result = self.processor.process(incomplete_data)
        self.assertIsNone(result, "測試缺失欄位:應該回傳None")

    def test_valid_data_processing(self):
        """測試正常數據處理"""
        result = self.processor.process(self.test_data)
        self.assertIsNotNone(result, "測試正常數據:應該回傳資料框")

        # 檢查是否包含所有技術指標
        expected_columns = ['ma_5', 'ma_20', 'macd', 'signal', 'rsi',
                            'atr', 'bb_middle', 'bb_upper', 'bb_lower',
                            'trend']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"缺少技術指標列: {col}")

    def test_dropna_removal(self):
        """測試NaN值處理"""
        # 在測試數據中插入一些NaN值
        test_data_with_nan = self.test_data.copy()
        test_data_with_nan.loc[10:15, 'close'] = np.nan

        result = self.processor.process(test_data_with_nan)
        self.assertNotIn(None, result['close'].values,
                         "處理後的數據不應該包含NaN值")

    def test_date_index(self):
        """測試日期索引處理"""
        # 測試date欄位轉換為索引
        result = self.processor.process(self.test_data)
        self.assertTrue(isinstance(result.index, pd.DatetimeIndex),
                        "索引應該是DatetimeIndex類型")


if __name__ == '__main__':
    unittest.main()
