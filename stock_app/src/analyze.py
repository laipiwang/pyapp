import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging
from src.utils.config_loader import ConfigLoader


class Analyzer:
    def __init__(self):
        config_loader = ConfigLoader()
        self.config = config_loader.get_config()
        self.logger = logging.getLogger('stock_analysis.analyzer')

        # 加載分析參數
        self.analysis_params = self.config['analysis']

    def analyze(self, df: pd.DataFrame) -> Dict:
        """執行完整的分析流程"""
        try:
            results = {
                'technical_analysis': self._technical_analysis(df),
                'trend_analysis': self._trend_analysis(df),
                'pattern_analysis': self._pattern_analysis(df),
                'risk_analysis': self._risk_analysis(df),
                'prediction': self._make_prediction(df)
            }
            return results
        except Exception as e:
            self.logger.error(f"分析過程發生錯誤: {str(e)}")
            return None

    def _technical_analysis(self, df: pd.DataFrame) -> Dict:
        """技術分析"""
        try:
            latest = df.iloc[-1]
            prev = df.iloc[-2]

            # 計算基本變化
            price_change = \
                (latest['close'] - prev['close']) / prev['close'] * 100
            volume_change = \
                (latest['volume'] - prev['volume']) / prev['volume'] * 100

            # RSI 狀態
            rsi_status = (
                'oversold' if latest['rsi'] < 30
                else 'overbought' if latest['rsi'] > 70
                else 'neutral'
            )

            # MACD 信號
            macd_signal = 'buy' \
                if latest['macd'] > latest['signal'] else 'sell'

            # 趨勢強度 - 使用移動平均線判斷
            ma20 = latest.get('ma_20', latest['close'])
            trend_strength = abs((latest['close'] - ma20) / ma20 * 100)

            analysis = {
                'current_price': latest['close'],
                'price_change': price_change,
                'volume_change': volume_change,
                'rsi_status': rsi_status,
                'macd_signal': macd_signal,
                'trend_strength': trend_strength  # 添加趨勢強度
            }

            return analysis

        except Exception as e:
            self.logger.error(f"執行技術分析時發生錯誤: {str(e)}")
            return None

    def _trend_analysis(self, df: pd.DataFrame) -> Dict:
        """趨勢分析"""
        # 計算各種時間週期的趨勢
        periods = [self.config['data_processing']['time_range']]
        trends = {}

        for period in periods:
            price_for_now = df['close'].iloc[-1] - df['close'].iloc[-period]
            price_change = price_for_now / df['close'].iloc[-period] * 100
            trends[f'{period}d_trend'] = {
                'direction': 'up' if price_change > 0 else 'down',
                'change_percent': price_change
            }

        return trends

    def _pattern_analysis(self, df: pd.DataFrame) -> Dict:
        """形態分析"""
        patterns = {}

        # 計算K線形態
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # 十字星形態
        doji = abs(latest['open'] - latest['close']) <= (
            latest['high'] - latest['low']
            ) * 0.1

        # 錘子線形態
        diff_of_latest = latest['high'] - latest['low']
        diff_of_OC = latest['open'] - latest['close']
        diff_OC_low = min(latest['open'], latest['close']) - latest['low']
        hammer = (
            diff_of_latest > 3 * abs(diff_of_OC) and
            diff_OC_low > 2 * abs(diff_of_OC)
                )

        patterns.update({
            'doji': doji,
            'hammer': hammer,
            'support_level': self._find_support(df),
            'resistance_level': self._find_resistance(df)
        })

        return patterns

    def _risk_analysis(self, df: pd.DataFrame) -> Dict:
        """風險分析"""
        returns = df['close'].pct_change()

        risk_metrics = {
            'volatility': returns.std() * np.sqrt(252),  # 年化波動率
            'var_95': returns.quantile(0.05),  # 95% VaR
            'max_drawdown': self._calculate_max_drawdown(df['close']),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'beta': self._calculate_beta(df)
        }

        return risk_metrics

    def _make_prediction(self, df: pd.DataFrame) -> Dict:
        """預測分析"""
        try:
            from sklearn.ensemble import RandomForestRegressor

            # 準備特徵
            feature_cols = [col for col in df.columns if
                            col.endswith('_normalized')]
            X = df[feature_cols].fillna(0)
            y = df['close']

            # 分割數據
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )

            # 訓練模型
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)

            # 預測
            last_data = X.iloc[-1:]
            prediction = model.predict(last_data)[0]

            return {
                'predicted_price': prediction,
                'confidence': model.score(X_test, y_test),
                'prediction_date': df.index[-1] + pd.Timedelta(days=1)
            }

        except Exception as e:
            self.logger.error(f"預測失敗: {str(e)}")
            return None

    def _find_support(self, df: pd.DataFrame, window: int = 20) -> float:
        """找出支撐位"""
        return df['low'].rolling(window=window).min().iloc[-1]

    def _find_resistance(self, df: pd.DataFrame, window: int = 20) -> float:
        """找出阻力位"""
        return df['high'].rolling(window=window).max().iloc[-1]

    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """計算最大回撤"""
        peak = prices.expanding(min_periods=1).max()
        drawdown = (prices - peak) / peak
        return drawdown.min()

    def _calculate_sharpe_ratio(self, returns: pd.Series,
                                risk_free_rate: float = 0.02) -> float:
        """計算夏普比率"""
        excess_returns = returns - risk_free_rate/252
        return np.sqrt(252) * excess_returns.mean() / returns.std()

    def _calculate_beta(self, df: pd.DataFrame) -> float:
        """計算貝塔係數"""
        # 這裡需要市場指數數據才能計算真實的貝塔係數
        # 這是一個簡化的計算
        return df['close'].pct_change().std() * np.sqrt(252)

        # df是來自process return的result(DataFrame)
    def _ma_dense(self, df: pd.DataFrame, dense_parameters: float)\
            -> pd.DataFrame:
        # 確保所有必要的均線列都存在
        ma_config = self.config['technical_indicators']['ma']
        required_columns = [f"MA{days}" for days in ma_config.values()]
        missing_columns = [col for col in required_columns
                           if col not in df.columns]
        if missing_columns:
            raise ValueError(f"缺少必要的列: {missing_columns}")

        # 初始化結果
        results = []

        for idx, row in df.iterrows():
            # 判斷是否有數據缺失
            ma_values = row[required_columns]
            if ma_values.isnull().any():
                missing_days = max(120 - idx, 0)
                results.append({'date': idx,
                                'dense': None,
                                'missing_days': missing_days})
                continue

            # 計算均線間的最大差距
            ma_diff = ma_values.max() - ma_values.min()

            # 判斷是否密集
            is_dense = ma_diff <= dense_parameters
            results.append({'date': idx,
                            'dense': is_dense,
                            'missing_days': None})

        # 返回結果 DataFrame
        return pd.DataFrame(results)
