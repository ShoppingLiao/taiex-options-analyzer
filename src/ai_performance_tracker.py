"""
AI 預測績效追蹤器
收集所有歷史預測檢討，生成績效統計和趨勢圖數據
"""

from pathlib import Path
import json
from typing import List, Dict, Any
from datetime import datetime


class AIPerformanceTracker:
    """AI 預測績效追蹤器"""
    
    def __init__(self):
        self.reviews_dir = Path("data/ai_learning/settlement_reviews")
        
    def collect_all_reviews(self) -> List[Dict[str, Any]]:
        """收集所有結算檢討記錄"""
        reviews = []
        
        if not self.reviews_dir.exists():
            return reviews
        
        # 遍歷所有檢討檔案
        for review_file in sorted(self.reviews_dir.glob("settlement_review_*.json")):
            try:
                with open(review_file, 'r', encoding='utf-8') as f:
                    review_data = json.load(f)
                    reviews.append(review_data)
            except Exception as e:
                print(f"⚠️  無法載入 {review_file}: {e}")
                
        return reviews
    
    def calculate_statistics(self, reviews: List[Dict]) -> Dict[str, Any]:
        """計算統計數據"""
        if not reviews:
            return {
                "total_predictions": 0,
                "avg_accuracy": 0,
                "avg_price_error": 0,
                "range_success_rate": 0,
                "direction_success_rate": 0,
                "grade_distribution": {}
            }
        
        total = len(reviews)
        total_accuracy = 0
        total_price_error = 0
        range_success = 0
        direction_success = 0
        grade_counts = {}
        
        for review in reviews:
            accuracy = review.get('accuracy', {})
            
            # 累加準確度
            total_accuracy += accuracy.get('overall_accuracy', 0)
            
            # 累加價格誤差
            total_price_error += accuracy.get('price_error', 0)
            
            # 統計區間預測成功率
            if accuracy.get('in_predicted_range'):
                range_success += 1
            
            # 統計方向預測成功率
            if accuracy.get('direction_correct'):
                direction_success += 1
            
            # 統計評分分佈
            score = review.get('score', 'Unknown')
            # 提取等級（例如從 "🏆 優秀 (A+)" 提取 "A+"）
            if '(' in score and ')' in score:
                grade = score.split('(')[1].split(')')[0]
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        return {
            "total_predictions": total,
            "avg_accuracy": round(total_accuracy / total, 2),
            "avg_price_error": round(total_price_error / total, 2),
            "range_success_rate": round((range_success / total) * 100, 2),
            "direction_success_rate": round((direction_success / total) * 100, 2),
            "grade_distribution": grade_counts
        }
    
    def generate_trend_data(self, reviews: List[Dict]) -> List[Dict]:
        """生成趨勢圖數據"""
        trend_data = []
        
        for review in reviews:
            settlement_date = review.get('settlement_date', '')
            accuracy = review.get('accuracy', {})
            
            # 格式化日期
            try:
                date_obj = datetime.strptime(settlement_date, '%Y%m%d')
                formatted_date = date_obj.strftime('%m/%d')
                weekday = review.get('weekday', '').replace('wednesday', '三').replace('friday', '五')
            except:
                formatted_date = settlement_date
                weekday = ''
            
            trend_data.append({
                "date": settlement_date,
                "formatted_date": f"{formatted_date}({weekday})",
                "overall_accuracy": accuracy.get('overall_accuracy', 0),
                "price_error": accuracy.get('price_error', 0),
                "predicted_price": accuracy.get('predicted_price', 0),
                "actual_price": accuracy.get('actual_price', 0),
                "in_range": accuracy.get('in_predicted_range', False),
                "direction_correct": accuracy.get('direction_correct', False)
            })
        
        return trend_data
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """獲取績效總覽"""
        reviews = self.collect_all_reviews()
        statistics = self.calculate_statistics(reviews)
        trend_data = self.generate_trend_data(reviews)
        
        return {
            "statistics": statistics,
            "trend_data": trend_data,
            "latest_review": reviews[-1] if reviews else None,
            "best_prediction": self._find_best_prediction(reviews),
            "total_experience": len(reviews)
        }
    
    def _find_best_prediction(self, reviews: List[Dict]) -> Dict[str, Any]:
        """找出最佳預測"""
        if not reviews:
            return None
        
        best = min(reviews, key=lambda r: r.get('accuracy', {}).get('price_error', float('inf')))
        
        return {
            "date": best.get('settlement_date'),
            "price_error": best.get('accuracy', {}).get('price_error', 0),
            "accuracy": best.get('accuracy', {}).get('overall_accuracy', 0),
            "score": best.get('score', '')
        }
    
    def export_to_json(self, output_path: str = None) -> str:
        """匯出績效數據為 JSON"""
        if output_path is None:
            output_path = "data/ai_learning/performance_summary.json"
        
        summary = self.get_performance_summary()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return str(output_file)


if __name__ == '__main__':
    tracker = AIPerformanceTracker()
    summary = tracker.get_performance_summary()
    
    print("\n" + "=" * 60)
    print("📊 AI 預測績效總覽")
    print("=" * 60)
    
    stats = summary['statistics']
    print(f"\n📈 統計數據:")
    print(f"  總預測次數: {stats['total_predictions']}")
    print(f"  平均準確度: {stats['avg_accuracy']}%")
    print(f"  平均誤差: {stats['avg_price_error']:.2f} 點")
    print(f"  區間命中率: {stats['range_success_rate']}%")
    print(f"  方向正確率: {stats['direction_success_rate']}%")
    
    if stats['grade_distribution']:
        print(f"\n🏆 評分分佈:")
        for grade, count in sorted(stats['grade_distribution'].items()):
            print(f"  {grade}: {count} 次")
    
    if summary['best_prediction']:
        best = summary['best_prediction']
        print(f"\n⭐ 最佳預測:")
        print(f"  日期: {best['date']}")
        print(f"  誤差: {best['price_error']} 點")
        print(f"  準確度: {best['accuracy']}%")
        print(f"  評分: {best['score']}")
    
    # 匯出 JSON
    output_file = tracker.export_to_json()
    print(f"\n✅ 績效數據已匯出: {output_file}")
