"""
結算情境分析模組
基於 OI 分布和價格行為，分析可能的結算情境
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
from .parser import OptionsData
from .analyzer import OptionsAnalyzer


@dataclass
class SettlementScenario:
    """結算情境"""
    name: str  # 情境名稱
    probability: str  # 機率評估 (高/中/低)
    settlement_range: Tuple[int, int]  # 結算區間
    conditions: List[str]  # 觸發條件
    description: str  # 情境描述
    impact: str  # 對選擇權的影響
    key_levels: List[int]  # 關鍵價位


@dataclass
class SettlementAnalysis:
    """結算分析結果"""
    date: str
    contract_month: str
    current_max_pain: int  # 當前最大痛點
    scenarios: List[SettlementScenario]  # 可能情境
    critical_strikes: List[int]  # 關鍵履約價
    dealer_position: str  # 莊家位置判斷
    market_bias: str  # 市場偏向


class SettlementAnalyzer:
    """結算情境分析器"""

    def __init__(self):
        self.multiplier = 50  # 台指選擇權每點 50 元
        self.base_analyzer = OptionsAnalyzer()

    def analyze_settlement_scenarios(self, options_data: OptionsData) -> SettlementAnalysis:
        """
        分析結算情境

        Args:
            options_data: 選擇權資料

        Returns:
            結算分析結果
        """
        # 先做基礎分析
        base_result = self.base_analyzer.analyze(options_data)

        # 找出關鍵價位
        critical_strikes = self._identify_critical_strikes(options_data)

        # 判斷莊家位置和市場偏向
        dealer_position = self._analyze_dealer_position(options_data, base_result)
        market_bias = self._analyze_market_bias(options_data, base_result)

        # 生成可能的結算情境
        scenarios = self._generate_scenarios(
            options_data,
            base_result,
            critical_strikes,
            dealer_position,
            market_bias
        )

        return SettlementAnalysis(
            date=options_data.date,
            contract_month=options_data.contract_month,
            current_max_pain=base_result.max_pain,
            scenarios=scenarios,
            critical_strikes=critical_strikes,
            dealer_position=dealer_position,
            market_bias=market_bias
        )

    def _identify_critical_strikes(self, options_data: OptionsData) -> List[int]:
        """
        識別關鍵履約價
        關鍵價位包括：
        1. Call OI 最大的價位
        2. Put OI 最大的價位
        3. 總 OI 最大的價位
        4. OI 變化最大的價位
        """
        critical = []

        # Call OI 最大
        call_oi_dict = dict(zip(options_data.strike_prices, options_data.call_oi))
        if call_oi_dict:
            max_call_strike = max(call_oi_dict, key=call_oi_dict.get)
            critical.append(max_call_strike)

        # Put OI 最大
        put_oi_dict = dict(zip(options_data.strike_prices, options_data.put_oi))
        if put_oi_dict:
            max_put_strike = max(put_oi_dict, key=put_oi_dict.get)
            critical.append(max_put_strike)

        # 總 OI 最大
        total_oi_dict = {
            strike: call_oi_dict.get(strike, 0) + put_oi_dict.get(strike, 0)
            for strike in options_data.strike_prices
        }
        if total_oi_dict:
            max_total_strike = max(total_oi_dict, key=total_oi_dict.get)
            critical.append(max_total_strike)

        # OI 變化最大（絕對值）
        oi_change_dict = {
            strike: abs(options_data.call_oi_change[i]) + abs(options_data.put_oi_change[i])
            for i, strike in enumerate(options_data.strike_prices)
        }
        if oi_change_dict:
            max_change_strike = max(oi_change_dict, key=oi_change_dict.get)
            critical.append(max_change_strike)

        # 去重並排序
        return sorted(list(set(critical)))

    def _analyze_dealer_position(self, options_data: OptionsData, base_result) -> str:
        """
        分析莊家位置
        基於 OI 變化判斷莊家的建倉方向
        """
        call_oi_change = base_result.call_oi_change
        put_oi_change = base_result.put_oi_change

        if put_oi_change > call_oi_change * 1.5:
            return "莊家大量賣出 Put（看多或護盤）"
        elif call_oi_change > put_oi_change * 1.5:
            return "莊家大量賣出 Call（看空或壓盤）"
        elif put_oi_change > 0 and call_oi_change > 0:
            return "莊家雙邊賣出（區間整理）"
        else:
            return "莊家持倉減少（觀望或平倉）"

    def _analyze_market_bias(self, options_data: OptionsData, base_result) -> str:
        """
        分析市場偏向
        基於 Put/Call Ratio 判斷市場情緒
        """
        pc_ratio = base_result.pc_ratio_oi

        if pc_ratio > 1.3:
            return "看空氣氛濃厚（Put 未平倉明顯大於 Call）"
        elif pc_ratio > 1.1:
            return "偏空（Put 未平倉略大於 Call）"
        elif pc_ratio > 0.9:
            return "中性（Put/Call 未平倉接近）"
        elif pc_ratio > 0.7:
            return "偏多（Call 未平倉略大於 Put）"
        else:
            return "看多氣氛濃厚（Call 未平倉明顯大於 Put）"

    def _generate_scenarios(
        self,
        options_data: OptionsData,
        base_result,
        critical_strikes: List[int],
        dealer_position: str,
        market_bias: str
    ) -> List[SettlementScenario]:
        """
        生成結算情境
        
        這個函數生成3種可能的結算情境，以 Max Pain 為中心點來推測：
        - 情境 A: 跌破 Max Pain，往下至主要 Put OI 支撐
        - 情境 B: 突破 Max Pain，往上至主要 Call OI 壓力  
        - 情境 C: 在 Max Pain 附近整理（最常見）
        """
        scenarios = []

        # 找出最大 Put OI 和 Call OI 價位
        put_oi_dict = dict(zip(options_data.strike_prices, options_data.put_oi))
        call_oi_dict = dict(zip(options_data.strike_prices, options_data.call_oi))

        max_put_strike = max(put_oi_dict, key=put_oi_dict.get) if put_oi_dict else 0
        max_call_strike = max(call_oi_dict, key=call_oi_dict.get) if call_oi_dict else 0
        max_pain = base_result.max_pain

        # 情境 A: 弱勢結算（跌破 Max Pain，往最大 Put OI 靠攏）
        # 如果跌破 Max Pain，可能會往主要 Put OI 集中處靠攏
        weak_low = max_put_strike - 100
        weak_high = max_put_strike + 100
        
        scenarios.append(SettlementScenario(
            name="情境 A：弱勢結算（跌破防線）",
            probability=self._assess_weak_probability(options_data, base_result, market_bias),
            settlement_range=(weak_low, weak_high),
            conditions=[
                f"現貨跌破 Max Pain {max_pain:,} 點",
                f"往最大 Put OI ({max_put_strike:,} 點) 靠攏",
                "賣壓持續，買盤不足"
            ],
            description=f"如果現貨持續走弱並跌破 Max Pain {max_pain:,} 點，可能會往主要 Put OI 集中處（{max_put_strike:,} 點）移動。",
            impact=f"結算區間可能落在 {weak_low:,} ~ {weak_high:,} 點附近。"
                   f"這會讓 {max_put_strike:,} 點以上的 Put 變成價內，Call 則價值縮水或歸零。",
            key_levels=[weak_low, max_put_strike, weak_high]
        ))

        # 情境 B: 強勢結算（突破 Max Pain，往最大 Call OI 靠攏）
        # 如果突破 Max Pain，可能會被 Call OI 壓力壓回
        strong_low = max_call_strike - 100
        strong_high = max_call_strike + 100

        scenarios.append(SettlementScenario(
            name="情境 B：強勢結算（突破壓力）",
            probability=self._assess_rally_probability(options_data, base_result, dealer_position),
            settlement_range=(strong_low, strong_high),
            conditions=[
                f"現貨突破 Max Pain {max_pain:,} 點",
                f"往最大 Call OI ({max_call_strike:,} 點) 靠攏",
                "買盤強勁，但遇到壓力"
            ],
            description=f"如果現貨持續走強並突破 Max Pain {max_pain:,} 點，可能會往主要 Call OI 集中處（{max_call_strike:,} 點）移動，但會遇到壓力。",
            impact=f"結算價可能落在 {strong_low:,} ~ {strong_high:,} 點附近。"
                   f"這會讓 {max_call_strike:,} 點以下的 Call 變成價內，Put 則價值縮水或歸零。",
            key_levels=[strong_low, max_call_strike, strong_high]
        ))

        # 情境 C: 區間震盪結算（在 Max Pain 附近，最常見）
        range_low = max_pain - 100
        range_high = max_pain + 100
        
        scenarios.append(SettlementScenario(
            name="情境 C：區間震盪（Max Pain 附近）",
            probability="高",  # 這是最常見的情境
            settlement_range=(range_low, range_high),
            conditions=[
                f"現貨在 Max Pain {max_pain:,} 點附近整理",
                "多空力量均衡",
                "莊家試圖將價格拉向 Max Pain"
            ],
            description=f"最常見的情境，結算價會被拉向 Max Pain ({max_pain:,} 點)，這是選擇權賣方損失最小的價位。",
            impact=f"結算價在 {range_low:,} ~ {range_high:,} 點，"
                   f"Max Pain 兩側的選擇權都有部分價值，達到莊家利益最大化。",
            key_levels=[range_low, max_pain, range_high]
        ))

        return scenarios

    def _assess_weak_probability(self, options_data, base_result, market_bias: str) -> str:
        """評估弱勢結算的機率"""
        if "看空" in market_bias and base_result.put_oi_change > 0:
            return "高"
        elif base_result.put_oi_change > base_result.call_oi_change:
            return "中等"
        else:
            return "低"

    def _assess_rally_probability(self, options_data, base_result, dealer_position: str) -> str:
        """評估拉回護盤的機率"""
        if "看多" in dealer_position or "護盤" in dealer_position:
            return "中等"
        elif base_result.call_oi_change > base_result.put_oi_change:
            return "中等"
        else:
            return "低"

    def _find_support_level(self, options_data, put_oi_dict, max_put_strike: int) -> int:
        """尋找支撐位（通常是次高 Put OI 價位或 Max Pain 下方）"""
        # 找出第二高的 Put OI 價位
        sorted_puts = sorted(put_oi_dict.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_puts) >= 2:
            return sorted_puts[1][0]
        else:
            return max_put_strike - 100

    def format_analysis_text(self, analysis: SettlementAnalysis) -> str:
        """
        格式化分析結果為文字報告
        """
        lines = []
        lines.append(f"# {analysis.contract_month} 結算情境分析\n")
        lines.append(f"**交易日期**: {analysis.date}")
        lines.append(f"**當前 Max Pain**: {analysis.current_max_pain:,} 點")
        lines.append(f"**莊家位置判斷**: {analysis.dealer_position}")
        lines.append(f"**市場偏向**: {analysis.market_bias}")
        lines.append(f"**關鍵履約價**: {', '.join(f'{s:,}' for s in analysis.critical_strikes)} 點\n")

        lines.append("## 今日結算價的可能走勢：\n")

        for i, scenario in enumerate(analysis.scenarios, 1):
            lines.append(f"### {scenario.name}\n")
            lines.append(f"**機率評估**: {scenario.probability}\n")
            lines.append(f"**觸發條件**:")
            for cond in scenario.conditions:
                lines.append(f"- {cond}")
            lines.append(f"\n**情境描述**: {scenario.description}\n")
            lines.append(f"**結算影響**: {scenario.impact}\n")
            lines.append(f"**關鍵價位**: {', '.join(f'{k:,}' for k in scenario.key_levels)} 點\n")

        return "\n".join(lines)
