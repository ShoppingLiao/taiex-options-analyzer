#!/usr/bin/env python3
"""
結算日報告生成工具

使用方式:
    python generate_settlement_report.py --dates 20260105,20260106 --settlement 2026/01/07 --weekday wednesday
    python generate_settlement_report.py --dates 20260107,20260108 --settlement 2026/01/09 --weekday friday
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# 加入 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.settlement_predictor import SettlementPredictor
from src.settlement_report_generator import SettlementReportGenerator


def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description='結算日報告生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
    # 預測週三結算（使用週一二數據）
    python generate_settlement_report.py \\
        --dates 20260105,20260106 \\
        --settlement 2026/01/07 \\
        --weekday wednesday
    
    # 預測週五結算（使用週三四數據）
    python generate_settlement_report.py \\
        --dates 20260107,20260108 \\
        --settlement 2026/01/09 \\
        --weekday friday
        '''
    )
    
    parser.add_argument(
        '--dates',
        required=True,
        help='分析數據日期（逗號分隔，格式: YYYYMMDD），例如: 20260105,20260106'
    )
    
    parser.add_argument(
        '--settlement',
        required=True,
        help='結算日期（格式: YYYY/MM/DD），例如: 2026/01/07'
    )
    
    parser.add_argument(
        '--weekday',
        required=True,
        choices=['wednesday', 'friday'],
        help='結算星期: wednesday（週三）或 friday（週五）'
    )
    
    parser.add_argument(
        '--output',
        help='輸出檔名（可選），例如: settlement_20260107_wed.html'
    )
    
    return parser.parse_args()


def main():
    """主程式"""
    args = parse_arguments()
    
    # 解析日期列表
    dates = [d.strip() for d in args.dates.split(',')]
    
    # 驗證日期格式
    for date in dates:
        if len(date) != 8 or not date.isdigit():
            print(f'❌ 錯誤: 日期格式不正確 "{date}"，應為 YYYYMMDD')
            return 1
    
    # 驗證結算日期格式
    try:
        settlement_dt = datetime.strptime(args.settlement, '%Y/%m/%d')
    except ValueError:
        print(f'❌ 錯誤: 結算日期格式不正確 "{args.settlement}"，應為 YYYY/MM/DD')
        return 1
    
    # 驗證結算日期必須是週三或週五
    weekday = settlement_dt.weekday()  # 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
    weekday_name = settlement_dt.strftime('%A')
    
    if args.weekday == 'wednesday' and weekday != 2:
        print(f'❌ 錯誤: 指定為週三結算，但 {args.settlement} 是 {weekday_name}（週{["一", "二", "三", "四", "五", "六", "日"][weekday]}）')
        print(f'   提示: 選擇權結算日只會在週三和週五')
        return 1
    
    if args.weekday == 'friday' and weekday != 4:
        print(f'❌ 錯誤: 指定為週五結算，但 {args.settlement} 是 {weekday_name}（週{["一", "二", "三", "四", "五", "六", "日"][weekday]}）')
        print(f'   提示: 選擇權結算日只會在週三和週五')
        return 1
    
    print('\n🎯 結算日報告生成工具')
    print('=' * 50)
    print(f'分析日期: {", ".join(dates)}')
    print(f'結算日期: {args.settlement} ({args.weekday})')
    print('=' * 50)
    
    # 創建預測器
    predictor = SettlementPredictor()
    
    print('\n📊 分析中...')
    
    # 執行預測
    try:
        prediction = predictor.predict_settlement(
            dates=dates,
            settlement_date=args.settlement,
            settlement_weekday=args.weekday
        )
    except Exception as e:
        print(f'\n❌ 預測分析失敗: {e}')
        return 1
    
    # 顯示預測結果
    print('\n📈 預測結果:')
    print(f'  整體趨勢: {prediction.overall_trend_text}')
    print(f'  趨勢強度: {prediction.trend_strength}/5 星')
    print(f'  當前價格: {prediction.current_price:,}')
    print(f'  預測區間: {prediction.predicted_range[0]:,} ~ {prediction.predicted_range[1]:,}')
    
    print(f'\n📡 趨勢訊號 ({len(prediction.trend_signals)} 個):')
    for signal in prediction.trend_signals:
        icon = {'bullish': '📈', 'bearish': '📉', 'neutral': '➖'}[signal.direction]
        print(f'  {icon} [{signal.strength}/5] {signal.description}')
    
    print(f'\n🎬 結算劇本 ({len(prediction.scenarios)} 個):')
    for i, scenario in enumerate(prediction.scenarios, 1):
        print(f'  {i}. {scenario.icon} {scenario.name} ({scenario.probability:.1f}%)')
        print(f'     區間: {scenario.price_range[0]:,} ~ {scenario.price_range[1]:,}')
    
    if prediction.risks:
        print(f'\n⚠️  風險提示 ({len(prediction.risks)} 項):')
        for risk in prediction.risks:
            print(f'  {risk}')
    
    # 生成報告
    print('\n📝 生成報告中...')
    
    try:
        generator = SettlementReportGenerator()
        report_path = generator.generate_report(
            prediction=prediction,
            output_filename=args.output
        )
        
        print(f'\n✅ 報告生成成功!')
        print(f'   檔案位置: {report_path}')
        print(f'   瀏覽器開啟: file://{report_path.absolute()}')
        
        return 0
        
    except Exception as e:
        print(f'\n❌ 報告生成失敗: {e}')
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
