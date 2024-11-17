# 視覺化處理
import matplotlib.pyplot as plt
import seaborn as sns


class visualizer:
    def plot(self, df, analysis_results):
        """繪製分析結果圖表"""
        # 設置圖表風格
        plt.style.use('seaborn')

        # 創建子圖
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 15))

        # 繪製價格和移動平均線
        ax1.plot(df.index, df['Close'], label='收盤價')
        ax1.plot(df.index, df['MA5'], label='MA5')
        ax1.plot(df.index, df['MA20'], label='MA20')
        ax1.set_title('股價走勢與移動平均線')
        ax1.legend()

        # 繪製RSI指標
        ax2.plot(df.index, df['RSI'], color='purple')
        ax2.axhline(y=70, color='r', linestyle='--')
        ax2.axhline(y=30, color='g', linestyle='--')
        ax2.set_title('RSI指標')

        # 繪製日收益率分布
        sns.histplot(df['Returns'], bins=50, ax=ax3)
        ax3.set_title('日收益率分布')

        plt.tight_layout()
        plt.savefig('data/stock_data/analysis_results.png')
        plt.close()
