"""
選擇權分析模組
計算 OI 分析、Put/Call Ratio、Max Pain 等指標
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Tuple
from .parser import OptionsData


@dataclass
class AnalysisResult:
    """分析結果資料結構"""
    date: str
    contract_month: str

    # Put/Call Ratio
    pc_ratio_volume: float  # 成交量 P/C Ratio
    pc_ratio_oi: float  # 未平倉 P/C Ratio

    # Max Pain
    max_pain: int  # 最大痛點價位
    max_pain_value: float  # 最大痛點金額

    # OI 分析
    total_call_oi: int  # 買權總未平倉
    total_put_oi: int  # 賣權總未平倉
    call_oi_change: int  # 買權 OI 變化
    put_oi_change: int  # 賣權 OI 變化

    # 關鍵價位
    max_call_oi_strike: int  # 最大買權 OI 履約價
    max_put_oi_strike: int  # 最大賣權 OI 履約價
    max_call_oi: int  # 最大買權 OI 量
    max_put_oi: int  # 最大賣權 OI 量

    # 價位範圍
    call_resistance: List[int]  # 買權壓力區 (高 OI 價位)
    put_support: List[int]  # 賣權支撐區 (高 OI 價位)

    # 原始資料
    df: pd.DataFrame = None


class OptionsAnalyzer:
    """選擇權分析器"""

    def __init__(self):
        self.multiplier = 50  # 台指選擇權每點 50 元

    def analyze(self, options_data: OptionsData) -> AnalysisResult:
        """
        分析選擇權資料

        Args:
            options_data: 選擇權資料

        Returns:
            分析結果
        """
        df = options_data.to_dataframe()

        # 計算 Put/Call Ratio
        pc_ratio_volume = self._calculate_pc_ratio(
            sum(options_data.put_volume),
            sum(options_data.call_volume)
        )
        pc_ratio_oi = self._calculate_pc_ratio(
            sum(options_data.put_oi),
            sum(options_data.call_oi)
        )

        # 計算 Max Pain
        max_pain, max_pain_value = self._calculate_max_pain(options_data)

        # OI 統計
        total_call_oi = sum(options_data.call_oi)
        total_put_oi = sum(options_data.put_oi)
        call_oi_change = sum(options_data.call_oi_change)
        put_oi_change = sum(options_data.put_oi_change)

        # 找出關鍵價位
        call_oi_dict = dict(zip(options_data.strike_prices, options_data.call_oi))
        put_oi_dict = dict(zip(options_data.strike_prices, options_data.put_oi))

        max_call_oi_strike = max(call_oi_dict, key=call_oi_dict.get) if call_oi_dict else 0
        max_put_oi_strike = max(put_oi_dict, key=put_oi_dict.get) if put_oi_dict else 0

        # 壓力支撐區 (取 OI 前 3 高的價位)
        call_resistance = self._get_top_strikes(call_oi_dict, 3)
        put_support = self._get_top_strikes(put_oi_dict, 3)

        return AnalysisResult(
            date=options_data.date,
            contract_month=options_data.contract_month,
            pc_ratio_volume=pc_ratio_volume,
            pc_ratio_oi=pc_ratio_oi,
            max_pain=max_pain,
            max_pain_value=max_pain_value,
            total_call_oi=total_call_oi,
            total_put_oi=total_put_oi,
            call_oi_change=call_oi_change,
            put_oi_change=put_oi_change,
            max_call_oi_strike=max_call_oi_strike,
            max_put_oi_strike=max_put_oi_strike,
            max_call_oi=call_oi_dict.get(max_call_oi_strike, 0),
            max_put_oi=put_oi_dict.get(max_put_oi_strike, 0),
            call_resistance=call_resistance,
            put_support=put_support,
            df=df,
        )

    def _calculate_pc_ratio(self, put_value: float, call_value: float) -> float:
        """
        計算 Put/Call Ratio
        """
        if call_value == 0:
            return float('inf') if put_value > 0 else 0
        return round(put_value / call_value, 4)

    def _calculate_max_pain(self, options_data: OptionsData) -> Tuple[int, float]:
        """
        計算 Max Pain (最大痛點)

        Max Pain 是讓選擇權買方總損失最大的價位，
        也就是讓選擇權賣方獲利最大的價位。

        計算方法:
        對每個可能的結算價，計算所有選擇權的內含價值總和，
        最小值對應的履約價就是 Max Pain。

        Returns:
            (max_pain_price, total_pain_value)
        """
        strikes = options_data.strike_prices
        call_oi = options_data.call_oi
        put_oi = options_data.put_oi

        if not strikes:
            return 0, 0.0

        pain_values = {}

        for settlement_price in strikes:
            total_pain = 0

            for i, strike in enumerate(strikes):
                # Call 的損失 (結算價高於履約價時有價值)
                call_value = max(0, settlement_price - strike) * call_oi[i]

                # Put 的損失 (結算價低於履約價時有價值)
                put_value = max(0, strike - settlement_price) * put_oi[i]

                total_pain += (call_value + put_value) * self.multiplier

            pain_values[settlement_price] = total_pain

        # 找出最小痛點 (最小值)
        max_pain = min(pain_values, key=pain_values.get)
        max_pain_value = pain_values[max_pain]

        return max_pain, max_pain_value

    def _get_top_strikes(self, oi_dict: dict, n: int = 3) -> List[int]:
        """
        取得 OI 最高的前 N 個履約價
        """
        sorted_strikes = sorted(oi_dict.items(), key=lambda x: x[1], reverse=True)
        return [strike for strike, oi in sorted_strikes[:n]]

    def analyze_trend(self, current: AnalysisResult, previous: AnalysisResult = None) -> dict:
        """
        分析趨勢變化

        Args:
            current: 當前分析結果
            previous: 前一日分析結果 (可選)

        Returns:
            趨勢分析字典
        """
        trend = {
            'market_sentiment': self._interpret_pc_ratio(current.pc_ratio_oi),
            'max_pain_level': current.max_pain,
        }

        # 解讀 OI 分布
        if current.max_call_oi_strike > current.max_put_oi_strike:
            trend['oi_bias'] = 'bearish'
            trend['oi_interpretation'] = f'壓力區 {current.max_call_oi_strike} 高於支撐區 {current.max_put_oi_strike}'
        else:
            trend['oi_bias'] = 'bullish'
            trend['oi_interpretation'] = f'支撐區 {current.max_put_oi_strike} 高於壓力區 {current.max_call_oi_strike}'

        # 與前一日比較
        if previous:
            trend['pc_ratio_change'] = current.pc_ratio_oi - previous.pc_ratio_oi
            trend['max_pain_change'] = current.max_pain - previous.max_pain
            trend['call_oi_trend'] = 'increasing' if current.call_oi_change > 0 else 'decreasing'
            trend['put_oi_trend'] = 'increasing' if current.put_oi_change > 0 else 'decreasing'

        return trend

    def _interpret_pc_ratio(self, pc_ratio: float) -> str:
        """
        解讀 P/C Ratio 的市場意義
        """
        if pc_ratio < 0.7:
            return 'extremely_bullish'  # 極度樂觀
        elif pc_ratio < 0.9:
            return 'bullish'  # 樂觀
        elif pc_ratio < 1.1:
            return 'neutral'  # 中性
        elif pc_ratio < 1.3:
            return 'bearish'  # 悲觀
        else:
            return 'extremely_bearish'  # 極度悲觀

    def get_key_levels(self, result: AnalysisResult) -> dict:
        """
        取得關鍵價位摘要

        Args:
            result: 分析結果

        Returns:
            關鍵價位字典
        """
        return {
            'max_pain': result.max_pain,
            'resistance': result.call_resistance,
            'support': result.put_support,
            'range': {
                'upper': result.call_resistance[0] if result.call_resistance else None,
                'lower': result.put_support[0] if result.put_support else None,
            }
        }


def analyze_from_dataframe(df: pd.DataFrame, date: str = "unknown", contract_month: str = "unknown") -> AnalysisResult:
    """
    從 DataFrame 進行分析的輔助函數

    Args:
        df: 包含選擇權資料的 DataFrame
        date: 交易日期
        contract_month: 契約月份

    Returns:
        分析結果
    """
    # 建立 OptionsData
    options_data = OptionsData(
        date=date,
        contract_month=contract_month,
        strike_prices=df['履約價'].tolist(),
        call_volume=df['買權成交量'].tolist() if '買權成交量' in df.columns else [0] * len(df),
        call_oi=df['買權未平倉'].tolist(),
        call_oi_change=df['買權OI變化'].tolist() if '買權OI變化' in df.columns else [0] * len(df),
        put_volume=df['賣權成交量'].tolist() if '賣權成交量' in df.columns else [0] * len(df),
        put_oi=df['賣權未平倉'].tolist(),
        put_oi_change=df['賣權OI變化'].tolist() if '賣權OI變化' in df.columns else [0] * len(df),
    )

    analyzer = OptionsAnalyzer()
    return analyzer.analyze(options_data)


if __name__ == "__main__":
    # 測試分析功能
    from .parser import PDFParser
    from pathlib import Path
    import sys

    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        project_root = Path(__file__).parent.parent
        pdf_dir = project_root / "data" / "pdf"
        pdf_files = list(pdf_dir.glob("*.pdf"))

        if pdf_files:
            pdf_path = str(pdf_files[0])
        else:
            print("請提供 PDF 檔案路徑或將 PDF 放入 data/pdf 目錄")
            sys.exit(1)

    print(f"分析檔案: {pdf_path}")

    parser = PDFParser()
    analyzer = OptionsAnalyzer()

    try:
        options_list = parser.parse(pdf_path)

        for options_data in options_list:
            print(f"\n=== {options_data.contract_month} 月份分析結果 ===")
            result = analyzer.analyze(options_data)

            print(f"P/C Ratio (成交量): {result.pc_ratio_volume:.4f}")
            print(f"P/C Ratio (未平倉): {result.pc_ratio_oi:.4f}")
            print(f"Max Pain: {result.max_pain}")
            print(f"最大買權 OI: {result.max_call_oi_strike} ({result.max_call_oi:,} 口)")
            print(f"最大賣權 OI: {result.max_put_oi_strike} ({result.max_put_oi:,} 口)")
            print(f"壓力區: {result.call_resistance}")
            print(f"支撐區: {result.put_support}")

    except Exception as e:
        print(f"分析失敗: {e}")
