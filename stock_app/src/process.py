# 處理模組


import numpy as np
import pandas
import os


class processor:

    def pocess(self, DataFrame=None):
        if DataFrame is None or DataFrame.empty:
            return None

        process_DataFrame = DataFrame.copy()

        if 'Close' not in process_DataFrame.columns:
            print("缺少收盤價")
            return None

        if 'Volume' not in process_DataFrame.colums:
            print("缺少成交量")
            return None

        process_DataFrame['MA5'] = process_DataFrame['Close'].rolling(
            window=5
            ).mean()
        process_DataFrame['MA20'] = process_DataFrame['Close'].rolling(
            window=20
            ).mean()
        process_DataFrame['MA60'] = process_DataFrame['Close'].rolling(
            window=60
            ).mean()
        process_DataFrame['MA120'] = process_DataFrame['Close'].rolling(
            window=120
            ).mean()
        # 變化量
        process_DataFrame['Returns'] = process_DataFrame['Close'].pct_change()

        process_DataFrame['Volume_MA5'] = process_DataFrame['Volume'] \
            .rolling(window=5).mean()

        # 移除空的值
        process_DataFrame = process_DataFrame.dropna()

        print("使用DTYPES:\n"+process_DataFrame.dtypes)
        print("使用INFO:\n"+process_DataFrame.info())
        print("使用HEAD:\n"+process_DataFrame.head())

        return process_DataFrame
