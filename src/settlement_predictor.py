"""
結算日預測分析模組
透過週一二或週三四的數據預測週三或週五的結算區間
著重於趨勢分析和劇本情境
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
import re


@dataclass
class TrendSignal:
    """趨勢訊號"""
    direction: str  # 'bullish', 'bearish', 'neutral'
    strength: int  # 1-5 強度
    indicators: List[str]  # 訊號來源
    description: str  # 說明


@dataclass
class Scenario:
    """結算劇本"""
    name: str  # 劇本名稱
    probability: float  # 機率 (0-100)
    price_range: Tuple[int, int]  # 結算區間
    key_levels: List[int]  # 關鍵價位
    conditions: List[str]  # 成立條件
    strategy: str  # 操作建議
    color: str  # 顯示顏色
    icon: str  # 圖示


@dataclass
class SettlementPrediction:
    """結算日預測結果"""
    settlement_date: str  # 結算日期
    settlement_weekday: str  # 週三或週五
    analysis_dates: List[str]  # 分析數據日期
    current_price: int  # 當前價格
    
    # 趨勢分析
    trend_signals: List[TrendSignal]
    overall_trend: str  # 整體趨勢 direction
    overall_trend_text: str  # 趨勢文字描述
    trend_strength: int  # 趨勢強度 1-5
    
    # 結算預測
    predicted_range: Tuple[int, int]  # 主要預測區間
    scenarios: List[Scenario]  # 可能劇本
    
    # 關鍵數據
    key_metrics: Dict[str, any]  # 關鍵指標
    
    # 風險提示
    risks: List[str]


class SettlementPredictor:
    """結算日預測器"""
    
    def __init__(self):
        self.reports_dir = Path('reports')
        
    def predict_settlement(
        self, 
        dates: List[str], 
        settlement_date: str,
        settlement_weekday: str  # 'wednesday' or 'friday'
    ) -> SettlementPrediction:
        """
        預測結算日
        
        Args:
            dates: 分析數據日期列表 (YYYYMMDD格式)
            settlement_date: 結算日期 (YYYY/MM/DD格式)
            settlement_weekday: 結算星期 ('wednesday' or 'friday')
            
        Returns:
            SettlementPrediction: 結算預測結果
        """
        # 載入各日報告數據
        reports_data = self._load_reports_data(dates)
        
        if not reports_data:
            # 返回預設值
            return self._create_default_prediction(settlement_date, settlement_weekday, dates)
        
        # 趨勢分析
        trend_signals = self._analyze_trends(reports_data)
        overall_trend, trend_strength = self._calculate_overall_trend(trend_signals)
        overall_trend_text = self._get_trend_text(overall_trend, trend_strength)
        
        # 計算關鍵指標
        key_metrics = self._calculate_key_metrics(reports_data)
        
        # 預測結算區間
        predicted_range = self._predict_settlement_range(
            reports_data, 
            trend_signals,
            key_metrics
        )
        
        # 生成劇本
        scenarios = self._generate_scenarios(
            reports_data,
            predicted_range,
            trend_signals,
            key_metrics
        )
        
        # 風險評估
        risks = self._assess_risks(reports_data, trend_signals, key_metrics)
        
        # 取得當前價格
        current_price = key_metrics.get('current_price', 0)
        
        return SettlementPrediction(
            settlement_date=settlement_date,
            settlement_weekday=settlement_weekday,
            analysis_dates=dates,
            current_price=current_price,
            trend_signals=trend_signals,
            overall_trend=overall_trend,
            overall_trend_text=overall_trend_text,
            trend_strength=trend_strength,
            predicted_range=predicted_range,
            scenarios=scenarios,
            key_metrics=key_metrics,
            risks=risks
        )
    
    def _load_reports_data(self, dates: List[str]) -> List[Dict]:
        """載入報告數據"""
        reports = []
        
        for date in dates:
            # 查找該日期的報告檔案
            report_files = list(self.reports_dir.glob(f'report_{date}_*.html'))
            
            if report_files:
                report_data = self._parse_report_html(report_files[0])
                if report_data:
                    report_data['date'] = date
                    reports.append(report_data)
        
        return reports
    
    def _parse_report_html(self, html_path: Path) -> Optional[Dict]:
        """從報告 HTML 解析關鍵數據"""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            data = {}
            
            # 解析收盤價 (從價格走勢區塊)
            close_match = re.search(r'<div class="close-price">([0-9,]+)</div>', html_content)
            if close_match:
                data['close_price'] = int(close_match.group(1).replace(',', ''))
            
            # 解析 P/C Ratio
            pc_match = re.search(r'P/C Ratio.*?(\d+\.\d+)', html_content, re.DOTALL)
            if pc_match:
                data['pc_ratio'] = float(pc_match.group(1))
            
            # 解析 Max Pain
            pain_match = re.search(r'Max Pain.*?([0-9,]+)', html_content, re.DOTALL)
            if pain_match:
                data['max_pain'] = int(pain_match.group(1).replace(',', ''))
            
            # 解析 OI 數據 (從表格或統計區塊)
            call_oi_match = re.search(r'買權總 OI[:\s]*([0-9,]+)', html_content)
            if call_oi_match:
                data['call_oi'] = int(call_oi_match.group(1).replace(',', ''))
            
            put_oi_match = re.search(r'賣權總 OI[:\s]*([0-9,]+)', html_content)
            if put_oi_match:
                data['put_oi'] = int(put_oi_match.group(1).replace(',', ''))
            
            # OI 變化
            call_change_match = re.search(r'買權 OI 變化[:\s]*([+-]?[0-9,]+)', html_content)
            if call_change_match:
                data['call_oi_change'] = int(call_change_match.group(1).replace(',', ''))
            
            put_change_match = re.search(r'賣權 OI 變化[:\s]*([+-]?[0-9,]+)', html_content)
            if put_change_match:
                data['put_oi_change'] = int(put_change_match.group(1).replace(',', ''))
            
            return data if data else None
            
        except Exception as e:
            print(f"解析報告失敗 {html_path}: {e}")
            return None
    
    def _analyze_trends(self, reports_data: List[Dict]) -> List[TrendSignal]:
        """分析趨勢訊號"""
        signals = []
        
        if len(reports_data) < 1:
            return signals
        
        # 1. OI 變化趨勢
        oi_signal = self._analyze_oi_trend(reports_data)
        if oi_signal:
            signals.append(oi_signal)
        
        # 2. P/C Ratio 趨勢
        pc_signal = self._analyze_pc_ratio_trend(reports_data)
        if pc_signal:
            signals.append(pc_signal)
        
        # 3. 價格動能
        price_signal = self._analyze_price_momentum(reports_data)
        if price_signal:
            signals.append(price_signal)
        
        # 4. Max Pain 距離
        pain_signal = self._analyze_max_pain_distance(reports_data)
        if pain_signal:
            signals.append(pain_signal)
        
        return signals
    
    def _analyze_oi_trend(self, reports: List[Dict]) -> Optional[TrendSignal]:
        """分析 OI 變化趨勢"""
        # 取得有 OI 變化數據的報告
        valid_reports = [r for r in reports if 'call_oi_change' in r and 'put_oi_change' in r]
        
        if not valid_reports:
            return None
        
        # 計算平均變化
        avg_call_change = np.mean([r['call_oi_change'] for r in valid_reports])
        avg_put_change = np.mean([r['put_oi_change'] for r in valid_reports])
        
        # 判斷方向
        if avg_call_change > abs(avg_put_change) * 1.3:
            direction = 'bullish'
            strength = min(5, max(2, int(avg_call_change / 3000) + 2))
            desc = f'買權 OI 持續增加 (平均 {int(avg_call_change):+,})，多方積極佈局'
        elif abs(avg_put_change) > avg_call_change * 1.3:
            direction = 'bearish'
            strength = min(5, max(2, int(abs(avg_put_change) / 3000) + 2))
            desc = f'賣權 OI 持續增加 (平均 {int(avg_put_change):+,})，空方積極佈局'
        else:
            direction = 'neutral'
            strength = 2
            desc = f'OI 變化多空均衡 (Call {int(avg_call_change):+,} vs Put {int(avg_put_change):+,})'
        
        return TrendSignal(
            direction=direction,
            strength=strength,
            indicators=['OI 變化', '部位佈局'],
            description=desc
        )
    
    def _analyze_pc_ratio_trend(self, reports: List[Dict]) -> Optional[TrendSignal]:
        """分析 P/C Ratio 趨勢"""
        pc_ratios = [r['pc_ratio'] for r in reports if 'pc_ratio' in r]
        
        if not pc_ratios:
            return None
        
        avg_pc = np.mean(pc_ratios)
        
        if len(pc_ratios) >= 2:
            trend = pc_ratios[-1] - pc_ratios[0]
        else:
            trend = 0
        
        if avg_pc < 0.7:
            direction = 'bullish'
            strength = 4
            desc = f'P/C Ratio 低於 0.7 ({avg_pc:.2f})，市場情緒偏多'
        elif avg_pc > 1.3:
            direction = 'bearish'
            strength = 4
            desc = f'P/C Ratio 高於 1.3 ({avg_pc:.2f})，市場情緒偏空'
        elif trend < -0.1:
            direction = 'bullish'
            strength = 3
            desc = f'P/C Ratio 下降趨勢 ({pc_ratios[0]:.2f} → {pc_ratios[-1]:.2f})，空方減碼'
        elif trend > 0.1:
            direction = 'bearish'
            strength = 3
            desc = f'P/C Ratio 上升趨勢 ({pc_ratios[0]:.2f} → {pc_ratios[-1]:.2f})，空方加碼'
        else:
            direction = 'neutral'
            strength = 2
            desc = f'P/C Ratio 維持中性 ({avg_pc:.2f})'
        
        return TrendSignal(
            direction=direction,
            strength=strength,
            indicators=['P/C Ratio', '市場情緒'],
            description=desc
        )
    
    def _analyze_price_momentum(self, reports: List[Dict]) -> Optional[TrendSignal]:
        """分析價格動能"""
        prices = [r['close_price'] for r in reports if 'close_price' in r]
        
        if len(prices) < 2:
            # 單日數據，判斷與 Max Pain 的關係
            if prices and 'max_pain' in reports[-1]:
                price = prices[0]
                max_pain = reports[-1]['max_pain']
                diff = price - max_pain
                
                if diff > 200:
                    return TrendSignal(
                        direction='bullish',
                        strength=3,
                        indicators=['價格位置'],
                        description=f'價格高於 Max Pain {diff:+d} 點，多方控盤'
                    )
                elif diff < -200:
                    return TrendSignal(
                        direction='bearish',
                        strength=3,
                        indicators=['價格位置'],
                        description=f'價格低於 Max Pain {diff:+d} 點，空方控盤'
                    )
            return None
        
        price_change = prices[-1] - prices[0]
        price_pct = (price_change / prices[0]) * 100
        
        if price_change > 200:
            direction = 'bullish'
            strength = min(5, max(3, int(abs(price_pct) / 0.5) + 2))
            desc = f'價格上漲 {price_change:+d} 點 ({price_pct:+.2f}%)，多方動能強勁'
        elif price_change < -200:
            direction = 'bearish'
            strength = min(5, max(3, int(abs(price_pct) / 0.5) + 2))
            desc = f'價格下跌 {price_change:+d} 點 ({price_pct:+.2f}%)，空方動能強勁'
        else:
            direction = 'neutral'
            strength = 2
            desc = f'價格窄幅震盪 ({price_change:+d} 點)，方向不明'
        
        return TrendSignal(
            direction=direction,
            strength=strength,
            indicators=['價格動能', '趨勢方向'],
            description=desc
        )
    
    def _analyze_max_pain_distance(self, reports: List[Dict]) -> Optional[TrendSignal]:
        """分析 Max Pain 距離"""
        if not reports:
            return None
        
        latest = reports[-1]
        if 'close_price' not in latest or 'max_pain' not in latest:
            return None
        
        price = latest['close_price']
        max_pain = latest['max_pain']
        distance = price - max_pain
        distance_pct = (distance / price) * 100
        
        if distance > 400:
            direction = 'bearish'
            strength = 4
            desc = f'價格高於 Max Pain {distance:+d} 點 ({abs(distance_pct):.1f}%)，結算前可能回歸'
        elif distance < -400:
            direction = 'bullish'
            strength = 4
            desc = f'價格低於 Max Pain {distance:+d} 點 ({abs(distance_pct):.1f}%)，結算前可能反彈'
        elif abs(distance) < 150:
            direction = 'neutral'
            strength = 3
            desc = f'價格貼近 Max Pain ({distance:+d} 點)，磁吸效應明顯'
        else:
            direction = 'neutral'
            strength = 2
            desc = f'價格距離 Max Pain {distance:+d} 點，觀察磁吸效應'
        
        return TrendSignal(
            direction=direction,
            strength=strength,
            indicators=['Max Pain', '磁吸效應'],
            description=desc
        )
    
    def _calculate_overall_trend(
        self, 
        signals: List[TrendSignal]
    ) -> Tuple[str, int]:
        """計算整體趨勢"""
        if not signals:
            return 'neutral', 2
        
        # 加權計算
        bullish_score = sum(s.strength for s in signals if s.direction == 'bullish')
        bearish_score = sum(s.strength for s in signals if s.direction == 'bearish')
        neutral_score = sum(s.strength for s in signals if s.direction == 'neutral')
        
        total = bullish_score + bearish_score + neutral_score
        if total == 0:
            return 'neutral', 2
        
        # 判斷主趨勢
        if bullish_score > bearish_score * 1.3 and bullish_score > neutral_score:
            strength = min(5, max(3, int((bullish_score / total) * 8)))
            return 'bullish', strength
        elif bearish_score > bullish_score * 1.3 and bearish_score > neutral_score:
            strength = min(5, max(3, int((bearish_score / total) * 8)))
            return 'bearish', strength
        else:
            strength = min(4, max(2, int((neutral_score / total) * 6)))
            return 'neutral', strength
    
    def _get_trend_text(self, direction: str, strength: int) -> str:
        """取得趨勢文字描述"""
        strength_text = ['', '微弱', '偏弱', '中性', '偏強', '強勁'][min(strength, 5)]
        
        if direction == 'bullish':
            return f'多頭趨勢 ({strength_text})'
        elif direction == 'bearish':
            return f'空頭趨勢 ({strength_text})'
        else:
            return f'震盪整理 ({strength_text})'
    
    def _calculate_key_metrics(self, reports: List[Dict]) -> Dict[str, any]:
        """計算關鍵指標"""
        if not reports:
            return {}
        
        latest = reports[-1]
        
        metrics = {
            'current_price': latest.get('close_price', 0),
            'max_pain': latest.get('max_pain', 0),
        }
        
        # P/C Ratio
        pc_ratios = [r['pc_ratio'] for r in reports if 'pc_ratio' in r]
        if pc_ratios:
            metrics['avg_pc_ratio'] = np.mean(pc_ratios)
            metrics['latest_pc_ratio'] = pc_ratios[-1]
        
        # OI 數據
        if 'call_oi' in latest:
            metrics['total_call_oi'] = latest['call_oi']
        if 'put_oi' in latest:
            metrics['total_put_oi'] = latest['put_oi']
        
        # OI 變化
        call_changes = [r['call_oi_change'] for r in reports if 'call_oi_change' in r]
        put_changes = [r['put_oi_change'] for r in reports if 'put_oi_change' in r]
        
        if call_changes:
            metrics['avg_call_oi_change'] = np.mean(call_changes)
        if put_changes:
            metrics['avg_put_oi_change'] = np.mean(put_changes)
        
        return metrics
    
    def _predict_settlement_range(
        self,
        reports: List[Dict],
        signals: List[TrendSignal],
        metrics: Dict
    ) -> Tuple[int, int]:
        """預測結算區間"""
        current_price = metrics.get('current_price', 23000)
        max_pain = metrics.get('max_pain', 23000)
        
        # 基於趨勢調整
        overall_trend, trend_strength = self._calculate_overall_trend(signals)
        
        # 計算基準點
        if overall_trend == 'bullish':
            # 多頭：偏向當前價與 Max Pain 之間偏上
            if current_price > max_pain:
                center = int((current_price * 0.6 + max_pain * 0.4))
            else:
                center = int((current_price * 0.4 + max_pain * 0.6))
        elif overall_trend == 'bearish':
            # 空頭：偏向當前價與 Max Pain 之間偏下
            if current_price < max_pain:
                center = int((current_price * 0.6 + max_pain * 0.4))
            else:
                center = int((current_price * 0.4 + max_pain * 0.6))
        else:
            # 中性：Max Pain 附近
            center = max_pain
        
        # 計算波動範圍 (根據趨勢強度)
        base_range = 300
        volatility = int(base_range * (1 + trend_strength * 0.2))
        
        # 計算區間 (取整百)
        lower = (center - volatility) // 100 * 100
        upper = (center + volatility) // 100 * 100
        
        return (lower, upper)
    
    def _generate_scenarios(
        self,
        reports: List[Dict],
        predicted_range: Tuple[int, int],
        signals: List[TrendSignal],
        metrics: Dict
    ) -> List[Scenario]:
        """生成結算劇本"""
        scenarios = []
        
        current_price = metrics.get('current_price', 23000)
        max_pain = metrics.get('max_pain', 23000)
        lower, upper = predicted_range
        center = (lower + upper) // 2
        
        # 劇本 1: 強勢上攻 🚀
        scenarios.append(Scenario(
            name='強勢上攻',
            probability=self._calculate_scenario_probability('bullish', signals),
            price_range=(upper - 50, upper + 250),
            key_levels=[upper, upper + 100, upper + 200],
            conditions=[
                '✓ 多方持續加碼買權部位',
                '✓ P/C Ratio 持續下降',
                '✓ 價格突破近期高點',
                '✓ 成交量放大配合'
            ],
            strategy='順勢做多，停利設在區間上緣 +100，停損在 Max Pain',
            color='#22c55e',
            icon='🚀'
        ))
        
        # 劇本 2: 震盪整理 ⚖️
        scenarios.append(Scenario(
            name='震盪整理',
            probability=self._calculate_scenario_probability('neutral', signals),
            price_range=(lower, upper),
            key_levels=[max_pain, center, (lower + upper) // 2],
            conditions=[
                '✓ 多空力道均衡',
                '✓ OI 分佈集中在特定區間',
                '✓ 價格在 Max Pain 附近磁吸',
                '✓ 波動度收斂'
            ],
            strategy='區間操作為主，高出低進，避免追高殺低',
            color='#f59e0b',
            icon='⚖️'
        ))
        
        # 劇本 3: 回檔修正 📉
        scenarios.append(Scenario(
            name='回檔修正',
            probability=self._calculate_scenario_probability('bearish', signals),
            price_range=(lower - 250, lower + 50),
            key_levels=[lower - 200, lower - 100, lower],
            conditions=[
                '✓ 空方持續加碼賣權部位',
                '✓ P/C Ratio 持續上升',
                '✓ 價格跌破近期低點',
                '✓ 恐慌性賣壓出現'
            ],
            strategy='順勢做空，停利設在區間下緣 -100，停損在 Max Pain',
            color='#ef4444',
            icon='📉'
        ))
        
        # 劇本 4: Max Pain 磁吸 🧲
        pain_distance = abs(current_price - max_pain)
        if pain_distance > 200:
            scenarios.append(Scenario(
                name='Max Pain 磁吸',
                probability=min(40.0, pain_distance / 10),
                price_range=(max_pain - 100, max_pain + 100),
                key_levels=[max_pain - 100, max_pain, max_pain + 100],
                conditions=[
                    f'✓ 價格距離 Max Pain {pain_distance} 點',
                    '✓ 結算日臨近，磁吸效應增強',
                    '✓ 莊家調節部位',
                    '✓ 雙邊力道趨於平衡'
                ],
                strategy=f'預期價格向 {max_pain:,} 靠攏，可布局雙賣策略',
                color='#8b5cf6',
                icon='🧲'
            ))
        
        # 依機率排序
        scenarios.sort(key=lambda x: x.probability, reverse=True)
        
        return scenarios[:3]  # 最多返回 3 個主要劇本
    
    def _calculate_scenario_probability(
        self,
        scenario_type: str,
        signals: List[TrendSignal]
    ) -> float:
        """計算劇本機率"""
        if not signals:
            return 33.3
        
        # 計算各趨勢的強度總和
        bullish_score = sum(s.strength for s in signals if s.direction == 'bullish')
        bearish_score = sum(s.strength for s in signals if s.direction == 'bearish')
        neutral_score = sum(s.strength for s in signals if s.direction == 'neutral')
        
        total_score = bullish_score + bearish_score + neutral_score
        
        if total_score == 0:
            return 33.3
        
        if scenario_type == 'bullish':
            base_prob = (bullish_score / total_score) * 100
        elif scenario_type == 'bearish':
            base_prob = (bearish_score / total_score) * 100
        else:  # neutral
            base_prob = (neutral_score / total_score) * 100
        
        # 確保機率在合理範圍
        return max(15.0, min(60.0, base_prob))
    
    def _assess_risks(
        self,
        reports: List[Dict],
        signals: List[TrendSignal],
        metrics: Dict
    ) -> List[str]:
        """評估風險因素"""
        risks = []
        
        if not reports:
            return risks
        
        latest = reports[-1]
        
        # 檢查 Max Pain 距離
        if 'close_price' in latest and 'max_pain' in latest:
            distance = abs(latest['close_price'] - latest['max_pain'])
            if distance > 500:
                risks.append(f'⚠️ 價格遠離 Max Pain ({distance} 點)，磁吸風險高')
        
        # 檢查 P/C Ratio 極端值
        pc_ratio = metrics.get('latest_pc_ratio')
        if pc_ratio:
            if pc_ratio < 0.6:
                risks.append(f'⚠️ P/C Ratio 極低 ({pc_ratio:.2f})，市場過度樂觀')
            elif pc_ratio > 1.5:
                risks.append(f'⚠️ P/C Ratio 極高 ({pc_ratio:.2f})，市場過度悲觀')
        
        # 檢查 OI 劇烈變化
        avg_call_change = metrics.get('avg_call_oi_change', 0)
        avg_put_change = metrics.get('avg_put_oi_change', 0)
        
        if abs(avg_call_change) > 10000 or abs(avg_put_change) > 10000:
            risks.append('⚠️ OI 劇烈變動，留意大戶動向與主力意圖')
        
        # 檢查趨勢一致性
        if len(signals) >= 3:
            directions = [s.direction for s in signals]
            if len(set(directions)) == len(directions):  # 所有訊號方向都不同
                risks.append('⚠️ 趨勢訊號分歧，市場方向不明確')
        
        # 數據不足風險
        if len(reports) < 2:
            risks.append('⚠️ 分析數據不足，預測準確度降低')
        
        return risks
    
    def _create_default_prediction(
        self,
        settlement_date: str,
        settlement_weekday: str,
        dates: List[str]
    ) -> SettlementPrediction:
        """創建預設預測結果（當無法載入數據時）"""
        return SettlementPrediction(
            settlement_date=settlement_date,
            settlement_weekday=settlement_weekday,
            analysis_dates=dates,
            current_price=0,
            trend_signals=[],
            overall_trend='neutral',
            overall_trend_text='數據不足',
            trend_strength=0,
            predicted_range=(0, 0),
            scenarios=[],
            key_metrics={},
            risks=['⚠️ 無法載入分析數據，請確認報告檔案是否存在']
        )
