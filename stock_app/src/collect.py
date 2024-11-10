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
