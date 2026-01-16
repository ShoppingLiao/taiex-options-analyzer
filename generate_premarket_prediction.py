#!/usr/bin/env python3
"""
結算日盤前預測生成腳本

在結算日（週三或週五）早上 08:00 執行：
1. 抓取前一天夜盤資料
2. 載入前一天的交易員視角分析
3. 載入原本的結算預測
4. 生成盤前預測
5. 更新結算報告（加入盤前預測 tab）

使用方式:
    python generate_premarket_prediction.py --settlement-date 20260116 --weekday friday
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# 加入 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.night_session_fetcher import NightSessionFetcher
from src.ai_premarket_prediction import AIPremarketPrediction
from src.settlement_report_generator import SettlementReportGenerator
from src.settlement_predictor import SettlementPredictor


def get_previous_trading_day(date_obj: datetime) -> datetime:
    """取得前一個交易日"""
    from daily_workflow import is_trading_day

    prev_day = date_obj - timedelta(days=1)
    while not is_trading_day(prev_day)[0]:
        prev_day -= timedelta(days=1)
    return prev_day


def load_settlement_prediction(settlement_date: str, weekday: str) -> dict:
    """載入結算預測"""
    # 嘗試從 AI 學習系統載入預測
    from src.ai_settlement_prediction import AISettlementPrediction
    from src.ai_learning_system import AILearningSystem

    learning_system = AILearningSystem()
    prediction_system = AISettlementPrediction(learning_system)

    prediction = prediction_system.load_prediction(settlement_date)
    if prediction:
        return {
            'overall_trend': prediction.get('trend', 'neutral'),
            'predicted_range': [
                prediction.get('predicted_low', 30500),
                prediction.get('predicted_high', 31000)
            ],
            'current_price': prediction.get('base_price', 30800)
        }

    # 如果沒有預測記錄，返回預設值
    return {
        'overall_trend': 'neutral',
        'predicted_range': [30500, 31000],
        'current_price': 30800
    }


def load_trader_analysis(settlement_date: str) -> dict:
    """載入前一天的交易員視角分析"""
    # 交易員分析可能保存在結算報告的 JSON 中
    data_dir = Path('data/ai_learning')

    # 嘗試載入分析記錄
    analysis_file = data_dir / f'trader_analysis_{settlement_date}.json'
    if analysis_file.exists():
        with open(analysis_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    return None


def main():
    parser = argparse.ArgumentParser(
        description='結算日盤前預測生成',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--settlement-date', '-d',
        required=True,
        help='結算日期 (YYYYMMDD)'
    )

    parser.add_argument(
        '--weekday', '-w',
        required=True,
        choices=['wednesday', 'friday'],
        help='結算日是週幾 (wednesday 或 friday)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='顯示詳細資訊'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("結算日盤前預測生成")
    print("=" * 60)
    print(f"結算日期: {args.settlement_date}")
    print(f"星期: {'週三' if args.weekday == 'wednesday' else '週五'}")
    print()

    try:
        # 1. 計算前一天日期
        settlement_date_obj = datetime.strptime(args.settlement_date, '%Y%m%d')
        prev_date_obj = get_previous_trading_day(settlement_date_obj)
        prev_date = prev_date_obj.strftime('%Y%m%d')

        print(f"📅 前一交易日: {prev_date}")

        # 2. 抓取前一天夜盤資料
        print("\n🌙 抓取夜盤資料...")
        night_fetcher = NightSessionFetcher()
        night_data = night_fetcher.fetch_night_session(prev_date)

        if not night_data:
            print("❌ 無法獲取夜盤資料")
            sys.exit(1)

        print(f"   開盤: {night_data['open']:,.0f}")
        print(f"   最高: {night_data['high']:,.0f}")
        print(f"   最低: {night_data['low']:,.0f}")
        print(f"   收盤: {night_data['close']:,.0f}")
        print(f"   震幅: {night_data['amplitude']:,.0f} 點")
        if night_data.get('is_estimated'):
            print("   ⚠️  此為估算值")

        # 3. 載入原本的結算預測
        print("\n📊 載入結算預測...")
        settlement_pred = load_settlement_prediction(args.settlement_date, args.weekday)
        print(f"   預測區間: {settlement_pred['predicted_range'][0]:,} ~ {settlement_pred['predicted_range'][1]:,}")
        print(f"   整體趨勢: {settlement_pred['overall_trend']}")

        # 4. 載入交易員視角分析
        print("\n🧑‍💼 載入交易員視角分析...")
        trader_analysis = load_trader_analysis(prev_date)
        if trader_analysis:
            print("   ✅ 已載入交易員分析")
        else:
            print("   ⚠️  無交易員分析記錄")

        # 5. 生成盤前預測
        print("\n🎯 生成盤前預測...")
        premarket_predictor = AIPremarketPrediction()
        premarket_data = premarket_predictor.generate_premarket_prediction(
            night_session_data=night_data,
            previous_trader_analysis=trader_analysis,
            settlement_prediction=settlement_pred,
            settlement_date=args.settlement_date
        )

        adjusted_range = premarket_data['adjusted_prediction']['adjusted_range']
        print(f"   調整後區間: {adjusted_range[0]:,} ~ {adjusted_range[1]:,}")
        print(f"   預測信心: {premarket_data['adjusted_prediction']['confidence']}")

        # 6. 更新結算報告
        print("\n📝 更新結算報告...")

        # 重新生成結算報告，加入盤前預測
        predictor = SettlementPredictor()

        # 取得分析日期（前兩個交易日）
        from daily_workflow import is_trading_day
        analysis_dates = []
        current = settlement_date_obj - timedelta(days=1)
        while len(analysis_dates) < 2:
            if is_trading_day(current)[0]:
                analysis_dates.append(current.strftime('%Y%m%d'))
            current -= timedelta(days=1)
        analysis_dates = list(reversed(analysis_dates))

        # 生成預測
        settlement_date_formatted = settlement_date_obj.strftime('%Y/%m/%d')
        prediction = predictor.predict_settlement(
            dates=analysis_dates,
            settlement_date=settlement_date_formatted,
            settlement_weekday=args.weekday
        )

        # 生成報告（包含盤前預測）
        generator = SettlementReportGenerator()
        report_path = generator.generate_report(
            prediction=prediction,
            premarket_data=premarket_data
        )

        print(f"   ✅ 報告已更新: {report_path}")

        # 7. 顯示摘要
        print("\n" + "=" * 60)
        print("盤前預測摘要")
        print("=" * 60)
        print(premarket_data['analysis_text'])

        print("\n✅ 盤前預測生成完成！")
        return 0

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
