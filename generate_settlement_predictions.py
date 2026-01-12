"""
生成結算日 AI 預測
使用前兩天的數據來預測結算日
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.parser import PDFParser
from src.ai_learning_system import AILearningSystem
from src.ai_settlement_prediction import AISettlementPrediction


def main():
    """生成所有結算日的 AI 預測"""
    
    # 初始化系統
    parser = PDFParser()
    learning_system = AILearningSystem()
    settlement_prediction = AISettlementPrediction(learning_system)
    
    # 定義結算日和其前兩日
    settlements = [
        {
            "settlement_date": "20260107",  # 週三結算
            "weekday": "wednesday",
            "historical_dates": ["20260105", "20260106"]  # 週一、週二
        },
        {
            "settlement_date": "20260109",  # 週五結算  
            "weekday": "friday",
            "historical_dates": ["20260107", "20260108"]  # 週三、週四
        }
    ]
    
    print("=" * 80)
    print("開始生成結算日 AI 預測")
    print("=" * 80)
    
    for settlement in settlements:
        settlement_date = settlement["settlement_date"]
        weekday = settlement["weekday"]
        historical_dates = settlement["historical_dates"]
        
        weekday_zh = "週三" if weekday == "wednesday" else "週五"
        print(f"\n處理 {settlement_date} ({weekday_zh}結算)")
        print(f"使用 {historical_dates[0]} 和 {historical_dates[1]} 的數據")
        
        try:
            # 載入前兩日數據
            historical_data = []
            
            for date in historical_dates:
                print(f"  載入 {date} 數據...")
                
                # PDF 檔案路徑
                pdf_path = Path(f"data/pdf/期貨選擇權盤後日報_{date}.pdf")
                
                if not pdf_path.exists():
                    print(f"  ⚠️  找不到 PDF: {pdf_path}")
                    continue
                
                # 解析 PDF
                options_data_list = parser.parse(str(pdf_path))
                
                if not options_data_list or len(options_data_list) == 0:
                    print(f"  ⚠️  {date} 無法解析數據")
                    continue
                
                # 取第一個月份的數據
                options_data = options_data_list[0]
                
                # 計算總 OI
                total_call_oi = sum(options_data.call_oi)
                total_put_oi = sum(options_data.put_oi)
                
                # 準備數據格式
                data = {
                    "date": date,
                    "tx_close": options_data.tx_close,
                    "call_oi": total_call_oi,
                    "put_oi": total_put_oi,
                    "pc_ratio": total_put_oi / total_call_oi if total_call_oi > 0 else 0,
                    "call_volume": options_data.call_volume,
                    "put_volume": options_data.put_volume,
                }
                
                historical_data.append(data)
                print(f"  ✅ {date} 數據載入成功 (TX收盤: {options_data.tx_close:,})")
            
            # 檢查是否有兩天數據
            if len(historical_data) < 2:
                print(f"  ❌ 數據不足，無法生成預測 (需要 2 天，實際 {len(historical_data)} 天)")
                continue
            
            # 生成預測
            print(f"  🔮 生成 {weekday_zh}結算預測...")
            prediction = settlement_prediction.generate_settlement_prediction(
                historical_data=historical_data,
                settlement_date=settlement_date,
                weekday=weekday
            )
            
            # 顯示預測結果
            print(f"\n  ✨ {weekday_zh}結算預測完成！")
            print(f"  📊 趨勢: {prediction['trend_analysis']['trend_direction']}")
            print(f"  🎯 預測結算價: {prediction['settlement_price_prediction']['predicted_price']:,}")
            print(f"  📈 預測區間: {prediction['settlement_price_prediction']['lower_bound']:,} - {prediction['settlement_price_prediction']['upper_bound']:,}")
            print(f"  💪 信心度: {prediction['confidence_level']}%")
            
        except Exception as e:
            print(f"  ❌ 生成預測時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "=" * 80)
    print("結算日 AI 預測生成完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
