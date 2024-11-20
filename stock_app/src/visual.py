import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from src.utils.config_loader import ConfigLoader


class Visualizer:
    def __init__(self):
        config_loader = ConfigLoader()
        self.config = config_loader.get_config()
        self.logger = logging.getLogger('stock_analysis.visualizer')

        # 加載視覺化配置
        self.visual_params = self.config['visualization']

        # 設置圖表風格
        self.theme = self.visual_params.get('theme', 'plotly_dark')
        self.colors = self.visual_params.get('colors', {
            'up': '#00ff00',
            'down': '#ff0000',
            'line': '#ffffff',
            'volume': '#888888'
        })

    def create_analysis_dashboard(
            self, df: pd.DataFrame,
            analysis_results: Dict
            ) -> Dict:
        """創建完整的分析儀表板"""
        try:
            # 原本想用元祖把df跟an_re包起來的
            charts = {
                'price_chart': self._create_price_chart(df),
                'technical_indicators': self._create_technical_chart(df),
                'volume_analysis': self._create_volume_chart(df),
                'pattern_analysis': self._create_pattern_chart(
                    df, analysis_results),
                'correlation_matrix': self._create_correlation_matrix(df)
            }
            return charts
        except Exception as e:
            self.logger.error(f"創建儀表板失敗: {str(e)}")
            return None

    def _create_price_chart(self, df: pd.DataFrame) -> go.Figure:
        """創建價格走勢圖"""
        fig = go.Figure()

        # 添加K線圖
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K線'
        ))

        # 添加移動平均線
        ma_config = self.config['technical_indicators']['ma']

        for period in [f'MA{days}' for days in ma_config]:
            if f'ma_{period}' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df[f'ma_{period}'],
                    name=f'MA{period}',
                    line=dict(width=1)
                ))

        # 更新布局
        fig.update_layout(
            title='股價走勢圖',
            yaxis_title='價格',
            template=self.theme,
            xaxis_rangeslider_visible=False
        )

        return fig

    def _create_technical_chart(self, df: pd.DataFrame) -> go.Figure:
        """創建技術指標圖"""
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('RSI', 'MACD', 'Bollinger Bands')
            )

        # RSI
        fig.add_trace(go.Scatter(
            x=df.index, y=df['rsi'],
            name='RSI',
            line=dict(color='purple')
        ), row=1, col=1)

        # MACD
        fig.add_trace(go.Scatter(
            x=df.index, y=df['macd'],
            name='MACD',
            line=dict(color='blue')
        ), row=2, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['signal'],
            name='Signal',
            line=dict(color='orange')
        ), row=2, col=1)

        # Bollinger Bands
        fig.add_trace(go.Scatter(
            x=df.index, y=df['bb_upper'],
            name='Upper BB',
            line=dict(color='gray', dash='dash')
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['bb_middle'],
            name='Middle BB',
            line=dict(color='blue')
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['bb_lower'],
            name='Lower BB',
            line=dict(color='gray', dash='dash')
        ), row=3, col=1)

        fig.update_layout(height=900, template=self.theme)
        return fig

    def _create_volume_chart(self, df: pd.DataFrame) -> go.Figure:
        """創建成交量圖"""
        fig = go.Figure()

        colors = [self.colors['up']
                  if df['close'].iloc[i] > df['close'].iloc[i-1]
                  else self.colors['down']
                  for i in range(1, len(df))]
        colors.insert(0, self.colors['volume'])

        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            name='Volume',
            marker_color=colors
        ))

        fig.update_layout(
            title='成交量分析',
            yaxis_title='成交量',
            template=self.theme
        )

        return fig

    def _create_pattern_chart(
            self, df: pd.DataFrame,
            analysis_results: Dict
            ) -> go.Figure:
        """創建形態分析圖"""
        fig = go.Figure()

        # 添加價格線
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['close'],
            name='收盤價',
            line=dict(color=self.colors['line'])
        ))

        # 添加支撐和阻力位
        if 'pattern_analysis' in analysis_results:
            patterns = analysis_results['pattern_analysis']
            support = patterns.get('support_level')
            resistance = patterns.get('resistance_level')

            if support:
                fig.add_hline(y=support, line_dash="dash",
                              annotation_text="支撐位")
            if resistance:
                fig.add_hline(y=resistance, line_dash="dash",
                              annotation_text="阻力位")

        fig.update_layout(
            title='形態分析',
            template=self.theme
        )

        return fig

    def _create_correlation_matrix(self, df: pd.DataFrame) -> go.Figure:
        """創建相關性矩陣圖"""
        # 選擇數值型列
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlation = df[numeric_cols].corr()

        fig = go.Figure(data=go.Heatmap(
            z=correlation,
            x=correlation.columns,
            y=correlation.columns,
            colorscale='RdBu'
        ))

        fig.update_layout(
            title='相關性矩陣',
            template=self.theme
        )

        return fig

    def save_charts(self, charts: Dict[str, go.Figure], output_dir: str):
        """保存圖表"""
        import os

        try:
            os.makedirs(output_dir, exist_ok=True)

            for name, fig in charts.items():
                output_path = os.path.join(output_dir, f"{name}.html")
                fig.write_html(output_path)
                self.logger.info(f"已保存圖表: {output_path}")

        except Exception as e:
            self.logger.error(f"保存圖表失敗: {str(e)}")
