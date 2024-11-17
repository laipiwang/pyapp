# 主程式

from src.collect import collector
from src.process import processor
from src.analyze import analyzer
from src.visual import visualizer


def main():
    # 初始化各個模組
    data_collector = collector()
    data_processor = processor()
    data_analyzer = analyzer()
    data_visualizer = visualizer()

    # 參數初始化
    # stock_num = ''
    # start_date = ''
    # end_date = ''

    # list_of_ma_days = []


# 設定股票代碼（以台積電為例）
    stock_symbol = "2330.TW"

    # 1. 收集數據
    print("正在收集股票數據...")
    stock_data = data_collector.collection(stock_symbol)
    stock_info = data_collector.info_get(stock_symbol)

    if stock_data is None:
        print("無法收集數據，程序終止")
        return

    # 2. 處理數據
    print("正在處理數據...")
    processed_data = data_processor.process(stock_data)

    # 3. 分析數據
    print("正在分析數據...")
    analysis_results = data_analyzer.analyze(processed_data)

    # 4. 視覺化結果
    print("正在生成圖表...")
    data_visualizer.plot(processed_data, analysis_results)

    # 5. 輸出結果
    print("\n分析結果：")
    print(f"股票名稱: {stock_info['name']}")
    print(f"當前價格: {analysis_results['trend']['current_price']:.2f}")
    print(f"20日均線: {analysis_results['trend']['ma20']:.2f}")
    print(f"預測下一日價格: {analysis_results['prediction']:.2f}")


if __name__ == "__main__":
    main()
