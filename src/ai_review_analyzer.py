"""
AI 交易員檢討分析器
比較預測與實際結果，生成檢討報告
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

class AIReviewAnalyzer:
    """生成預測檢討報告"""
    
    def __init__(self, learning_system, prediction_generator):
        self.learning_system = learning_system
        self.prediction_generator = prediction_generator
        self.reviews_dir = Path("data/ai_learning/reviews")
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_review(self, prediction_date: str, actual_data) -> Dict[str, Any]:
        """
        生成檢討報告
        
        Args:
            prediction_date: 預測日期 (YYYYMMDD)
            actual_data: 實際的選擇權數據
            
        Returns:
            檢討報告字典
        """
        # 載入預測
        prediction = self.prediction_generator.load_prediction(prediction_date)
        
        if not prediction:
            return {
                "error": f"找不到 {prediction_date} 的預測記錄",
                "review_date": prediction_date,
            }
        
        # 計算實際結果
        actual_date = prediction["next_trading_day"]
        actual_tx = actual_data.tx_close or 0
        
        # 計算實際的 PC Ratio
        total_call_oi = sum(actual_data.call_oi) if actual_data.call_oi else 1
        total_put_oi = sum(actual_data.put_oi) if actual_data.put_oi else 1
        actual_pc_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0
        
        # 計算預測準確度
        accuracy = self._calculate_accuracy(prediction, actual_data)
        
        # 生成檢討內容
        review = {
            "prediction_date": prediction_date,
            "actual_date": actual_date,
            "prediction": prediction,
            "actual_result": {
                "tx_close": actual_tx,
                "pc_ratio": round(actual_pc_ratio, 2),
                "call_oi": total_call_oi,
                "put_oi": total_put_oi,
            },
            "accuracy": accuracy,
            "self_reflection": self._generate_reflection(prediction, actual_data, accuracy),
            "lessons_learned": self._extract_lessons(prediction, actual_data, accuracy),
            "improvement_areas": self._identify_improvements(accuracy),
            "score": self._calculate_score(accuracy),
        }
        
        # 儲存檢討
        self._save_review(review)
        
        # 更新學習系統
        self._update_learning_system(review)
        
        return review
    
    def _calculate_accuracy(self, prediction: Dict, actual_data) -> Dict[str, Any]:
        """計算各項預測的準確度"""
        pred_range = prediction["range_prediction"]
        actual_tx = actual_data.tx_close or 0
        predicted_tx = pred_range["current"]
        
        # 方向準確度
        direction_correct = self._check_direction_accuracy(prediction, actual_data)
        
        # 價格準確度
        price_error = abs(actual_tx - predicted_tx)
        price_error_percent = (price_error / predicted_tx * 100) if predicted_tx > 0 else 100
        
        # 區間準確度
        in_range = pred_range["lower_bound"] <= actual_tx <= pred_range["upper_bound"]
        
        return {
            "direction_correct": direction_correct,
            "price_error": price_error,
            "price_error_percent": round(price_error_percent, 2),
            "in_predicted_range": in_range,
            "overall_accuracy": self._calculate_overall_accuracy(
                direction_correct, price_error_percent, in_range
            ),
        }
    
    def _check_direction_accuracy(self, prediction: Dict, actual_data) -> bool:
        """檢查方向預測是否正確"""
        pred_direction = prediction["direction_prediction"]["direction"]
        pred_tx = prediction["range_prediction"]["current"]
        actual_tx = actual_data.tx_close or 0
        
        actual_change = actual_tx - pred_tx
        
        if pred_direction == "看漲" and actual_change > 0:
            return True
        elif pred_direction == "看跌" and actual_change < 0:
            return True
        elif pred_direction == "震盪" and abs(actual_change) < pred_tx * 0.005:  # 0.5% 內算震盪
            return True
        
        return False
    
    def _calculate_overall_accuracy(self, direction_correct: bool, 
                                   price_error_percent: float, 
                                   in_range: bool) -> float:
        """計算總體準確度分數 (0-100)"""
        score = 0
        
        # 方向正確 +40 分
        if direction_correct:
            score += 40
        
        # 價格誤差 (最多 +40 分)
        if price_error_percent < 0.5:
            score += 40
        elif price_error_percent < 1.0:
            score += 30
        elif price_error_percent < 2.0:
            score += 20
        elif price_error_percent < 3.0:
            score += 10
        
        # 在預測區間內 +20 分
        if in_range:
            score += 20
        
        return score
    
    def _generate_reflection(self, prediction: Dict, actual_data, 
                            accuracy: Dict) -> str:
        """生成第一人稱的自我反思"""
        actual_tx = actual_data.tx_close or 0
        pred_tx = prediction["range_prediction"]["current"]
        pred_direction = prediction["direction_prediction"]["direction"]
        
        reflection = "📝 **盤後自我檢討**\n\n"
        
        # 整體表現
        overall = accuracy["overall_accuracy"]
        if overall >= 80:
            reflection += "今天的預測相當準確，我感到很滿意！"
        elif overall >= 60:
            reflection += "今天的預測還算可以，但還有進步空間。"
        elif overall >= 40:
            reflection += "今天的預測不夠準確，我需要好好檢討。"
        else:
            reflection += "今天的預測失誤了，這是個重要的學習機會。"
        
        reflection += f"（準確度：{overall}%）\n\n"
        
        # 方向分析
        if accuracy["direction_correct"]:
            reflection += f"✅ **方向判斷正確**：我預測{pred_direction}，實際走勢確實如此。"
            reflection += f"這證明我對市場情緒的解讀是準確的。\n\n"
        else:
            reflection += f"❌ **方向判斷錯誤**：我原本預測{pred_direction}，但實際走勢相反。"
            reflection += f"我需要重新檢視當時的判斷邏輯。\n\n"
        
        # 價格分析
        error = accuracy["price_error"]
        error_pct = accuracy["price_error_percent"]
        if error_pct < 1.0:
            reflection += f"✅ **價格預測精準**：誤差僅 {error} 點（{error_pct}%），"
            reflection += f"我對價格區間的掌握相當好。\n\n"
        elif error_pct < 2.0:
            reflection += f"⚠️ **價格略有偏差**：誤差 {error} 點（{error_pct}%），"
            reflection += f"還算在可接受範圍內。\n\n"
        else:
            reflection += f"❌ **價格偏離較大**：誤差 {error} 點（{error_pct}%），"
            reflection += f"我需要改進價格預測的方法。\n\n"
        
        # 策略回顧
        reflection += "**策略執行回顧**：\n"
        strategy = prediction["strategy_recommendation"]
        if accuracy["direction_correct"]:
            reflection += f"如果按照我建議的「{strategy['primary']}」策略執行，"
            reflection += f"應該能夠獲利。這個策略在當時的市況下是正確的選擇。"
        else:
            reflection += f"我建議的「{strategy['primary']}」策略在今天可能會虧損。"
            reflection += f"下次遇到類似情況，我應該更謹慎或選擇其他策略。"
        
        return reflection
    
    def _extract_lessons(self, prediction: Dict, actual_data, 
                        accuracy: Dict) -> list:
        """提取學到的教訓"""
        lessons = []
        
        pred_pc = prediction["current_metrics"]["pc_ratio"]
        
        # 計算實際的 PC Ratio
        total_call_oi = sum(actual_data.call_oi) if actual_data.call_oi else 1
        total_put_oi = sum(actual_data.put_oi) if actual_data.put_oi else 1
        actual_pc = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0
        
        # PC Ratio 相關教訓
        if not accuracy["direction_correct"]:
            if pred_pc > 1.2:
                lessons.append(
                    f"當 PC Ratio 高達 {pred_pc:.2f} 時，不一定會反彈，"
                    f"還需要考慮其他因素如成交量和技術面。"
                )
            elif pred_pc < 0.8:
                lessons.append(
                    f"PC Ratio 低於 {pred_pc:.2f} 時的樂觀情緒，"
                    f"不見得會立即導致回檔，多頭動能可能持續。"
                )
        
        # 價格波動相關教訓
        if not accuracy["in_predicted_range"]:
            lessons.append(
                f"今天的波動超出預期區間，說明我低估了市場的波動性。"
                f"下次應該設定更寬的安全邊際。"
            )
        
        # 信心水準相關教訓
        confidence = prediction["confidence_level"]
        if confidence > 70 and accuracy["overall_accuracy"] < 50:
            lessons.append(
                f"我當時的信心水準為 {confidence}%，但實際準確度很低。"
                f"這提醒我要保持謙虛，避免過度自信。"
            )
        
        # 如果沒有特別教訓，加入通用反思
        if not lessons:
            if accuracy["overall_accuracy"] >= 80:
                lessons.append("這次預測成功，我應該記住這次分析的邏輯和方法。")
            else:
                lessons.append("每一次預測都是學習機會，無論對錯都能累積經驗。")
        
        return lessons
    
    def _identify_improvements(self, accuracy: Dict) -> list:
        """識別需要改進的領域"""
        improvements = []
        
        if not accuracy["direction_correct"]:
            improvements.append("📈 改進方向判斷邏輯，加入更多技術指標")
        
        if accuracy["price_error_percent"] > 2.0:
            improvements.append("📊 提升價格預測精度，參考歷史波動率")
        
        if not accuracy["in_predicted_range"]:
            improvements.append("📉 擴大預測區間範圍，增加安全邊際")
        
        if accuracy["overall_accuracy"] < 60:
            improvements.append("🎯 整體預測能力需要加強，多研究市場規律")
        
        # 如果表現很好，給予正面鼓勵
        if not improvements:
            improvements.append("✨ 繼續保持目前的分析水準，累積更多成功經驗")
        
        return improvements
    
    def _calculate_score(self, accuracy: Dict) -> str:
        """計算評分等級"""
        score = accuracy["overall_accuracy"]
        
        if score >= 90:
            return "🏆 優秀 (A+)"
        elif score >= 80:
            return "🥇 良好 (A)"
        elif score >= 70:
            return "🥈 中上 (B+)"
        elif score >= 60:
            return "🥉 中等 (B)"
        elif score >= 50:
            return "📝 及格 (C)"
        else:
            return "⚠️ 需改進 (D)"
    
    def _save_review(self, review: Dict):
        """儲存檢討報告"""
        filename = f"review_{review['prediction_date']}.json"
        filepath = self.reviews_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(review, f, ensure_ascii=False, indent=2)
    
    def _update_learning_system(self, review: Dict):
        """更新學習系統"""
        # 記錄這次預測的結果
        record_data = {
            "date": review["actual_date"],
            "prediction_accuracy": review["accuracy"]["overall_accuracy"],
            "direction_correct": review["accuracy"]["direction_correct"],
            "price_error": review["accuracy"]["price_error"],
            "lessons": review["lessons_learned"],
        }
        
        # 這裡可以將記錄加入到學習系統
        # 目前先儲存到檔案，之後可以擴充
        insights_file = Path("data/ai_learning/learned_insights.json")
        
        if insights_file.exists():
            with open(insights_file, 'r', encoding='utf-8') as f:
                insights = json.load(f)
        else:
            insights = {}
        
        # 確保 reviews 鍵存在
        if "reviews" not in insights:
            insights["reviews"] = []
        
        insights["reviews"].append(record_data)
        
        with open(insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)
    
    def load_review(self, date: str) -> Optional[Dict]:
        """載入指定日期的檢討"""
        filename = f"review_{date}.json"
        filepath = self.reviews_dir / filename
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
