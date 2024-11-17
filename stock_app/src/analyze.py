import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


class analyzer:
    def analyze(self, df, density_range=5.0):
        """分析處理後的數據"""
        if df is None or df.empty:
            return None

        analysis_results = {}

        # 基本統計分析
        analysis_results['basic_stats'] = self.calculate_basic_stats(df)

        # 趨勢分析
        analysis_results['trend'] = self.analyze_trend(df)

        # 均線密集度分析
        analysis_results['ma_density'] = \
            self.analyze_moving_average_density(df)

        # 預測下一日價格
        analysis_results['prediction'] = self.predict_next_day(df)

        return analysis_results

    def calculate_basic_stats(self, df):
        """計算基本統計數據"""
        return {
            'mean_price': df['Close'].mean(),
            'std_price': df['Close'].std(),
            'max_price': df['Close'].max(),
            'min_price': df['Close'].min(),
            'daily_return_mean': df['Returns'].mean(),
            'daily_return_std': df['Returns'].std()
        }

    def analyze_trend(self, df):
        """分析價格趨勢"""
        current_price = df['Close'].iloc[-1]
        ma20 = df['MA20'].iloc[-1]
        ma5 = df['MA5'].iloc[-1]

        trend = {
            'current_price': current_price,
            'ma20': ma20,
            'ma5': ma5,
            'above_ma20': current_price > ma20,
            'above_ma5': current_price > ma5,
        }
        return trend

    def analyze_moving_average_density(self, df):
        """分析均線密集度"""
        ma_columns = ['MA5', 'MA20', 'MA60', 'MA120']

        # 檢查這些均線欄位是否都在 DataFrame 中
        if not all(col in df.columns for col in ma_columns):
            return None

        # 計算均線的標準差來判斷密集程度
        density = {
            'ma_std_dev': df[ma_columns].std().mean(),  # 均線標準差的平均
            'ma_variance': df[ma_columns].var().mean(),  # 均線方差的平均
        }

        # 比較相鄰均線的距離，分析是否密集
        density['ma_density'] = {
            'MA5_MA20_diff': np.abs(df['MA5'] - df['MA20']).mean(),
            'MA20_MA60_diff': np.abs(df['MA20'] - df['MA60']).mean(),
            'MA60_MA120_diff': np.abs(df['MA60'] - df['MA120']).mean(),
        }

        return density

    def predict_next_day(self, df):
        """使用簡單線性回歸預測下一日價格"""
        df['Target'] = df['Close'].shift(-1)
        df['Sequence'] = range(len(df))

        # 準備訓練數據
        X = df[['Sequence']].values[:-1]
        y = df['Target'].values[:-1]

        # 訓練模型
        model = LinearRegression()
        model.fit(X, y)

        # 預測下一日
        next_day = [[len(df)]]
        prediction = model.predict(next_day)

        return float(prediction[0])
