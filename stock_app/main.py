import sys
import yaml
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

from src.collect import Collector
from src.process import Processor
from src.analyze import Analyzer
from src.visual import Visualizer
from src.utils.logger import setup_logging
from src.utils.decorators import timing_decorator, error_handler


class StockAnalyzer:
    def __init__(self, config):
        self.config = config
        self.logger = setup_logging()
        self.initialize_components()

    @error_handler
    def initialize_components(self):
        """初始化所有組件"""
        self.collector = Collector()
        self.processor = Processor()
        self.analyzer = Analyzer()
        self.visualizer = Visualizer()  # 移除參數，使用統一配置

    @timing_decorator
    @error_handler
    def run(self, symbol):
        """執行分析流程"""
        try:
            # 收集數據
            self.logger.info(f"開始收集 {symbol} 的數據...")
            stock_data = self.collector.collect(
                symbol,
                start_date=self.config['data_collection']
                ['default_start_date'],
                end_date=self.config['data_collection']
                ['default_end_date']
            )

            if stock_data is None:
                self.logger.error(f"收集 {symbol} 的數據失敗")
                return None

            stock_info = self.collector.get_info(symbol)  # 修正方法名稱
            if stock_info is None:
                self.logger.error(f"獲取 {symbol} 的信息失敗")
                return None

            # 處理數據
            self.logger.info("處理數據...")
            processed_data = self.processor.process(stock_data)
            if processed_data is None:
                self.logger.error("數據處理失敗")
                return None

            # 分析數據
            self.logger.info("分析數據...")
            analysis_results = self.analyzer.analyze(processed_data)
            if analysis_results is None:
                self.logger.error("數據分析失敗")
                return None

            # 視覺化
            self.logger.info("生成視覺化結果...")
            charts = self.visualizer.create_analysis_dashboard(
                processed_data,
                analysis_results
            )
            if charts is None:
                self.logger.error("視覺化生成失敗")
                return None

            # 輸出結果
            self.output_results(symbol, stock_info, analysis_results, charts)
            return True

        except Exception as e:
            self.logger.error(f"分析過程發生錯誤: {str(e)}")
            return None

    def output_results(self, symbol, stock_info, results, charts):
        """輸出分析結果"""
        try:
            result_current = results['technical_analysis']['current_price']
            output = {
                "股票代碼": symbol,
                "股票名稱": stock_info.get('name', 'Unknown'),
                "當前價格": f"{result_current:.2f}",
                "20日均線": f"{results['technical_analysis'].get('ma20', 0):.2f}",
                "RSI": f"{results['technical_analysis'].get('rsi', 0):.2f}",
                "MACD": f"{results['technical_analysis'].get('macd', 0):.2f}",
                "趨勢": results['trend_analysis'].get('direction', 'Unknown'),
                "分析時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # 保存結果
            self.save_results(output)
            self.visualizer.save_charts(charts, self.config['base']
                                        ['output_dir'])

            # 打印結果
            for key, value in output.items():
                self.logger.info(f"{key}: {value}")

        except Exception as e:
            self.logger.error(f"輸出結果時發生錯誤: {str(e)}")

    def save_results(self, results):
        """保存結果到文件"""
        try:
            output_dir = Path(self.config['base']['output_dir'])
            output_dir.mkdir(exist_ok=True)

            filename = \
                output_dir / f"analysis_{datetime.now():%Y%m%d_%H%M%S}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            self.logger.info(f"結果已保存到: {filename}")

        except Exception as e:
            self.logger.error(f"保存結果失敗: {str(e)}")


def load_config(config_path):
    """加載配置文件"""
    try:
        # 使用絕對路徑
        config_path = Path(config_path).resolve()
        if not config_path.exists():
            logging.error(f"找不到配置文件: {config_path}")
            return None

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    except Exception as e:
        logging.error(f"加載配置文件失敗: {str(e)}")
        return None


def parse_arguments():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description='股票分析程序')
    parser.add_argument('--symbol', type=str, help='股票代碼，多個代碼用逗號分隔')
    # 修改默認配置文件路徑
    default_config = str(Path(__file__).parent / 'config' / 'config.yaml')
    parser.add_argument('--config', type=str, default=default_config,
                        help='配置文件路徑')
    return parser.parse_args()


def main():
    """主入口函數"""
    try:
        # 解析參數
        args = parse_arguments()

        # 加載配置
        config = load_config(args.config)
        if config is None:
            return 1

        # 創建分析器實例
        analyzer = StockAnalyzer(config)

        # 獲取要分析的股票列表
        symbols = args.symbol.split(',') if args.symbol \
            else config.get('default_symbols', [])
        if not symbols:
            logging.error("未指定股票代碼且配置中沒有默認股票")
            return 1

        # 執行分析
        success = True
        for symbol in symbols:
            if analyzer.run(symbol) is None:
                logging.error(f"分析股票 {symbol} 失敗")
                success = False

        return 0 if success else 1

    except Exception as e:
        logging.error(f"程序執行失敗: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
