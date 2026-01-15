#!/usr/bin/env python3
"""
生成結算日檢討報告 - 聚財網數據源版本
使用聚財網數據來生成結算盤後檢討

使用方式:
    python generate_settlement_review_wearn.py --settlement-date 20260116 --weekday friday
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import json

# 加入 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.wearn_fetcher import WearnFetcher
from src.parser import OptionsData
from src.analyzer import OptionsAnalyzer
from src.twse_fetcher import TWSEDataFetcher
from src.ai_settlement_review import AISettlementReview
from src.ai_settlement_prediction import AISettlementPrediction
from src.ai_learning_system import AILearningSystem


def fetch_settlement_data(settlement_date: str, weekday: str):
    """
    抓取結算日的數據
    
    Args:
        settlement_date: 結算日期 YYYYMMDD
        weekday: 'wednesday' or 'friday'
    
    Returns:
        OptionsData 物件
    """
    print(f"\n📡 正在抓取 {settlement_date} 的數據...")
    
    # 1. 抓取台指期貨數據
    twse_fetcher = TWSEDataFetcher()
    tx_data = twse_fetcher.fetch_ohlc(settlement_date)
    
    if not tx_data:
        print("  ⚠️  無法取得台指期貨數據，使用預設值")
        tx_data = {'close': 30800, 'open': 30800, 'high': 30850, 'low': 30750, 'settlement': 30800}
    else:
        print(f"  ✓ 台指期貨收盤: {tx_data.get('close', 'N/A')}")
        # 如果沒有結算價，使用收盤價
        if 'settlement' not in tx_data:
            tx_data['settlement'] = tx_data.get('close')
    
    # 2. 抓取聚財網選擇權數據
    wearn_fetcher = WearnFetcher()
    wearn_data = wearn_fetcher.fetch_all_weekly_contracts()
    
    if not wearn_data:
        print("  ❌ 無法抓取聚財網數據")
        return None, None
    
    # 3. 根據 weekday 選擇對應的契約
    contract_type = 'weekly_fri' if weekday == 'friday' else 'weekly_wed'
    contract_data = wearn_data.get(contract_type)
    
    if not contract_data:
        print(f"  ❌ 找不到 {weekday} 契約數據")
        return None, None
    
    # 4. 轉換為 OptionsData 格式
    strike_prices = [item['strike_price'] for item in contract_data['data']]
    call_oi = [item['call_oi'] for item in contract_data['data']]
    call_oi_change = [item['call_oi_change'] for item in contract_data['data']]
    put_oi = [item['put_oi'] for item in contract_data['data']]
    put_oi_change = [item['put_oi_change'] for item in contract_data['data']]
    
    page_title = '週五選擇權' if weekday == 'friday' else '週三選擇權'
    
    options_data = OptionsData(
        date=settlement_date,
        contract_month=contract_data['contract_code'][:6],
        strike_prices=strike_prices,
        call_volume=[0] * len(strike_prices),
        call_oi=call_oi,
        call_oi_change=call_oi_change,
        put_volume=[0] * len(strike_prices),
        put_oi=put_oi,
        put_oi_change=put_oi_change,
        contract_type=contract_type,
        contract_code=contract_data['contract_code'],
        page_title=page_title,
        settlement_date=settlement_date,
        tx_close=tx_data.get('close'),
        tx_open=tx_data.get('open'),
        tx_high=tx_data.get('high'),
        tx_low=tx_data.get('low'),
        tx_settlement=tx_data.get('settlement'),
    )
    
    print(f"  ✓ 契約: {options_data.contract_code}")
    print(f"  ✓ 數據筆數: {len(options_data.strike_prices)}")
    
    return options_data, tx_data


def main():
    parser = argparse.ArgumentParser(
        description='生成結算日檢討報告（聚財網數據源）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
    # 檢討週五結算
    python generate_settlement_review_wearn.py \\
        --settlement-date 20260116 \\
        --weekday friday
    
    # 檢討週三結算
    python generate_settlement_review_wearn.py \\
        --settlement-date 20260121 \\
        --weekday wednesday
        '''
    )
    
    parser.add_argument('--settlement-date', required=True, help='結算日期 YYYYMMDD')
    parser.add_argument('--weekday', required=True, choices=['wednesday', 'friday'], 
                       help='結算星期（wednesday 或 friday）')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"📝 結算日檢討報告生成器（聚財網數據源）")
    print(f"{'='*60}")
    print(f"結算日期: {args.settlement_date}")
    print(f"結算星期: {args.weekday}")
    
    # 1. 抓取結算日數據
    options_data, tx_data = fetch_settlement_data(args.settlement_date, args.weekday)
    
    if not options_data or not tx_data:
        print("\n❌ 無法取得數據，退出")
        return 1
    
    actual_settlement_price = int(tx_data.get('settlement', tx_data.get('close')))
    print(f"\n✅ 實際結算價: {actual_settlement_price:,}")
    
    # 2. 初始化 AI 系統
    print(f"\n🤖 初始化 AI 學習系統...")
    learning_system = AILearningSystem()
    prediction_generator = AISettlementPrediction(learning_system)
    review_generator = AISettlementReview(learning_system, prediction_generator)
    
    # 3. 生成檢討報告
    print(f"\n🔍 分析預測結果與實際結果...")
    
    actual_data = {
        'tx_close': int(tx_data.get('close')) if tx_data.get('close') else None,
        'tx_settlement': actual_settlement_price,
        'tx_high': int(tx_data.get('high')) if tx_data.get('high') else None,
        'tx_low': int(tx_data.get('low')) if tx_data.get('low') else None,
        'call_oi': sum(options_data.call_oi) if options_data.call_oi else 0,
        'put_oi': sum(options_data.put_oi) if options_data.put_oi else 0,
    }
    
    try:
        review = review_generator.generate_settlement_review(
            settlement_date=args.settlement_date,
            actual_settlement_price=actual_settlement_price,
            actual_data=actual_data
        )
        
        if 'error' in review:
            print(f"\n❌ {review['error']}")
            return 1
        
        # 4. 顯示檢討結果
        print(f"\n{'='*60}")
        print(f"✅ 檢討報告生成成功！")
        print(f"{'='*60}\n")
        
        print(f"📊 預測準確度: {review.get('accuracy_score', 'N/A')}/100")
        print(f"🎯 預測區間: {review.get('predicted_range', 'N/A')}")
        print(f"📍 實際結算: {actual_settlement_price:,}")
        print(f"✅ 發生劇本: {review.get('occurred_scenario', 'N/A')}")
        
        # 5. 顯示學習要點
        if 'key_learnings' in review and review['key_learnings']:
            print(f"\n💡 關鍵學習:")
            for i, learning in enumerate(review['key_learnings'], 1):
                print(f"  {i}. {learning}")
        
        # 6. 保存檢討報告
        review_dir = Path('data/ai_learning/settlement_reviews')
        review_dir.mkdir(parents=True, exist_ok=True)
        
        review_file = review_dir / f"review_{args.settlement_date}.json"
        with open(review_file, 'w', encoding='utf-8') as f:
            json.dump(review, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 檢討報告已保存: {review_file}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 生成檢討報告時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
