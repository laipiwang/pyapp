import logging
import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
from src.utils.config_loader import ConfigLoader


class Collector:
    def __init__(self):
        """初始化收集器"""
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.get_config()
        self.logger = logging.getLogger('stock_analysis.collector')

        # 設置數據存儲路徑
        self.data_dir = Path(self.config['base']['data_dir'])
        self.data_dir.mkdir(exist_ok=True)

    def collect(self, stock_num: str,
                start_date: Optional[str] = None,
                end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """收集股票數據"""
        try:
            # 使用配置文件中的默認日期
            if start_date is None:
                start_date = self.config['data_collection']
                ['default_start_date']
            if end_date is None:
                end_date = self.config['data_collection']['default_end_date']

            # 驗證參數
            if not self._validate_stock_num(stock_num):
                return None
            if not self._validate_dates(start_date, end_date):
                return None

            # 獲取重試配置
            retry_config = self.config['data_collection']['retry']
            max_attempts = retry_config['max_attempts']
            delay_seconds = retry_config['delay_seconds']

            # 嘗試獲取數據
            for attempt in range(max_attempts):
                try:
                    # 檢查緩存
                    cached_data = self._check_cache(stock_num)
                    if cached_data is not None:
                        self.logger.info(f"使用緩存的數據: {stock_num}")
                        return cached_data

                    # 從 Yahoo Finance 獲取數據
                    stock = yf.Ticker(f"{stock_num}.TW")
                    df = stock.history(start=start_date, end=end_date)

                    if df is None or df.empty:
                        self.logger.warning(f"股票代碼 {stock_num} 的數據為空")
                        return None

                    # 清理數據
                    df = self._clean_dataframe(df)

                    # 保存到緩存
                    self._save_to_file(stock_num, df)

                    self.logger.info(f"成功下載數據: {stock_num}")
                    return df

                except Exception as e:
                    if attempt < max_attempts - 1:
                        self.logger.warning(
                            f"嘗試 {attempt + 1}/{max_attempts} 失敗: {str(e)}"
                        )
                        import time
                        time.sleep(delay_seconds)
                    else:
                        self.logger.error(f"所有嘗試都失敗: {str(e)}")
                        return None

        except Exception as e:
            self.logger.error(f"收集數據時發生錯誤: {str(e)}")
            return None

    def get_info(self, stock_num: str) -> Optional[Dict]:
        """獲取股票基本信息"""
        try:
            stock = yf.Ticker(f"{stock_num}.TW")
            info = stock.info

            result = {
                'symbol': stock_num,
                'name': info.get('longName', ''),
                'industry': info.get('industry', ''),
                'sector': info.get('sector', ''),
                'website': info.get('website', ''),
                'market_cap': info.get('marketCap', None),
                'currency': info.get('currency', 'TWD')
            }

            self.logger.info(f"成功獲取股票信息: {stock_num}")
            return result

        except Exception as e:
            self.logger.error(f"獲取股票信息失敗 {stock_num}: {str(e)}")
            return None

    def _validate_stock_num(self, stock_num: str) -> bool:
        """驗證股票代碼"""
        try:
            if not isinstance(stock_num, str):
                raise ValueError("股票代碼必須是字符串")
            if not stock_num.strip():
                raise ValueError("股票代碼不能為空")
            if not stock_num.isdigit():
                raise ValueError("股票代碼必須是數字字符串")
            return True
        except Exception as e:
            self.logger.error(f"股票代碼驗證失敗: {str(e)}")
            return False

    def _validate_dates(self, start_date: str, end_date: str) -> bool:
        """驗證日期格式"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start > end:
                raise ValueError("起始日期不能晚於結束日期")
            return True
        except ValueError as e:
            self.logger.error(f"日期格式錯誤: {str(e)}")
            return False

    def _clean_dataframe(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """清理數據框"""
        try:
            if df is None or df.empty:
                return None

            # 標準化列名
            df.columns = [col.lower() for col in df.columns]

            # 處理重複和缺失值
            df = df.drop_duplicates()
            df = df.dropna()

            # 確保索引是日期類型
            df.index = pd.to_datetime(df.index)

            return df

        except Exception as e:
            self.logger.error(f"清理數據失敗: {str(e)}")
            return None

    def _check_cache(self, stock_num: str) -> Optional[pd.DataFrame]:
        """檢查是否有緩存數據"""
        try:
            file_path = self.data_dir / f"{stock_num}.csv"

            if file_path.exists():
                df = pd.read_csv(file_path)
                if not df.empty:
                    # 使用 tz_localize(None) 來移除時區資訊
                    today = pd.Timestamp.now().normalize().tz_localize(None)
                    latest_date = pd.to_datetime(df['date']).max()
                    if latest_date >= today - pd.Timedelta(days=1):
                        self.logger.info(f"使用緩存數據: {file_path}")
                        return df
            return None

        except Exception as e:
            self.logger.warning(f"讀取緩存失敗: {str(e)}")
        return None

    def _save_to_file(self, stock_num: str, df: pd.DataFrame) -> None:
        """保存數據到文件"""
        try:
            file_path = self.data_dir / f"{stock_num}.csv"
            df.to_csv(file_path, index=True)
            self.logger.info(f"數據已保存到: {file_path}")

        except Exception as e:
            self.logger.error(f"保存數據失敗: {str(e)}")
