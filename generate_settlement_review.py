#!/usr/bin/env python3
"""
生成結算日檢討報告
"""

import sys
import argparse
from pathlib import Path
from src.parser import PDFParser
from src.ai_settlement_review import AISettlementReview
from src.ai_settlement_prediction import AISettlementPrediction
from src.ai_learning_system import AILearningSystem


def main():
    parser = argparse.ArgumentParser(description='生成結算日檢討報告')
    parser.add_argument('--settlement-date', required=True, help='結算日期 YYYYMMDD')
    parser.add_argument('--pdf-path', required=True, help='結算日 PDF 檔案路徑')
    
    args = parser.parse_args()
    
    settlement_date = args.settlement_date
    pdf_path = args.pdf_path
    
    print(f"\n{'='*60}")
    print(f"📝 生成結算檢討報告")
    print(f"{'='*60}\n")
    
    # 1. 解析結算日數據
    print(f"📂 解析 PDF: {pdf_path}")
    pdf_parser = PDFParser()
    
    try:
        data_list = pdf_parser.parse(pdf_path)
        if not data_list:
            print("❌ 無法解析 PDF 數據")
            return 1
        
        data = data_list[0]
        actual_settlement_price = int(data.tx_settlement) if data.tx_settlement else int(data.tx_close)
        
        print(f"✅ 實際結算價: {actual_settlement_price:,}")
        
    except Exception as e:
        print(f"❌ 解析 PDF 失敗: {e}")
        return 1
    
    # 2. 初始化 AI 系統
    learning_system = AILearningSystem()
    prediction_generator = AISettlementPrediction(learning_system)
    review_generator = AISettlementReview(learning_system, prediction_generator)
    
    # 3. 生成檢討報告
    print(f"\n🔍 分析預測結果...")
    
    actual_data = {
        'tx_close': int(data.tx_close) if data.tx_close else None,
        'tx_settlement': actual_settlement_price,
        'tx_high': int(data.tx_high) if data.tx_high else None,
        'tx_low': int(data.tx_low) if data.tx_low else None,
        'call_oi': sum(data.call_oi) if data.call_oi else 0,
        'put_oi': sum(data.put_oi) if data.put_oi else 0,
    }
    
    try:
        review = review_generator.generate_settlement_review(
            settlement_date=settlement_date,
            actual_settlement_price=actual_settlement_price,
            actual_data=actual_data
        )
        
        if 'error' in review:
            print(f"❌ {review['error']}")
            return 1
        
        # 4. 顯示檢討結果
        print(f"\n{'='*60}")
        print(f"✅ 檢討報告生成成功！")
        print(f"{'='*60}\n")
        
        accuracy = review['accuracy']
        
        print(f"🏆 總體評分: {review['score']}")
        print(f"\n📊 準確度分析:")
        print(f"   預測價格: {accuracy['predicted_price']:,}")
        print(f"   實際價格: {accuracy['actual_price']:,}")
        print(f"   價格誤差: {accuracy['price_error']:.0f} 點 ({accuracy['price_error_percent']:.2f}%)")
        print(f"   預測區間: {accuracy['predicted_range']}")
        print(f"   區間預測: {'✅ 在區間內' if accuracy['in_predicted_range'] else '❌ 超出區間'}")
        print(f"   方向預測: {'✅ 正確' if accuracy['direction_correct'] else '❌ 錯誤'}")
        print(f"   綜合準確度: {accuracy['overall_accuracy']}%")
        
        print(f"\n💡 自我反思:")
        for i, reflection in enumerate(review['self_reflection'][:3], 1):
            print(f"   {i}. {reflection}")
        
        print(f"\n📚 學到的經驗:")
        for i, lesson in enumerate(review['lessons_learned'][:3], 1):
            print(f"   {i}. {lesson}")
        
        if 'improvement_areas' in review and review['improvement_areas']:
            print(f"\n🎯 改進方向:")
            for i, area in enumerate(review['improvement_areas'][:2], 1):
                print(f"   {i}. {area}")
        
        print(f"\n📝 儲存位置:")
        review_file = review_generator.reviews_dir / f'settlement_review_{settlement_date}.json'
        print(f"   {review_file}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 生成檢討失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
