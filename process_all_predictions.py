"""
批次處理所有報告的預測與檢討
按照時間順序：預測 -> 檢討 -> 學習
"""

import sys
from pathlib import Path
from datetime import datetime

# 加入 src 目錄到路徑
sys.path.insert(0, str(Path(__file__).parent / "src"))

from parser import PDFParser
from ai_learning_system import AILearningSystem
from ai_prediction_generator import AIPredictionGenerator
from ai_review_analyzer import AIReviewAnalyzer

def main():
    """
    處理流程：
    1. 0105 生成預測 -> 0106 檢討
    2. 0106 生成預測 -> 0107 檢討
    3. 0107 生成預測 -> 0108 檢討
    4. 0108 生成預測 -> 0109 檢討
    """
    
    # 初始化系統
    print("🚀 初始化 AI 學習系統...")
    learning_system = AILearningSystem()
    prediction_generator = AIPredictionGenerator(learning_system)
    review_analyzer = AIReviewAnalyzer(learning_system, prediction_generator)
    parser = PDFParser()
    
    # 定義處理順序
    dates = [
        "20260105",
        "20260106", 
        "20260107",
        "20260108",
        "20260109",
    ]
    
    print("\n" + "="*60)
    print("開始處理每日預測與檢討")
    print("="*60 + "\n")
    
    # 處理每個日期
    for i, date in enumerate(dates):
        print(f"\n{'='*60}")
        print(f"📅 處理日期：{date}")
        print(f"{'='*60}\n")
        
        # 解析當日數據
        pdf_path = f"data/pdf/期貨選擇權盤後日報_{date}.pdf"
        
        try:
            # 檢查 PDF 是否存在
            if not Path(pdf_path).exists():
                print(f"⚠️  找不到 PDF 檔案：{pdf_path}")
                continue
            
            print(f"📖 解析 {date} 的數據...")
            options_data_list = parser.parse(pdf_path)
            
            # 取第一個月份的數據（通常是近月）
            if not options_data_list:
                print(f"⚠️  無法解析 {date} 的數據")
                continue
            
            options_data = options_data_list[0]  # 使用第一個月份的數據
            
            # 步驟 1: 生成明日預測
            print(f"\n🔮 生成 {date} 對下個交易日的預測...")
            prediction = prediction_generator.generate_prediction(options_data, date)
            
            print(f"✅ 預測完成！")
            print(f"   - 預測方向：{prediction['direction_prediction']['direction']}")
            print(f"   - 信心水準：{prediction['confidence_level']}%")
            print(f"   - 目標日期：{prediction['next_trading_day']}")
            
            # 步驟 2: 如果有下一天的數據，進行檢討
            if i < len(dates) - 1:
                next_date = dates[i + 1]
                next_pdf = f"data/pdf/期貨選擇權盤後日報_{next_date}.pdf"
                
                if Path(next_pdf).exists():
                    print(f"\n📊 載入 {next_date} 的實際數據進行檢討...")
                    actual_data_list = parser.parse(next_pdf)
                    
                    if not actual_data_list:
                        print(f"⚠️  無法解析 {next_date} 的數據")
                        continue
                    
                    actual_data = actual_data_list[0]  # 使用第一個月份的數據
                    
                    print(f"🔍 生成檢討報告...")
                    review = review_analyzer.generate_review(date, actual_data)
                    
                    if "error" not in review:
                        accuracy = review["accuracy"]["overall_accuracy"]
                        score = review["score"]
                        
                        print(f"✅ 檢討完成！")
                        print(f"   - 準確度：{accuracy}%")
                        print(f"   - 評分：{score}")
                        print(f"   - 方向正確：{'✓' if review['accuracy']['direction_correct'] else '✗'}")
                        print(f"   - 價格誤差：{review['accuracy']['price_error']} 點")
                        
                        # 顯示學到的教訓
                        if review["lessons_learned"]:
                            print(f"\n📝 學到的教訓：")
                            for lesson in review["lessons_learned"]:
                                print(f"   • {lesson}")
                    else:
                        print(f"⚠️  {review['error']}")
                else:
                    print(f"⚠️  找不到 {next_date} 的數據，無法進行檢討")
            
            print(f"\n✨ {date} 處理完成！")
            
        except Exception as e:
            print(f"❌ 處理 {date} 時發生錯誤：{str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*60)
    print("🎉 所有報告處理完成！")
    print("="*60)
    
    # 顯示學習系統統計
    print("\n📊 學習系統統計：")
    experience = learning_system.get_experience_level()
    print(f"   - 經驗等級：{experience}")
    print(f"   - 預測記錄：{len(list(Path('data/ai_learning/predictions').glob('*.json')))} 筆")
    print(f"   - 檢討記錄：{len(list(Path('data/ai_learning/reviews').glob('*.json')))} 筆")
    
    print("\n💾 所有數據已儲存到：")
    print("   - data/ai_learning/predictions/")
    print("   - data/ai_learning/reviews/")

if __name__ == "__main__":
    main()
