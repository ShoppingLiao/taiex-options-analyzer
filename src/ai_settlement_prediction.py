"""
AI 結算日預測生成器
使用前兩天的數據預測結算日可能的結算價
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

CALIBRATION_FILE = Path("data/ai_learning/calibration.json")

# 預設值（calibration 不存在時使用）
DEFAULT_HALF_RANGE = {"wednesday": 1000, "friday": 150}
DEFAULT_SCENARIO_PROBS = {
    "wednesday": {"in_range": 40.0, "breakout_up": 30.0, "breakout_down": 30.0},
    "friday": {"in_range": 60.0, "breakout_up": 20.0, "breakout_down": 20.0},
}


def _load_calibration() -> dict:
    """載入校準參數"""
    if CALIBRATION_FILE.exists():
        try:
            return json.loads(CALIBRATION_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


class AISettlementPrediction:
    """AI 結算日預測生成器"""

    def __init__(self, learning_system):
        self.learning_system = learning_system
        self.predictions_dir = Path("data/ai_learning/settlement_predictions")
        self.predictions_dir.mkdir(parents=True, exist_ok=True)
        self._calibration = _load_calibration()
    
    def generate_settlement_prediction(
        self, 
        historical_data: List[Dict],  # 前兩天的數據
        settlement_date: str,  # 結算日期 YYYYMMDD
        weekday: str  # 'wednesday' or 'friday'
    ) -> Dict[str, Any]:
        """
        生成結算日預測
        
        Args:
            historical_data: 前兩天的選擇權數據列表 [day1, day2]
            settlement_date: 結算日期
            weekday: 星期幾
            
        Returns:
            預測結果字典
        """
        
        # 分析歷史趨勢
        trend_analysis = self._analyze_trend(historical_data)
        
        # 獲取經驗等級
        experience = self.learning_system.get_experience_level()
        
        # 生成結算價預測
        settlement_price_prediction = self._predict_settlement_price(historical_data, trend_analysis, weekday)
        
        # 生成情境分析
        scenarios = self._generate_scenarios(historical_data, settlement_price_prediction, weekday)
        
        # 生成策略建議
        strategy = self._recommend_settlement_strategy(settlement_price_prediction, trend_analysis, weekday)
        
        # 第一人稱展望
        outlook = self._generate_settlement_outlook(
            historical_data, 
            settlement_price_prediction, 
            trend_analysis,
            weekday
        )
        
        prediction = {
            "prediction_date": datetime.now().strftime("%Y%m%d"),
            "settlement_date": settlement_date,
            "settlement_weekday": weekday,
            "experience_level": experience,
            "historical_data": self._summarize_historical_data(historical_data),
            "trend_analysis": trend_analysis,
            "settlement_price_prediction": settlement_price_prediction,
            "scenarios": scenarios,
            "strategy_recommendation": strategy,
            "outlook": outlook,
            "confidence_level": self._calculate_settlement_confidence(historical_data, trend_analysis),
        }
        
        # 儲存預測
        self._save_prediction(prediction)
        
        return prediction
    
    def _analyze_trend(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """分析兩天的趨勢"""
        if len(historical_data) < 2:
            return {"trend": "insufficient_data"}
        
        day1, day2 = historical_data[0], historical_data[1]
        
        # 價格趨勢
        price_change = day2["tx_close"] - day1["tx_close"]
        price_change_pct = (price_change / day1["tx_close"] * 100) if day1["tx_close"] > 0 else 0
        
        # PC Ratio 趨勢
        pc_change = day2["pc_ratio"] - day1["pc_ratio"]
        
        # 判斷趨勢方向
        if abs(price_change_pct) < 0.5:
            trend_direction = "盤整"
        elif price_change > 0:
            trend_direction = "上漲"
        else:
            trend_direction = "下跌"
        
        # 情緒變化
        if pc_change > 0.1:
            sentiment_change = "恐慌升溫"
        elif pc_change < -0.1:
            sentiment_change = "樂觀增強"
        else:
            sentiment_change = "情緒穩定"
        
        return {
            "trend_direction": trend_direction,
            "price_change": price_change,
            "price_change_pct": round(price_change_pct, 2),
            "pc_change": round(pc_change, 2),
            "sentiment_change": sentiment_change,
            "momentum": "strong" if abs(price_change_pct) > 1.0 else "moderate" if abs(price_change_pct) > 0.5 else "weak"
        }
    
    def _predict_settlement_price(self, historical_data: List[Dict], trend: Dict, weekday: str = "friday") -> Dict[str, Any]:
        """預測結算價"""
        if len(historical_data) < 2:
            return {"error": "insufficient_data"}
        
        day1, day2 = historical_data[0], historical_data[1]
        
        # 基準價：第二天收盤價
        base_price = day2["tx_close"]
        
        # 根據趨勢調整預測
        if trend["trend_direction"] == "上漲":
            # 上漲趨勢，預測繼續上漲但幅度減半
            predicted_change = trend["price_change"] * 0.5
        elif trend["trend_direction"] == "下跌":
            # 下跌趨勢，預測繼續下跌但幅度減半
            predicted_change = trend["price_change"] * 0.5
        else:
            # 盤整，預測小幅波動
            predicted_change = 0
        
        predicted_settlement = round(base_price + predicted_change)

        # 從校準參數取得對應週別的建議半徑
        weekday_stats = self._calibration.get("weekday", {}).get(weekday, {})
        half_range = weekday_stats.get(
            "recommended_half_range",
            DEFAULT_HALF_RANGE.get(weekday, 300)
        )

        lower_bound = (predicted_settlement - half_range) // 50 * 50
        upper_bound = (predicted_settlement + half_range) // 50 * 50

        # 關鍵整數關卡
        round_100 = round(predicted_settlement / 100) * 100

        return {
            "predicted_price": predicted_settlement,
            "upper_bound": upper_bound,
            "lower_bound": lower_bound,
            "base_price": base_price,
            "expected_change": round(predicted_change),
            "nearest_100": round_100,
            "confidence_range": f"±{half_range}點",
        }
    
    def _generate_scenarios(
        self,
        historical_data: List[Dict],
        settlement_pred: Dict,
        weekday: str
    ) -> List[Dict]:
        """生成結算日情境（機率來自校準資料）"""
        # 從校準參數取得情境機率
        cal_probs = (
            self._calibration.get("scenario_probabilities", {}).get(weekday)
            or DEFAULT_SCENARIO_PROBS.get(weekday, {"in_range": 50.0, "breakout_up": 25.0, "breakout_down": 25.0})
        )

        p_in_range = cal_probs["in_range"]
        p_up = cal_probs["breakout_up"]
        p_down = cal_probs["breakout_down"]

        scenarios = [
            {
                "name": "✅ 符合預期情境",
                "description": f"結算價落在預測區間 {settlement_pred['lower_bound']:,} - {settlement_pred['upper_bound']:,}",
                "probability": p_in_range,
                "strategy": "按照原定策略執行",
                "action": "持有部位至結算",
            },
            {
                "name": "📈 超預期上漲",
                "description": f"結算價突破 {settlement_pred['upper_bound']:,}",
                "probability": p_up,
                "strategy": "Call 部位獲利，Put 可能止損",
                "action": "考慮提前調整 Put 部位",
            },
            {
                "name": "📉 超預期下跌",
                "description": f"結算價跌破 {settlement_pred['lower_bound']:,}",
                "probability": p_down,
                "strategy": "Put 部位獲利，Call 可能止損",
                "action": "考慮提前調整 Call 部位",
            },
        ]

        return scenarios
    
    def _recommend_settlement_strategy(
        self,
        settlement_pred: Dict,
        trend: Dict,
        weekday: str
    ) -> Dict[str, Any]:
        """推薦結算日策略"""
        
        strategy = {
            "before_settlement": {
                "timing": "結算日09:00前",
                "action": "觀察開盤價格，決定是否提前調整",
                "caution": "避免追高殺低"
            },
            "during_settlement": {
                "timing": "13:30-13:45 (結算區間)",
                "action": "密切關注結算價形成過程",
                "caution": "注意最後五分鐘的劇烈波動"
            },
            "position_management": {
                "if_bullish": "持有 Call 至結算，Put 考慮提前平倉",
                "if_bearish": "持有 Put 至結算，Call 考慮提前平倉",
                "if_neutral": "採取 Straddle 或 Strangle，兩邊對沖"
            },
            "risk_control": {
                "stop_loss": "當走勢明顯偏離預測時，立即止損",
                "position_size": "結算日部位不超過平時的50%",
                "time_decay": f"{'週三結算影響較小' if weekday == 'wednesday' else '週五結算時間價值歸零，需特別注意'}"
            }
        }
        
        return strategy
    
    def _generate_settlement_outlook(
        self,
        historical_data: List[Dict],
        settlement_pred: Dict,
        trend: Dict,
        weekday: str
    ) -> str:
        """生成第一人稱結算展望"""
        
        day2 = historical_data[1] if len(historical_data) >= 2 else historical_data[0]
        
        weekday_zh = "週三" if weekday == "wednesday" else "週五"
        
        outlook = f"🔮 **{weekday_zh}結算日展望**\n\n"
        
        outlook += f"經過這兩天的盤勢觀察，我看到市場呈現{trend['trend_direction']}的態勢，"
        outlook += f"價格{('上漲' if trend['price_change'] > 0 else '下跌')} {abs(trend['price_change'])} 點。\n\n"
        
        outlook += f"今天的收盤價是 {day2['tx_close']:,}，PC Ratio 為 {day2['pc_ratio']:.2f}。"
        
        if day2['pc_ratio'] > 1.1:
            outlook += "市場恐慌情緒明顯，我認為這可能是個反轉訊號。"
        elif day2['pc_ratio'] < 0.9:
            outlook += "市場過度樂觀，結算前可能會有修正。"
        else:
            outlook += "市場情緒相對平衡，結算應該不會有太大意外。"
        
        outlook += f"\n\n基於這些觀察，我預測{weekday_zh}的結算價會在 **{settlement_pred['predicted_price']:,}** 附近，"
        outlook += f"合理區間應該是 {settlement_pred['lower_bound']:,} 到 {settlement_pred['upper_bound']:,}。"
        
        outlook += f"\n\n{'週三結算只影響當週契約，對整體市場衝擊較小。' if weekday == 'wednesday' else '週五是大結算日，需要特別注意最後時段的波動。'}"
        
        outlook += "\n\n我會密切關注開盤後的走勢，適時調整部位。"
        
        return outlook
    
    def _calculate_settlement_confidence(self, historical_data: List[Dict], trend: Dict) -> int:
        """計算結算預測信心水準"""
        base_confidence = 50
        
        # 根據趨勢明確度調整
        if trend["momentum"] == "strong":
            base_confidence += 15
        elif trend["momentum"] == "moderate":
            base_confidence += 10
        
        # 根據數據完整度調整
        if len(historical_data) >= 2:
            base_confidence += 10
        
        # 經驗加成
        record_count = len(self.learning_system.records)
        base_confidence += min(record_count, 15)
        
        return min(base_confidence, 80)  # 最高80%
    
    def _summarize_historical_data(self, historical_data: List[Dict]) -> List[Dict]:
        """摘要歷史數據"""
        summary = []
        for i, data in enumerate(historical_data, 1):
            summary.append({
                "day": i,
                "date": data.get("date", "unknown"),
                "tx_close": data["tx_close"],
                "pc_ratio": data["pc_ratio"],
                "call_oi": data.get("call_oi", 0),
                "put_oi": data.get("put_oi", 0)
            })
        return summary
    
    def _save_prediction(self, prediction: Dict):
        """儲存預測到 JSON"""
        filename = f"settlement_prediction_{prediction['settlement_date']}.json"
        filepath = self.predictions_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(prediction, f, ensure_ascii=False, indent=2)
    
    def load_prediction(self, settlement_date: str) -> Optional[Dict]:
        """載入結算日預測"""
        filename = f"settlement_prediction_{settlement_date}.json"
        filepath = self.predictions_dir / filename
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
