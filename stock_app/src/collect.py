# 數據收集模組
import logging
import yfinance as yf
import pandas
import os
from datetime import datetime


class collector:

    def __init__(self, data_file="data/stock_data"):
        logging.basicConfig(
            filename='stock_collector.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def collection(self, stock_num, start_date="2021-01-01", end_date=None):
        # 讀取時間

        if not stock_num:
            raise ValueError("股票代碼不能為空")

        try:
            stock = yf.Ticker(stock_num)
            DataFrame = stock.history(start=start_date, end=end_date)
            if DataFrame.empty:
                print("不是哥們，找不到數據(資料框為空)")
                return None
            file_path = os.path.join(self.data_file, f"{stock_num}.csv")
            print(f"路徑是{file_path}")
            DataFrame.to_csv(file_path)
            return DataFrame

        except yf.exceptions.YFinanceError as e:
            print(f"Yahoo Finance API 錯誤: {e}")
            return None
        except pandas.errors.EmptyDataError:
            print("下載的數據為空")
            return None
        except Exception as e:
            print(f"未預期的錯誤: {e}")
            return None

    def _validate_dates(self, start_date, end_date):
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start > end:
                raise ValueError("起始日期不能晚於結束日期")
            return True
        except ValueError as e:
            print(f"日期格式錯誤: {e}")
            return False

    def info_get(self, stock_num):
        # 獲取名稱、產業別
        try:
            stock = yf.Ticker(stock_num)
            info = stock.info
            return {
                'name': info.get('longName', ''),
                'industry': info.get('industry', '')
            }

        except Exception as e:
            print(f"讀取錯誤: {e}")
            return None
