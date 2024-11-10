# 數據收集模組

import yfinace as yf
import pandas as pd
import os
from datetime import datetime


class collect:

    def __init__(self, data_file="data/stock_data"):
        # 初始化數具資料夾
        self.data_file = data_file
        # 檢查路徑
        if not os.path.exists(self.data_file):
            os.makedirs(self.data_file)

    def collection(self, stock_num, start_date="2021-01-01", end_date=None):
        # 讀取時間
        end_date = datetime.now.strftime("%Y-%M-%D")

    try:
        stock = yf.Ticker(stock_num)
        DataFrame = stock.history(start=start_date, end=end_date)
        if DataFrame.empty:
            print("不是哥們，找不到數據(資料框為空)")
            return None
        file_path = os.path.join(self.data_file)