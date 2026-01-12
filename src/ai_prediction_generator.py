"""
AI 交易員預測生成器
負責生成第一人稱的下個交易日預測
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
from pathlib import Path

class AIPredictionGenerator:
    """生成下個交易日的預測"""
    
    def __init__(self, learning_system):
        self.learning_system = learning_system
        self.predictions_dir = Path("data/ai_learning/predictions")
        self.predictions_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_prediction(self, options_data, analysis_date: str) -> Dict[str, Any]:
        """
        生成下個交易日的預測
        
        Args:
            options_data: 當日選擇權數據
            analysis_date: 分析日期 (YYYYMMDD)
            
        Returns:
            預測結果字典
        """
        # 計算關鍵指標
        tx_close = options_data.tx_close or 0
        
        # 計算 PC Ratio (Put OI / Call OI)
        total_call_oi = sum(options_data.call_oi) if options_data.call_oi else 1
        total_put_oi = sum(options_data.put_oi) if options_data.put_oi else 1
        pc_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0
        
        # 判斷市場情緒
        if pc_ratio > 1.2:
            sentiment = "看跌"
        elif pc_ratio < 0.8:
            sentiment = "看漲"
        else:
            sentiment = "中性"
        
        # 獲取歷史洞察
        insights = self.learning_system.get_historical_context(pc_ratio, sentiment)
        experience = self.learning_system.get_experience_level()
        
        # 生成預測
        prediction = {
            "prediction_date": analysis_date,
            "next_trading_day": self._get_next_trading_day(analysis_date),
            "experience_level": experience,
            "current_metrics": {
                "tx_close": tx_close,
                "pc_ratio": round(pc_ratio, 2),
                "call_oi": total_call_oi,
                "put_oi": total_put_oi,
            },
            "outlook": self._generate_market_outlook(tx_close, pc_ratio, insights),
            "direction_prediction": self._predict_direction(tx_close, pc_ratio, insights),
            "range_prediction": self._predict_range(tx_close, pc_ratio, insights),
            "strategy_recommendation": self._recommend_strategy(tx_close, pc_ratio, insights),
            "risk_warning": self._generate_risk_warning(pc_ratio, insights),
            "confidence_level": self._calculate_confidence(pc_ratio, insights),
            "key_levels": self._identify_key_levels(tx_close),
        }
        
        # 儲存預測
        self._save_prediction(prediction)
        
        return prediction
    
    def _get_next_trading_day(self, date_str: str) -> str:
        """計算下個交易日"""
        current = datetime.strptime(date_str, "%Y%m%d")
        next_day = current + timedelta(days=1)
        
        # 如果是週五，跳到下週一
        while next_day.weekday() >= 5:  # 5=Saturday, 6=Sunday
            next_day += timedelta(days=1)
        
        return next_day.strftime("%Y%m%d")
    
    def _generate_market_outlook(self, tx_close: float, pc_ratio: float, insights: Dict) -> str:
        """生成市場展望（第一人稱）"""
        
        outlook = "🔮 **明日市場展望**\n\n"
        
        # 根據 PC Ratio 判斷情緒
        if pc_ratio > 1.2:
            outlook += "我觀察到今天的 PC Ratio 達到 {:.2f}，市場恐慌情緒明顯升溫。".format(pc_ratio)
            outlook += "這種情況下，我傾向認為明天可能出現技術性反彈的機會。"
        elif pc_ratio < 0.8:
            outlook += "今天的 PC Ratio 僅 {:.2f}，市場過度樂觀讓我有些擔心。".format(pc_ratio)
            outlook += "我預期明天可能會有獲利回吐的壓力。"
        else:
            outlook += "今天的 PC Ratio 為 {:.2f}，處於相對平衡的狀態。".format(pc_ratio)
            outlook += "我認為明天盤勢將以區間震盪為主。"
        
        # 加入歷史經驗
        if insights.get("recent_insights"):
            outlook += f"\n\n根據我過去的經驗，類似的市場條件通常會..."
            for insight in insights["recent_insights"][:2]:
                if "pc_ratio" in insight.lower():
                    outlook += f"\n• {insight}"
        
        return outlook
    
    def _predict_direction(self, tx_close: float, pc_ratio: float, insights: Dict) -> Dict[str, Any]:
        """預測方向"""
        
        # 基於 PC Ratio 的方向判斷
        if pc_ratio > 1.2:
            direction = "看漲"
            probability = min(60 + (pc_ratio - 1.2) * 20, 75)
            reasoning = "恐慌情緒過高，通常是反彈訊號"
        elif pc_ratio < 0.8:
            direction = "看跌"
            probability = min(60 + (0.8 - pc_ratio) * 20, 75)
            reasoning = "樂觀情緒過度，可能有回檔壓力"
        else:
            direction = "震盪"
            probability = 55
            reasoning = "市場情緒中性，方向不明確"
        
        return {
            "direction": direction,
            "probability": round(probability, 1),
            "reasoning": reasoning,
        }
    
    def _predict_range(self, tx_close: float, pc_ratio: float, insights: Dict) -> Dict[str, Any]:
        """預測價格區間"""
        
        # 簡單的 ATR 估算（假設波動約 1-2%）
        volatility = 0.015  # 1.5% 預設波動
        
        upper = round(tx_close * (1 + volatility))
        lower = round(tx_close * (1 - volatility))
        
        return {
            "current": tx_close,
            "upper_bound": upper,
            "lower_bound": lower,
            "key_resistance": round(tx_close * 1.01),
            "key_support": round(tx_close * 0.99),
        }
    
    def _recommend_strategy(self, tx_close: float, pc_ratio: float, insights: Dict) -> Dict[str, Any]:
        """推薦策略"""
        direction = self._predict_direction(tx_close, pc_ratio, insights)
        
        if direction["direction"] == "看漲":
            strategy = {
                "primary": "買進 Call / 賣出 Put",
                "alternative": "Bull Call Spread",
                "entry_timing": "開盤後等待回檔進場",
                "stop_loss": "跌破當日低點",
            }
        elif direction["direction"] == "看跌":
            strategy = {
                "primary": "買進 Put / 賣出 Call",
                "alternative": "Bear Put Spread",
                "entry_timing": "反彈時分批進場",
                "stop_loss": "突破當日高點",
            }
        else:
            strategy = {
                "primary": "Iron Condor / Butterfly",
                "alternative": "觀望為主",
                "entry_timing": "區間震盪時布局",
                "stop_loss": "破區間立即出場",
            }
        
        return strategy
    
    def _generate_risk_warning(self, pc_ratio: float, insights: Dict) -> str:
        """生成風險警告"""
        warnings = []
        
        if pc_ratio > 1.5:
            warnings.append("⚠️ PC Ratio 極高，市場恐慌可能導致劇烈波動")
        elif pc_ratio < 0.6:
            warnings.append("⚠️ PC Ratio 極低，小心樂極生悲")
        
        # 加入固定風險提醒
        warnings.append("⚠️ 請務必設定停損點，控制單筆風險在 2% 以內")
        warnings.append("⚠️ 預測僅供參考，實際應根據盤中變化調整")
        
        return "\n".join(warnings)
    
    def _calculate_confidence(self, pc_ratio: float, insights: Dict) -> int:
        """計算信心水準 (0-100)"""
        base_confidence = 50
        
        # 根據歷史記錄數量調整
        record_count = len(insights.get("recent_insights", []))
        confidence = base_confidence + min(record_count * 2, 30)
        
        # 根據 PC Ratio 極端程度調整
        if pc_ratio > 1.3 or pc_ratio < 0.7:
            confidence += 10  # 極端值時信心較高
        
        return min(confidence, 85)  # 最高不超過 85%
    
    def _identify_key_levels(self, tx_close: float) -> Dict[str, int]:
        """識別關鍵價位"""
        
        # 計算整數關卡
        round_100 = round(tx_close / 100) * 100
        round_50 = round(tx_close / 50) * 50
        
        return {
            "current_close": tx_close,
            "nearest_100": round_100,
            "nearest_50": round_50,
            "psychological_high": round_100 + 100,
            "psychological_low": round_100 - 100,
        }
    
    def _save_prediction(self, prediction: Dict):
        """儲存預測到 JSON 文件"""
        filename = f"prediction_{prediction['prediction_date']}.json"
        filepath = self.predictions_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(prediction, f, ensure_ascii=False, indent=2)
    
    def load_prediction(self, date: str) -> Optional[Dict]:
        """載入指定日期的預測"""
        filename = f"prediction_{date}.json"
        filepath = self.predictions_dir / filename
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
