import pandas as pd
import numpy as np
from typing import Optional
import logging
from src.utils.config_loader import ConfigLoader


class Processor:
    def __init__(self):
        """初始化處理器"""
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.get_config()
        self.logger = logging.getLogger('stock_analysis.processor')

    def process(self, df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
        """處理股票數據，計算技術指標"""
        try:
            # 基本驗證
            if df is None or df.empty:
                self.logger.error("數據處理失敗: 輸入數據為空")
                return None

            # 檢查必要的列
            required_cols = self.config['data_processing']['required_columns']
            missing_columns = [col for col in required_cols
                               if col not in df.columns]
            if missing_columns:
                self.logger.error(f"數據處理失敗: 缺少必要的列: {missing_columns}")
                return None

            # 複製數據避免修改原始數據
            result = df.copy()

            # 確保索引是日期類型
            if not isinstance(result.index, pd.DatetimeIndex):
                result.index = pd.to_datetime(result.index)

            try:
                # 計算移動平均線 (MA)
                ma_config = self.config['technical_indicators']['ma']
                for ma_name, period in ma_config.items():
                    if isinstance(period, int) and period < len(result):
                        result[f'ma_{period}'] = result['close'].rolling(
                            window=period).mean()

                # 計算 MACD
                macd_config = self.config['technical_indicators']['macd']
                exp1 = result['close'].ewm(
                    span=macd_config['fast_period'],
                    adjust=False
                ).mean()
                exp2 = result['close'].ewm(
                    span=macd_config['slow_period'],
                    adjust=False
                ).mean()
                result['macd'] = exp1 - exp2
                result['signal'] = result['macd'].ewm(
                    span=macd_config['signal_period'],
                    adjust=False
                ).mean()

                # 計算 RSI
                rsi_config = self.config['technical_indicators']['rsi']
                delta = result['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(
                    window=rsi_config['period']
                ).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(
                    window=rsi_config['period']
                ).mean()
                rs = gain / loss
                result['rsi'] = 100 - (100 / (1 + rs))

                # 計算布林通道
                bb_config = self.config['technical_indicators']['bollinger_bands']
                bb_period = int(bb_config['period'])
                bb_multiplier = float(bb_config['std_multiplier'])

                result['bb_middle'] = result['close'].rolling(window=bb_period).mean()
                bb_std = result['close'].rolling(window=bb_period).std()
                result['bb_upper'] = result['bb_middle'] + (bb_std * bb_multiplier)
                result['bb_lower'] = result['bb_middle'] - (bb_std * bb_multiplier)

                # 計算 ATR
                high_low = result['high'] - result['low']
                high_cp = abs(result['high'] - result['close'].shift())
                low_cp = abs(result['low'] - result['close'].shift())
                tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
                result['atr'] = tr.rolling(
                    window=self.config['technical_indicators']['atr']['period']
                ).mean()

                # 計算趨勢
                ma_period = ma_config.get('ma20', 20)  # 使用20日均線判斷趨勢
                if f'ma_{ma_period}' in result.columns:
                    result['trend'] = np.where(
                        result['close'] > result[f'ma_{ma_period}'],
                        1,  # 上升趨勢
                        np.where(
                            result['close'] < result[f'ma_{ma_period}'],
                            -1,  # 下降趨勢
                            0   # 盤整
                        )
                    )

                # 處理 NaN 值
                if self.config['data_processing']['dropna']:
                    result = result.dropna()

                return result

            except Exception as e:
                self.logger.error(f"計算技術指標時發生錯誤: {str(e)}")
                return None

        except Exception as e:
            self.logger.error(f"數據處理失敗: {str(e)}")
            return None
