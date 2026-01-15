#!/usr/bin/env python3
"""
台指選擇權分析工具

使用方式:
    python main.py                    # 下載最新 PDF 並產生報告
    python main.py --date 20260109    # 分析指定日期
    python main.py --download-only    # 僅下載不分析
    python main.py --local FILE.pdf   # 分析本地 PDF 檔案
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# 加入 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.fetcher import PDFFetcher
from src.parser import PDFParser
from src.analyzer import OptionsAnalyzer
from src.reporter import ReportGenerator
from src.wearn_fetcher import WearnFetcher


def main():
    parser = argparse.ArgumentParser(
        description='台指選擇權分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  python main.py                    下載最新 PDF 並產生報告
  python main.py --date 20260109    分析指定日期的報告
  python main.py --download-only    僅下載 PDF 不進行分析
  python main.py --local file.pdf   分析本地的 PDF 檔案
        '''
    )

    parser.add_argument(
        '--date', '-d',
        type=str,
        help='指定日期 (格式: YYYYMMDD)'
    )

    parser.add_argument(
        '--download-only',
        action='store_true',
        help='僅下載 PDF 不進行分析'
    )

    parser.add_argument(
        '--local', '-l',
        type=str,
        help='分析本地 PDF 檔案'
    )

    parser.add_argument(
        '--wearn',
        action='store_true',
        help='從聚財網抓取選擇權數據（包含週三、週五、近月三個契約）'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='報告輸出目錄'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='顯示詳細資訊'
    )

    args = parser.parse_args()

    try:
        run_analysis(args)
    except KeyboardInterrupt:
        print("\n已取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n錯誤: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_analysis(args):
    """執行分析流程"""

    project_root = Path(__file__).parent
    pdf_path = None
    options_list = []

    # 使用聚財網數據
    if args.wearn:
        print("=" * 50)
        print("台指選擇權分析工具 - 聚財網數據源")
        print("=" * 50)
        print("\n正在從聚財網抓取選擇權數據...")
        
        wearn_fetcher = WearnFetcher()
        wearn_data = wearn_fetcher.fetch_all_weekly_contracts()
        
        if not wearn_data:
            print("\n無法從聚財網獲取數據")
            return
        
        # 將聚財網數據轉換為 OptionsData 格式
        from src.parser import OptionsData
        from src.twse_fetcher import TWSEDataFetcher
        
        # 嘗試獲取台指期貨數據
        twse_fetcher = TWSEDataFetcher()
        today_str = datetime.now().strftime('%Y%m%d')
        tx_data = twse_fetcher.fetch_ohlc(today_str)
        
        if tx_data:
            print(f"成功取得台指期貨數據: 收盤 {tx_data.get('close', 'N/A')}")
        else:
            print("警告: 無法取得台指期貨數據，將使用預設值")
            # 使用一個合理的預設值（約當前加權指數）
            tx_data = {'close': 30800, 'open': 30800, 'high': 30800, 'low': 30800}
        
        for contract_type, data in wearn_data.items():
            # 提取所有數據到列表
            strike_prices = []
            call_oi = []
            call_oi_change = []
            put_oi = []
            put_oi_change = []
            
            for item in data['data']:
                strike_prices.append(item['strike_price'])
                call_oi.append(item['call_oi'])
                call_oi_change.append(item['call_oi_change'])
                put_oi.append(item['put_oi'])
                put_oi_change.append(item['put_oi_change'])
            
            # 確定契約類型顯示名稱
            if contract_type == 'weekly_fri':
                page_title = '週五選擇權'
            elif contract_type == 'weekly_wed':
                page_title = '週三選擇權'
            else:
                page_title = '近月選擇權'
            
            options_data = OptionsData(
                date=datetime.now().strftime('%Y%m%d'),
                contract_month=data['contract_code'][:6],  # YYYYMM
                strike_prices=strike_prices,
                call_volume=[0] * len(strike_prices),  # 聚財網沒有成交量數據
                call_oi=call_oi,
                call_oi_change=call_oi_change,
                put_volume=[0] * len(strike_prices),
                put_oi=put_oi,
                put_oi_change=put_oi_change,
                contract_type=contract_type,
                contract_code=data['contract_code'],
                page_title=page_title,
                settlement_date='',  # 聚財網沒有提供到期日
                # 使用台指期貨數據
                tx_close=tx_data.get('close') if tx_data else None,
                tx_open=tx_data.get('open') if tx_data else None,
                tx_high=tx_data.get('high') if tx_data else None,
                tx_low=tx_data.get('low') if tx_data else None,
            )
            options_list.append(options_data)
        
        print(f"成功抓取 {len(options_list)} 個契約的數據")
        for opt in options_list:
            print(f"  - {opt.page_title} ({opt.contract_code}): {len(opt.strike_prices)} 筆數據")
    
    # 取得 PDF 檔案
    elif args.local:
        # 使用本地檔案
        pdf_path = Path(args.local)
        if not pdf_path.exists():
            raise FileNotFoundError(f"找不到檔案: {pdf_path}")
        print(f"使用本地檔案: {pdf_path}")

    else:
        # 從網站下載
        fetcher = PDFFetcher()

        print("=" * 50)
        print("台指選擇權分析工具")
        print("=" * 50)

        if args.date:
            print(f"\n正在下載 {args.date} 的報告...")
            pdf_path = fetcher.download_report(args.date)
        else:
            print("\n正在下載最新報告...")
            pdf_path = fetcher.download_latest()

        if not pdf_path:
            print("\n無法下載 PDF 檔案")
            print("可能原因:")
            print("  1. 網站需要登入")
            print("  2. PDF 連結結構已變更")
            print("  3. 指定日期的報告不存在")
            print("\n請手動下載 PDF 後使用 --local 參數分析")
            return

    if args.download_only:
        print(f"\n已下載: {pdf_path}")
        return

    # 如果不是使用聚財網數據，需要解析 PDF
    if not args.wearn:
        # 解析 PDF
        print(f"\n正在解析 PDF...")
        pdf_parser = PDFParser()
        options_list = pdf_parser.parse(str(pdf_path))

        if not options_list:
            print("\n無法從 PDF 中解析出選擇權資料")
            print("可能原因:")
            print("  1. PDF 格式與預期不符")
            print("  2. PDF 內容為掃描圖片而非文字")
            return

        print(f"找到 {len(options_list)} 組資料")

    # 分析資料
    print("\n正在分析資料...")
    analyzer = OptionsAnalyzer()
    reporter = ReportGenerator(
        output_dir=args.output if args.output else project_root / "reports"
    )

    reports = []
    
    # 如果有多個契約類型（週選+月選），生成綜合報告
    if len(options_list) > 1:
        print(f"\n發現 {len(options_list)} 種契約類型:")
        for opt in options_list:
            type_name = opt.page_title or opt.contract_type or "未知"
            print(f"  - {type_name} ({opt.contract_code}), 結算日: {opt.settlement_date}")
        
        # 使用第一個契約的日期作為主報告
        main_options = options_list[0]
        main_result = analyzer.analyze(main_options)
        
        # 顯示主要契約的摘要
        print(f"\n--- 主要契約: {main_options.contract_code} ---")
        print(f"  Max Pain: {main_result.max_pain:,}")
        print(f"  P/C Ratio (OI): {main_result.pc_ratio_oi:.4f}")
        
        # 產生包含所有契約的綜合報告
        report_path = reporter.generate_multi_contract_report(options_list, analyzer)
        reports.append(report_path)
        
    else:
        # 單一契約，使用原有流程
        for options_data in options_list:
            result = analyzer.analyze(options_data)

            # 顯示摘要
            print(f"\n--- {options_data.contract_month} 月份 ---")
            print(f"  Max Pain: {result.max_pain:,}")
            print(f"  P/C Ratio (OI): {result.pc_ratio_oi:.4f}")
            print(f"  買權 OI 壓力: {result.max_call_oi_strike:,} ({result.max_call_oi:,} 口)")
            print(f"  賣權 OI 支撐: {result.max_put_oi_strike:,} ({result.max_put_oi:,} 口)")

            # 產生報告
            report_path = reporter.generate(result, options_data)
            reports.append(report_path)

    print("\n" + "=" * 50)
    print("分析完成!")
    print("=" * 50)
    print("\n產生的報告:")
    for path in reports:
        print(f"  - {path}")

    # 嘗試開啟報告
    if reports:
        try:
            import webbrowser
            webbrowser.open(f"file://{reports[0]}")
            print(f"\n已在瀏覽器中開啟報告")
        except Exception:
            pass


if __name__ == "__main__":
    main()
