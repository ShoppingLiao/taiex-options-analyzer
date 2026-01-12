"""
AI 結算日檢討分析器
比較預測與實際結算結果，生成檢討報告
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

class AISettlementReview:
    """AI 結算日檢討分析器"""
    
    def __init__(self, learning_system, prediction_generator):
        self.learning_system = learning_system
        self.prediction_generator = prediction_generator
        self.reviews_dir = Path("data/ai_learning/settlement_reviews")
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_settlement_review(
        self,
        settlement_date: str,  # YYYYMMDD
        actual_settlement_price: int,
        actual_data: Dict  # 結算日的實際數據
    ) -> Dict[str, Any]:
        """
        生成結算日檢討報告
        
        Args:
            settlement_date: 結算日期
            actual_settlement_price: 實際結算價
            actual_data: 結算日實際數據
            
        Returns:
            檢討報告字典
        """
        
        # 載入預測
        prediction = self.prediction_generator.load_prediction(settlement_date)
        
        if not prediction:
            return {
                "error": f"找不到 {settlement_date} 的結算預測記錄",
                "settlement_date": settlement_date
            }
        
        # 計算準確度
        accuracy = self._calculate_settlement_accuracy(
            prediction,
            actual_settlement_price,
            actual_data
        )
        
        # 生成檢討內容
        review = {
            "settlement_date": settlement_date,
            "weekday": prediction["settlement_weekday"],
            "prediction": prediction,
            "actual_result": {
                "settlement_price": actual_settlement_price,
                "tx_close": actual_data.get("tx_close", actual_settlement_price),
                "pc_ratio": actual_data.get("pc_ratio", 0),
                "call_oi": actual_data.get("call_oi", 0),
                "put_oi": actual_data.get("put_oi", 0),
            },
            "accuracy": accuracy,
            "self_reflection": self._generate_settlement_reflection(
                prediction, 
                actual_settlement_price, 
                actual_data,
                accuracy
            ),
            "lessons_learned": self._extract_settlement_lessons(
                prediction,
                actual_settlement_price,
                accuracy
            ),
            "improvement_areas": self._identify_settlement_improvements(accuracy),
            "score": self._calculate_settlement_score(accuracy),
            "review_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 儲存檢討
        self._save_review(review)
        
        # 更新學習系統
        self._update_learning_system(review)
        
        return review
    
    def _calculate_settlement_accuracy(
        self,
        prediction: Dict,
        actual_price: int,
        actual_data: Dict
    ) -> Dict[str, Any]:
        """計算結算預測準確度"""
        
        predicted_price = prediction["settlement_price_prediction"]["predicted_price"]
        upper_bound = prediction["settlement_price_prediction"]["upper_bound"]
        lower_bound = prediction["settlement_price_prediction"]["lower_bound"]
        
        # 價格誤差
        price_error = abs(actual_price - predicted_price)
        price_error_pct = (price_error / predicted_price * 100) if predicted_price > 0 else 100
        
        # 是否在預測區間內
        in_range = lower_bound <= actual_price <= upper_bound
        
        # 方向正確性（如果有趨勢預測）
        trend_analysis = prediction.get("trend_analysis", {})
        predicted_trend = trend_analysis.get("trend_direction", "")
        
        # 根據趨勢判斷方向
        predicted_change = prediction["settlement_price_prediction"]["expected_change"]
        actual_change = actual_price - prediction["settlement_price_prediction"]["base_price"]
        
        direction_correct = False
        if abs(predicted_change) < 50 and abs(actual_change) < 50:
            # 都預測盤整
            direction_correct = True
        elif predicted_change > 0 and actual_change > 0:
            # 都是上漲
            direction_correct = True
        elif predicted_change < 0 and actual_change < 0:
            # 都是下跌
            direction_correct = True
        
        # 總體準確度
        overall_accuracy = self._calculate_overall_settlement_accuracy(
            in_range,
            direction_correct,
            price_error_pct
        )
        
        return {
            "price_error": price_error,
            "price_error_percent": round(price_error_pct, 2),
            "in_predicted_range": in_range,
            "direction_correct": direction_correct,
            "predicted_price": predicted_price,
            "actual_price": actual_price,
            "predicted_range": f"{lower_bound:,} - {upper_bound:,}",
            "overall_accuracy": overall_accuracy
        }
    
    def _calculate_overall_settlement_accuracy(
        self,
        in_range: bool,
        direction_correct: bool,
        price_error_pct: float
    ) -> int:
        """計算總體準確度 (0-100)"""
        score = 0
        
        # 在預測區間內 +50 分
        if in_range:
            score += 50
        
        # 方向正確 +25 分
        if direction_correct:
            score += 25
        
        # 價格誤差 (最多 +25 分)
        if price_error_pct < 0.5:
            score += 25
        elif price_error_pct < 1.0:
            score += 20
        elif price_error_pct < 1.5:
            score += 15
        elif price_error_pct < 2.0:
            score += 10
        elif price_error_pct < 3.0:
            score += 5
        
        return min(score, 100)
    
    def _generate_settlement_reflection(
        self,
        prediction: Dict,
        actual_price: int,
        actual_data: Dict,
        accuracy: Dict
    ) -> str:
        """生成結算日第一人稱反思"""
        
        weekday_zh = "週三" if prediction["settlement_weekday"] == "wednesday" else "週五"
        
        reflection = f"📝 **{weekday_zh}結算檢討**\n\n"
        
        # 整體表現
        overall = accuracy["overall_accuracy"]
        if overall >= 80:
            reflection += "這次結算預測相當準確，我很滿意！"
        elif overall >= 60:
            reflection += "結算預測基本符合預期，表現還不錯。"
        elif overall >= 40:
            reflection += "結算預測有些偏差，需要檢討。"
        else:
            reflection += "這次結算預測失誤較大，我要好好反省。"
        
        reflection += f"（準確度：{overall}%）\n\n"
        
        # 價格準確性
        predicted = accuracy["predicted_price"]
        actual = accuracy["actual_price"]
        error = accuracy["price_error"]
        error_pct = accuracy["price_error_percent"]
        
        reflection += f"**預測結算價**：{predicted:,} 點\n"
        reflection += f"**實際結算價**：{actual:,} 點\n"
        reflection += f"**價格誤差**：{error} 點 ({error_pct}%)\n\n"
        
        # 區間判斷
        if accuracy["in_predicted_range"]:
            reflection += f"✅ **區間預測正確**：結算價 {actual:,} 確實落在我預測的區間 {accuracy['predicted_range']} 內。"
            reflection += f"這證明我對市場波動幅度的判斷是準確的。\n\n"
        else:
            reflection += f"❌ **超出預測區間**：結算價 {actual:,} 跳出了我的預測區間 {accuracy['predicted_range']}。"
            reflection += f"我低估了結算日的波動性。\n\n"
        
        # 方向判斷
        if accuracy["direction_correct"]:
            reflection += "✅ **方向判斷正確**：結算走勢與我的預期一致。\n\n"
        else:
            reflection += "❌ **方向判斷錯誤**：結算走勢與我的預期相反，需要重新思考趨勢判斷邏輯。\n\n"
        
        # 策略回顧
        reflection += "**策略執行回顧**：\n"
        if overall >= 70:
            reflection += f"按照我的{weekday_zh}結算策略執行，應該能夠獲得不錯的收益。"
        elif overall >= 50:
            reflection += f"部分策略有效，但仍有改進空間。"
        else:
            reflection += f"這次的策略判斷有明顯失誤，下次需要更謹慎。"
        
        return reflection
    
    def _extract_settlement_lessons(
        self,
        prediction: Dict,
        actual_price: int,
        accuracy: Dict
    ) -> list:
        """提取結算日學到的教訓"""
        
        lessons = []
        
        weekday = prediction["settlement_weekday"]
        weekday_zh = "週三" if weekday == "wednesday" else "週五"
        
        # 區間預測相關
        if not accuracy["in_predicted_range"]:
            error_pct = accuracy["price_error_percent"]
            lessons.append(
                f"{weekday_zh}結算的波動幅度超出預期 {error_pct:.1f}%，"
                f"下次應該設定更寬的預測區間。"
            )
        
        # 方向預測相關
        if not accuracy["direction_correct"]:
            trend = prediction.get("trend_analysis", {}).get("trend_direction", "")
            lessons.append(
                f"結算前的{trend}趨勢並未延續到結算日，"
                f"說明結算日有其特殊性，不能單純延續前期走勢。"
            )
        
        # 準確度相關
        if accuracy["overall_accuracy"] >= 80:
            lessons.append(
                f"這次{weekday_zh}結算預測成功的經驗值得記錄，"
                f"類似的市場條件下可以參考這次的分析方法。"
            )
        elif accuracy["overall_accuracy"] < 50:
            lessons.append(
                f"{weekday_zh}結算的複雜度高於一般交易日，"
                f"需要考慮更多因素，如大戶動向、期現套利等。"
            )
        
        # 如果沒有特別教訓，加入通用反思
        if not lessons:
            lessons.append(
                f"每次{weekday_zh}結算都是學習機會，"
                f"持續累積經驗才能提升預測準確度。"
            )
        
        return lessons
    
    def _identify_settlement_improvements(self, accuracy: Dict) -> list:
        """識別需要改進的領域"""
        
        improvements = []
        
        if not accuracy["in_predicted_range"]:
            improvements.append("📊 改進波動率預測模型，更準確估計結算日波動幅度")
        
        if not accuracy["direction_correct"]:
            improvements.append("📈 加強趨勢延續性分析，區分結算日與一般交易日")
        
        if accuracy["price_error_percent"] > 2.0:
            improvements.append("🎯 提升結算價預測精度，參考歷史結算數據")
        
        if accuracy["overall_accuracy"] < 60:
            improvements.append("💡 整體預測能力需要加強，多觀察結算日的特殊規律")
        
        # 如果表現很好，給予鼓勵
        if not improvements or accuracy["overall_accuracy"] >= 80:
            improvements.append("✨ 繼續保持這個水準，累積更多結算日預測經驗")
        
        return improvements
    
    def _calculate_settlement_score(self, accuracy: Dict) -> str:
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
        filename = f"settlement_review_{review['settlement_date']}.json"
        filepath = self.reviews_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(review, f, ensure_ascii=False, indent=2)
    
    def _update_learning_system(self, review: Dict):
        """更新學習系統"""
        # 記錄這次結算預測的結果
        record_data = {
            "date": review["settlement_date"],
            "type": "settlement",
            "weekday": review["weekday"],
            "prediction_accuracy": review["accuracy"]["overall_accuracy"],
            "in_range": review["accuracy"]["in_predicted_range"],
            "direction_correct": review["accuracy"]["direction_correct"],
            "price_error": review["accuracy"]["price_error"],
            "lessons": review["lessons_learned"],
        }
        
        # 加入學習記錄
        insights_file = Path("data/ai_learning/learned_insights.json")
        
        if insights_file.exists():
            with open(insights_file, 'r', encoding='utf-8') as f:
                insights = json.load(f)
        else:
            insights = {}
        
        # 確保 settlement_reviews 鍵存在
        if "settlement_reviews" not in insights:
            insights["settlement_reviews"] = []
        
        insights["settlement_reviews"].append(record_data)
        
        with open(insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)
    
    def load_review(self, settlement_date: str) -> Optional[Dict]:
        """載入指定日期的結算檢討"""
        filename = f"settlement_review_{settlement_date}.json"
        filepath = self.reviews_dir / filename
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
