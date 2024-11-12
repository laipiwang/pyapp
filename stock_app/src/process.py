import numpy as np
import pandas as pd
import os


class processor:
    def process(self, DataF=None):
        # 1. 基本檢查
        if DataF is None:
            print("輸入數據為 None")
            return None

        if not isinstance(DataF, pd.DataFrame):
            print("輸入數據類型錯誤，應為 DataFrame")
            return None

        if DataF.empty:
            print("輸入數據為空")
            return None

        # 2. 深度複製數據
        process_DataFrame = DataF.copy(deep=True)

        # 3. 檢查必要欄位
        print("處理前數據列名:", process_DataFrame.columns)
        print("處理前數據型態:\n", process_DataFrame.dtypes)

        required_columns = ['Date', 'Close', 'Volume']
        if not all(col in
                   process_DataFrame.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in
                            process_DataFrame.columns]
            print(f"缺少必要欄位: {missing_cols}")
            return None

        # 4. 數據類型轉換前先處理可能的空值
        process_DataFrame = process_DataFrame.dropna(
            subset=['Date', 'Close', 'Volume'])

        # 5. 確保數據類型正確
        try:
            if process_DataFrame['Close'].dtype != 'float64':
                process_DataFrame['Close'] = \
                    process_DataFrame['Close'].astype(float)
            if process_DataFrame['Volume'].dtype != 'int64':
                process_DataFrame['Volume'] = \
                    process_DataFrame['Volume'].astype(int)
            if not pd.api.types.is_datetime64_any_dtype(
                    process_DataFrame['Date']):
                process_DataFrame['Date'] = pd.to_datetime(
                    process_DataFrame['Date'])
        except Exception as e:
            print(f"數據類型轉換失敗: {str(e)}")
            return None

        # 6. 檢查數據有效性
        if len(process_DataFrame) == 0:
            print("有效數據為空")
            return None

        if process_DataFrame['Close'].isna().all()\
                or process_DataFrame['Volume'].isna().all():
            print("Close 或 Volume 列包含全部空值")
            return None

        # 7. 確保日期排序
        process_DataFrame = process_DataFrame.sort_values('Date')

        # 8. 計算技術指標
        rolling_windows = {
            'MA5': 5,
            'MA20': 20,
            'MA60': 60,
            'MA120': 120
        }

        rolling_count = len(process_DataFrame)
        for ma_name, window in rolling_windows.items():
            if rolling_count >= window:
                process_DataFrame[ma_name] = \
                    process_DataFrame['Close'].rolling(window=window).mean()

        # 計算變化量和成交量移動平均
        process_DataFrame['Returns'] = process_DataFrame['Close'].pct_change()
        process_DataFrame['Volume_MA5'] = process_DataFrame['Volume'].rolling(
            window=5).mean()

        # 最終的空值處理
        process_DataFrame = process_DataFrame.dropna()

        if len(process_DataFrame) == 0:
            print("處理後數據為空")
            return None

        # 輸出處理結果資訊
        print("處理後數據資訊:")
        print("DTYPES:\n", process_DataFrame.dtypes)
        print("\nINFO:")
        process_DataFrame.info()
        print("\nHEAD:")
        print(process_DataFrame.head())

        return process_DataFrame
