"""
AI 學習系統
累積並學習歷史分析記錄，持續改進分析品質
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class AnalysisRecord:
    """分析記錄"""
    date: str  # YYYYMMDD
    close_price: float
    pc_ratio: float
    sentiment: str
    trend_signal: str  # 'bullish', 'bearish', 'neutral'
    
    # AI 分析內容
    market_observation: str
    position_strategy: str
    risk_assessment: str
    trading_plan: str
    
    # 後續驗證（可選）
    next_day_price: Optional[float] = None
    prediction_accuracy: Optional[str] = None  # 'correct', 'partially_correct', 'incorrect'
    lessons_learned: Optional[str] = None


class AILearningSystem:
    """AI 學習系統 - 從歷史分析中學習並改進"""

    def __init__(self, data_dir: str = 'data/ai_learning'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.records_file = self.data_dir / 'analysis_records.json'
        self.insights_file = self.data_dir / 'learned_insights.json'
        self.reference_dir = self.data_dir / 'reference_analysis'
        self.reviews_dir = self.data_dir / 'settlement_reviews'
        self.reference_dir.mkdir(parents=True, exist_ok=True)

        self.records: List[AnalysisRecord] = []
        self.insights: Dict = {}
        self.reference_analyses: List[Dict] = []
        self.settlement_reviews: List[Dict] = []

        self._load_data()
        self._load_reference_analyses()
        self._load_settlement_reviews()
    
    def _load_settlement_reviews(self):
        """載入所有結算審核記錄，建立真實績效統計"""
        self.settlement_reviews = []
        if not self.reviews_dir.exists():
            return
        for f in sorted(self.reviews_dir.glob("settlement_review_*.json")):
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
                self.settlement_reviews.append(data)
            except Exception:
                pass

        # 更新 insights 中的結算審核統計
        self._update_settlement_insights()

    def _update_settlement_insights(self):
        """將結算審核結果寫入 insights，讓外部可查詢績效"""
        if not self.settlement_reviews:
            return

        stats: Dict[str, Dict] = {}
        for r in self.settlement_reviews:
            wday = r.get("weekday", "unknown")
            acc = r.get("accuracy", {})
            if wday not in stats:
                stats[wday] = {
                    "count": 0,
                    "direction_correct": 0,
                    "in_range": 0,
                    "total_accuracy": 0.0,
                    "lessons": [],
                }
            stats[wday]["count"] += 1
            if acc.get("direction_correct"):
                stats[wday]["direction_correct"] += 1
            if acc.get("in_predicted_range"):
                stats[wday]["in_range"] += 1
            stats[wday]["total_accuracy"] += acc.get("overall_accuracy", 0)
            for lesson in r.get("lessons_learned", []):
                if lesson and lesson not in stats[wday]["lessons"]:
                    stats[wday]["lessons"].append(lesson)

        # 計算比率
        for wday, s in stats.items():
            n = s["count"]
            s["direction_accuracy_pct"] = round(s["direction_correct"] / n * 100, 1) if n else 0
            s["interval_hit_rate_pct"] = round(s["in_range"] / n * 100, 1) if n else 0
            s["avg_accuracy"] = round(s["total_accuracy"] / n, 1) if n else 0

        self.insights["settlement_performance"] = stats
        self._save_data()

    def get_settlement_performance_summary(self) -> str:
        """生成結算預測績效摘要（供 AI prompt 使用）"""
        perf = self.insights.get("settlement_performance", {})
        if not perf:
            return "尚無結算審核記錄"

        lines = ["📊 結算預測歷史績效："]
        for wday, s in perf.items():
            wday_zh = "週三" if wday == "wednesday" else "週五"
            lines.append(
                f"  {wday_zh}：{s['count']}次 | 方向準確={s['direction_accuracy_pct']}%"
                f" | 區間命中={s['interval_hit_rate_pct']}% | 平均得分={s['avg_accuracy']}%"
            )

            # 加入最近的教訓（最多 3 條）
            if s.get("lessons"):
                lines.append("  近期教訓：")
                for lesson in s["lessons"][-3:]:
                    lines.append(f"    • {lesson}")

        return "\n".join(lines)

    def _load_data(self):
        """載入歷史資料"""
        # 載入分析記錄
        if self.records_file.exists():
            with open(self.records_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.records = [AnalysisRecord(**record) for record in data]
        
        # 載入學習洞察
        if self.insights_file.exists():
            with open(self.insights_file, 'r', encoding='utf-8') as f:
                self.insights = json.load(f)

    def _load_reference_analyses(self):
        """載入參考分析資料（外部專家分析）"""
        self.reference_analyses = []
        for json_file in self.reference_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_filename'] = json_file.name
                    self.reference_analyses.append(data)
            except Exception as e:
                print(f"載入參考分析失敗: {json_file.name} - {e}")

        # 按日期排序
        self.reference_analyses.sort(
            key=lambda x: x.get('target_settlement_date', ''),
            reverse=True
        )

    def get_reference_methodology(self) -> Dict:
        """獲取參考分析方法論"""
        if not self.reference_analyses:
            return {}

        # 彙整所有參考分析的方法論
        all_steps = []
        all_factors = []

        for ref in self.reference_analyses:
            methodology = ref.get('analysis_methodology', {})
            steps = methodology.get('steps', [])
            factors = methodology.get('key_factors', [])

            for step in steps:
                if step not in all_steps:
                    all_steps.append(step)

            for factor in factors:
                if factor not in all_factors:
                    all_factors.append(factor)

        return {
            'analysis_steps': all_steps,
            'key_factors': all_factors,
            'reference_count': len(self.reference_analyses)
        }

    def get_reference_for_settlement(self, settlement_type: str = None) -> List[Dict]:
        """獲取結算日相關的參考分析"""
        results = []
        for ref in self.reference_analyses:
            if settlement_type:
                if settlement_type.lower() in ref.get('settlement_type', '').lower():
                    results.append(ref)
            else:
                results.append(ref)
        return results

    def get_settlement_analysis_template(self) -> Dict:
        """從參考分析中提取結算分析模板"""
        if not self.reference_analyses:
            return {}

        # 使用最新的參考分析作為模板
        latest = self.reference_analyses[0] if self.reference_analyses else {}

        return {
            'analysis_dimensions': [
                'market_data',           # 市場現況數據
                'pc_ratio_analysis',     # P/C Ratio 分析
                'oi_analysis',           # 未平倉量分析
                'iv_analysis',           # 隱含波動率分析
                'settlement_prediction', # 結算預測
                'observation_points'     # 觀察重點
            ],
            'oi_analysis_structure': {
                'resistance_zone': '壓力區分析（Call OI 牆）',
                'support_zone': '支撐區分析（Put OI 牆）',
                'key_changes': '重要履約價的 OI 變化'
            },
            'prediction_structure': {
                'initial_range': '初步預測區間',
                'revised_range': '修正後區間（考慮 IV 等因素）',
                'optimal_settlement_for_mm': '莊家最佳收割區間',
                'scenarios': '多空情境分析'
            },
            'reference_source': latest.get('source', 'Unknown')
        }

    def _save_data(self):
        """儲存資料"""
        # 儲存分析記錄
        with open(self.records_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(r) for r in self.records], f, ensure_ascii=False, indent=2)
        
        # 儲存學習洞察
        with open(self.insights_file, 'w', encoding='utf-8') as f:
            json.dump(self.insights, f, ensure_ascii=False, indent=2)
    
    def add_record(self, record: AnalysisRecord):
        """新增分析記錄"""
        self.records.append(record)
        self._save_data()
        self._update_insights()
    
    def _update_insights(self):
        """更新學習洞察"""
        if len(self.records) < 5:
            return  # 至少需要 5 筆記錄才能開始學習
        
        # 分析 PC Ratio 與市場走勢的關係
        self._analyze_pc_ratio_patterns()
        
        # 分析成功預測的共同特徵
        self._analyze_successful_predictions()
        
        # 分析不同市場情境的表現
        self._analyze_market_scenarios()
        
        self._save_data()
    
    def _analyze_pc_ratio_patterns(self):
        """分析 PC Ratio 模式"""
        patterns = {
            'extremely_low': [],  # < 0.7
            'low': [],            # 0.7 - 0.9
            'neutral': [],        # 0.9 - 1.1
            'high': [],           # 1.1 - 1.3
            'extremely_high': []  # > 1.3
        }
        
        for record in self.records:
            if record.next_day_price is None:
                continue
            
            price_change = record.next_day_price - record.close_price
            change_pct = (price_change / record.close_price) * 100
            
            pc = record.pc_ratio
            if pc < 0.7:
                patterns['extremely_low'].append(change_pct)
            elif pc < 0.9:
                patterns['low'].append(change_pct)
            elif pc < 1.1:
                patterns['neutral'].append(change_pct)
            elif pc < 1.3:
                patterns['high'].append(change_pct)
            else:
                patterns['extremely_high'].append(change_pct)
        
        # 計算平均變化
        self.insights['pc_ratio_patterns'] = {}
        for level, changes in patterns.items():
            if changes:
                avg_change = sum(changes) / len(changes)
                self.insights['pc_ratio_patterns'][level] = {
                    'avg_change_pct': round(avg_change, 2),
                    'sample_size': len(changes),
                    'interpretation': self._interpret_pc_pattern(level, avg_change)
                }
    
    def _interpret_pc_pattern(self, level: str, avg_change: float) -> str:
        """解讀 PC Ratio 模式"""
        if level == 'extremely_low':
            if avg_change > 0:
                return "極低 PC Ratio 通常伴隨上漲，市場過度樂觀需警惕反轉"
            else:
                return "極低 PC Ratio 反而下跌，可能是多頭陷阱"
        elif level == 'extremely_high':
            if avg_change < 0:
                return "極高 PC Ratio 通常伴隨下跌，市場過度悲觀需注意反彈"
            else:
                return "極高 PC Ratio 反而上漲，可能是空頭陷阱"
        return "中性區間，需搭配其他指標判斷"
    
    def _analyze_successful_predictions(self):
        """分析成功預測的共同特徵"""
        successful = [r for r in self.records if r.prediction_accuracy == 'correct']
        
        if len(successful) >= 3:
            self.insights['success_factors'] = {
                'total_predictions': len([r for r in self.records if r.prediction_accuracy]),
                'successful_count': len(successful),
                'success_rate': round(len(successful) / len([r for r in self.records if r.prediction_accuracy]) * 100, 1),
                'common_traits': self._extract_common_traits(successful)
            }
    
    def _extract_common_traits(self, records: List[AnalysisRecord]) -> List[str]:
        """提取成功預測的共同特徵"""
        traits = []
        
        # 分析情緒分布
        sentiments = [r.sentiment for r in records]
        if sentiments.count('neutral') / len(sentiments) > 0.5:
            traits.append("中性市場較容易預測")
        
        # 分析趨勢信號
        trends = [r.trend_signal for r in records]
        if len(set(trends)) == 1:
            traits.append(f"單一方向趨勢 ({trends[0]}) 較為明確")
        
        return traits
    
    def _analyze_market_scenarios(self):
        """分析不同市場情境"""
        scenarios = {}
        
        for record in self.records:
            key = f"{record.sentiment}_{record.trend_signal}"
            if key not in scenarios:
                scenarios[key] = {
                    'count': 0,
                    'successful': 0,
                    'observations': []
                }
            
            scenarios[key]['count'] += 1
            if record.prediction_accuracy == 'correct':
                scenarios[key]['successful'] += 1
            
            if record.lessons_learned:
                scenarios[key]['observations'].append(record.lessons_learned)
        
        self.insights['market_scenarios'] = scenarios
    
    def get_historical_context(self, current_pc_ratio: float, current_sentiment: str) -> Dict:
        """獲取歷史背景資訊，幫助當前分析"""
        context = {
            'similar_situations': [],
            'learned_insights': [],
            'risk_warnings': []
        }
        
        # 尋找相似情況
        for record in self.records[-20:]:  # 最近 20 筆
            if abs(record.pc_ratio - current_pc_ratio) < 0.1:
                context['similar_situations'].append({
                    'date': record.date,
                    'pc_ratio': record.pc_ratio,
                    'outcome': record.prediction_accuracy or '未驗證',
                    'lesson': record.lessons_learned or '無'
                })
        
        # 加入學習洞察
        if 'pc_ratio_patterns' in self.insights:
            for level, data in self.insights['pc_ratio_patterns'].items():
                if self._is_pc_in_range(current_pc_ratio, level):
                    context['learned_insights'].append(data['interpretation'])
        
        # 風險警告
        if current_sentiment in ['extremely_bullish', 'extremely_bearish']:
            context['risk_warnings'].append("極端情緒可能導致反轉，需謹慎")
        
        return context
    
    def _is_pc_in_range(self, pc_ratio: float, level: str) -> bool:
        """判斷 PC Ratio 是否在特定範圍"""
        if level == 'extremely_low':
            return pc_ratio < 0.7
        elif level == 'low':
            return 0.7 <= pc_ratio < 0.9
        elif level == 'neutral':
            return 0.9 <= pc_ratio < 1.1
        elif level == 'high':
            return 1.1 <= pc_ratio < 1.3
        elif level == 'extremely_high':
            return pc_ratio >= 1.3
        return False
    
    def generate_learning_summary(self) -> str:
        """生成學習摘要"""
        summary_parts = []

        # 分析記錄統計
        if len(self.records) >= 5:
            summary_parts.append(f"📚 已累積 {len(self.records)} 筆分析記錄")

            if 'success_factors' in self.insights:
                sf = self.insights['success_factors']
                summary_parts.append(f"🎯 預測成功率: {sf['success_rate']}% ({sf['successful_count']}/{sf['total_predictions']})")

            if 'pc_ratio_patterns' in self.insights:
                summary_parts.append(f"📊 已建立 {len(self.insights['pc_ratio_patterns'])} 種 PC Ratio 模式分析")
        else:
            summary_parts.append(f"📚 分析記錄: {len(self.records)} 筆（持續累積中）")

        # 參考分析統計
        if self.reference_analyses:
            summary_parts.append(f"📖 參考分析: {len(self.reference_analyses)} 份外部專家分析")
            methodology = self.get_reference_methodology()
            if methodology.get('key_factors'):
                summary_parts.append(f"🔍 已學習 {len(methodology['key_factors'])} 個關鍵分析因子")

        return "\n".join(summary_parts)
    
    def get_experience_level(self) -> tuple[str, str]:
        """獲取經驗等級"""
        count = len(self.records)
        
        if count < 10:
            return "新手", "🌱"
        elif count < 30:
            return "學習中", "📈"
        elif count < 50:
            return "進階", "🎓"
        elif count < 100:
            return "專家", "⭐"
        else:
            return "大師", "👑"
