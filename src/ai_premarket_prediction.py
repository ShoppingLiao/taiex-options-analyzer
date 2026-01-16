"""
AI 盤前預測分析器

在結算日早上 08:00 執行，結合：
1. 前一天夜盤資料（OHLC、震幅）
2. 前一天的交易員視角分析
3. 原本的結算預測

產出新的盤前預測結果
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AIPremarketPrediction:
    """AI 盤前預測分析器"""

    def __init__(self):
        self.data_dir = Path('data/ai_learning')
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def generate_premarket_prediction(
        self,
        night_session_data: Dict,
        previous_trader_analysis: Optional[Dict],
        settlement_prediction: Dict,
        settlement_date: str
    ) -> Dict:
        """
        生成盤前預測

        Args:
            night_session_data: 夜盤資料
            previous_trader_analysis: 前一天交易員視角分析
            settlement_prediction: 原本的結算預測
            settlement_date: 結算日期 (YYYYMMDD)

        Returns:
            盤前預測結果
        """
        logger.info(f"生成 {settlement_date} 的盤前預測...")

        # 分析夜盤走勢
        night_analysis = self._analyze_night_session(night_session_data)

        # 分析與前一天預測的一致性
        consistency_analysis = self._analyze_consistency(
            night_session_data,
            previous_trader_analysis,
            settlement_prediction
        )

        # 調整預測區間
        adjusted_prediction = self._adjust_prediction(
            night_session_data,
            settlement_prediction,
            night_analysis,
            consistency_analysis
        )

        # 生成開盤策略建議
        strategy = self._generate_opening_strategy(
            night_analysis,
            consistency_analysis,
            adjusted_prediction
        )

        # 生成綜合分析文字
        analysis_text = self._generate_analysis_text(
            night_session_data,
            night_analysis,
            consistency_analysis,
            adjusted_prediction,
            strategy
        )

        result = {
            'settlement_date': settlement_date,
            'generated_time': datetime.now().strftime('%Y/%m/%d %H:%M'),
            'night_session': night_session_data,
            'night_analysis': night_analysis,
            'consistency_analysis': consistency_analysis,
            'adjusted_prediction': adjusted_prediction,
            'strategy': strategy,
            'analysis_text': analysis_text
        }

        # 保存預測記錄
        self._save_prediction(settlement_date, result)

        return result

    def _analyze_night_session(self, night_data: Dict) -> Dict:
        """分析夜盤走勢"""
        amplitude = night_data.get('amplitude', 0)
        change = night_data.get('change', 0)
        change_pct = night_data.get('change_pct', 0)

        # 判斷夜盤趨勢
        if change > 50:
            trend = 'bullish'
            trend_text = '夜盤偏多'
        elif change < -50:
            trend = 'bearish'
            trend_text = '夜盤偏空'
        else:
            trend = 'neutral'
            trend_text = '夜盤持平'

        # 判斷震幅等級
        if amplitude > 150:
            amplitude_level = 'high'
            amplitude_text = '高震幅'
        elif amplitude > 80:
            amplitude_level = 'normal'
            amplitude_text = '正常震幅'
        else:
            amplitude_level = 'low'
            amplitude_text = '低震幅'

        # 計算夜盤收盤位置（相對於高低點）
        if night_data.get('high') and night_data.get('low'):
            high = night_data['high']
            low = night_data['low']
            close = night_data.get('close', (high + low) / 2)
            range_total = high - low if high > low else 1

            position = (close - low) / range_total
            if position > 0.7:
                close_position = '收在高檔'
            elif position < 0.3:
                close_position = '收在低檔'
            else:
                close_position = '收在中間'
        else:
            close_position = '未知'

        return {
            'trend': trend,
            'trend_text': trend_text,
            'amplitude': amplitude,
            'amplitude_level': amplitude_level,
            'amplitude_text': amplitude_text,
            'change': change,
            'change_pct': change_pct,
            'close_position': close_position
        }

    def _analyze_consistency(
        self,
        night_data: Dict,
        trader_analysis: Optional[Dict],
        settlement_prediction: Dict
    ) -> Dict:
        """分析夜盤與前一天預測的一致性"""

        # 原本預測的趨勢
        original_trend = settlement_prediction.get('overall_trend', 'neutral')
        original_range = settlement_prediction.get('predicted_range', [0, 0])

        # 夜盤收盤價
        night_close = night_data.get('close', 0)

        # 判斷一致性
        if original_trend == 'bullish':
            if night_data.get('change', 0) > 0:
                consistency = 'aligned'
                consistency_text = '夜盤走勢與預測一致（偏多）'
            else:
                consistency = 'diverged'
                consistency_text = '夜盤走勢與預測背離（預測偏多但夜盤偏空）'
        elif original_trend == 'bearish':
            if night_data.get('change', 0) < 0:
                consistency = 'aligned'
                consistency_text = '夜盤走勢與預測一致（偏空）'
            else:
                consistency = 'diverged'
                consistency_text = '夜盤走勢與預測背離（預測偏空但夜盤偏多）'
        else:
            consistency = 'neutral'
            consistency_text = '原預測為中性，夜盤走勢影響有限'

        # 檢查夜盤收盤是否在預測區間內
        if original_range[0] <= night_close <= original_range[1]:
            in_range = True
            range_text = '夜盤收盤在預測區間內'
        elif night_close < original_range[0]:
            in_range = False
            range_text = f'夜盤收盤已跌破預測區間下緣 ({original_range[0]:,})'
        else:
            in_range = False
            range_text = f'夜盤收盤已突破預測區間上緣 ({original_range[1]:,})'

        # 交易員視角分析的建議
        trader_view_summary = None
        if trader_analysis:
            trader_view_summary = trader_analysis.get('market_outlook', {}).get('main_view', '')

        return {
            'consistency': consistency,
            'consistency_text': consistency_text,
            'original_trend': original_trend,
            'in_range': in_range,
            'range_text': range_text,
            'trader_view_summary': trader_view_summary
        }

    def _adjust_prediction(
        self,
        night_data: Dict,
        settlement_prediction: Dict,
        night_analysis: Dict,
        consistency_analysis: Dict
    ) -> Dict:
        """根據夜盤資料調整預測區間"""

        original_range = settlement_prediction.get('predicted_range', [0, 0])
        original_lower = original_range[0]
        original_upper = original_range[1]

        night_close = night_data.get('close', (original_lower + original_upper) / 2)
        night_amplitude = night_data.get('amplitude', 100)

        # 調整邏輯
        # 1. 如果夜盤收盤已超出原預測區間，以夜盤收盤為新中心
        # 2. 根據夜盤震幅調整區間大小
        # 3. 根據趨勢一致性調整偏移

        adjustment = 0
        if not consistency_analysis.get('in_range', True):
            # 夜盤已超出區間，需要較大調整
            if night_close < original_lower:
                adjustment = night_close - original_lower - 50  # 向下調整
            else:
                adjustment = night_close - original_upper + 50  # 向上調整
        else:
            # 夜盤在區間內，根據趨勢微調
            if night_analysis['trend'] == 'bullish':
                adjustment = min(night_data.get('change', 0) * 0.5, 50)
            elif night_analysis['trend'] == 'bearish':
                adjustment = max(night_data.get('change', 0) * 0.5, -50)

        # 應用調整
        new_lower = original_lower + adjustment
        new_upper = original_upper + adjustment

        # 根據夜盤震幅調整區間寬度
        if night_analysis['amplitude_level'] == 'high':
            # 高震幅日，擴大預測區間
            range_expansion = 30
            new_lower -= range_expansion
            new_upper += range_expansion
        elif night_analysis['amplitude_level'] == 'low':
            # 低震幅日，收窄預測區間
            range_contraction = 20
            new_lower += range_contraction
            new_upper -= range_contraction

        # 更新趨勢判斷
        if adjustment > 30:
            new_trend = 'bullish'
            new_trend_text = '偏多調整'
        elif adjustment < -30:
            new_trend = 'bearish'
            new_trend_text = '偏空調整'
        else:
            new_trend = settlement_prediction.get('overall_trend', 'neutral')
            new_trend_text = '維持原判斷'

        return {
            'original_range': original_range,
            'adjusted_range': [int(new_lower), int(new_upper)],
            'adjustment': int(adjustment),
            'new_trend': new_trend,
            'new_trend_text': new_trend_text,
            'confidence': self._calculate_confidence(consistency_analysis, night_analysis)
        }

    def _calculate_confidence(self, consistency_analysis: Dict, night_analysis: Dict) -> str:
        """計算預測信心度"""
        score = 3  # 基礎分數（中等）

        # 一致性加分
        if consistency_analysis['consistency'] == 'aligned':
            score += 1
        elif consistency_analysis['consistency'] == 'diverged':
            score -= 1

        # 在區間內加分
        if consistency_analysis.get('in_range', True):
            score += 1

        # 低震幅通常更可預測
        if night_analysis['amplitude_level'] == 'low':
            score += 1
        elif night_analysis['amplitude_level'] == 'high':
            score -= 1

        # 轉換為文字
        if score >= 5:
            return '高'
        elif score >= 3:
            return '中'
        else:
            return '低'

    def _generate_opening_strategy(
        self,
        night_analysis: Dict,
        consistency_analysis: Dict,
        adjusted_prediction: Dict
    ) -> Dict:
        """生成開盤策略建議"""

        strategies = []
        risk_warnings = []

        adjusted_range = adjusted_prediction['adjusted_range']
        mid_point = (adjusted_range[0] + adjusted_range[1]) // 2

        # 根據趨勢生成策略
        if adjusted_prediction['new_trend'] == 'bullish':
            strategies.append({
                'action': '偏多操作',
                'entry': f'開盤若回測 {adjusted_range[0]:,} 附近可考慮做多',
                'target': f'目標 {mid_point:,} ~ {adjusted_range[1]:,}',
                'stop': f'停損設在 {adjusted_range[0] - 50:,}'
            })
        elif adjusted_prediction['new_trend'] == 'bearish':
            strategies.append({
                'action': '偏空操作',
                'entry': f'開盤若反彈 {adjusted_range[1]:,} 附近可考慮做空',
                'target': f'目標 {mid_point:,} ~ {adjusted_range[0]:,}',
                'stop': f'停損設在 {adjusted_range[1] + 50:,}'
            })
        else:
            strategies.append({
                'action': '區間操作',
                'entry': f'區間下緣 {adjusted_range[0]:,} 做多，上緣 {adjusted_range[1]:,} 做空',
                'target': f'目標區間中點 {mid_point:,}',
                'stop': '突破區間則停損反手'
            })

        # 風險警示
        if consistency_analysis['consistency'] == 'diverged':
            risk_warnings.append('⚠️ 夜盤走勢與原預測背離，注意趨勢可能反轉')

        if night_analysis['amplitude_level'] == 'high':
            risk_warnings.append('⚠️ 夜盤高震幅，今日波動可能較大')

        if not consistency_analysis.get('in_range', True):
            risk_warnings.append('⚠️ 夜盤已突破原預測區間，需密切關注')

        return {
            'strategies': strategies,
            'risk_warnings': risk_warnings,
            'key_levels': {
                'support': adjusted_range[0],
                'resistance': adjusted_range[1],
                'pivot': mid_point
            }
        }

    def _generate_analysis_text(
        self,
        night_data: Dict,
        night_analysis: Dict,
        consistency_analysis: Dict,
        adjusted_prediction: Dict,
        strategy: Dict
    ) -> str:
        """生成綜合分析文字"""

        lines = []

        # 夜盤摘要
        lines.append(f"【夜盤概況】")
        lines.append(f"夜盤收盤 {night_data.get('close', 0):,.0f}，"
                     f"震幅 {night_data.get('amplitude', 0):,.0f} 點（{night_analysis['amplitude_text']}），"
                     f"{night_analysis['trend_text']}，{night_analysis['close_position']}。")
        lines.append("")

        # 一致性分析
        lines.append(f"【與前日預測比較】")
        lines.append(f"{consistency_analysis['consistency_text']}。")
        lines.append(f"{consistency_analysis['range_text']}。")
        lines.append("")

        # 調整後預測
        lines.append(f"【盤前預測調整】")
        original = adjusted_prediction['original_range']
        adjusted = adjusted_prediction['adjusted_range']
        adj = adjusted_prediction['adjustment']

        if adj != 0:
            direction = '上調' if adj > 0 else '下調'
            lines.append(f"原預測區間 {original[0]:,} ~ {original[1]:,}，"
                         f"根據夜盤走勢{direction} {abs(adj)} 點。")
        lines.append(f"**調整後預測區間：{adjusted[0]:,} ~ {adjusted[1]:,}**")
        lines.append(f"預測信心度：{adjusted_prediction['confidence']}")
        lines.append("")

        # 操作策略
        lines.append(f"【開盤策略建議】")
        for s in strategy['strategies']:
            lines.append(f"• {s['action']}：{s['entry']}")
            lines.append(f"  目標：{s['target']}")
            lines.append(f"  停損：{s['stop']}")
        lines.append("")

        # 風險警示
        if strategy['risk_warnings']:
            lines.append(f"【風險提示】")
            for warning in strategy['risk_warnings']:
                lines.append(warning)

        return '\n'.join(lines)

    def _save_prediction(self, settlement_date: str, prediction: Dict):
        """保存預測記錄"""
        file_path = self.data_dir / f'premarket_prediction_{settlement_date}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(prediction, f, ensure_ascii=False, indent=2)
        logger.info(f"盤前預測已保存: {file_path}")

    def load_prediction(self, settlement_date: str) -> Optional[Dict]:
        """載入預測記錄"""
        file_path = self.data_dir / f'premarket_prediction_{settlement_date}.json'
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # 測試盤前預測
    predictor = AIPremarketPrediction()

    # 模擬數據
    night_data = {
        'date': '20260115',
        'open': 30800,
        'high': 30900,
        'low': 30750,
        'close': 30850,
        'amplitude': 150,
        'amplitude_pct': 0.49,
        'change': 50,
        'change_pct': 0.16,
        'source': '測試數據'
    }

    settlement_pred = {
        'overall_trend': 'neutral',
        'predicted_range': [30700, 30900],
        'current_price': 30800
    }

    result = predictor.generate_premarket_prediction(
        night_session_data=night_data,
        previous_trader_analysis=None,
        settlement_prediction=settlement_pred,
        settlement_date='20260116'
    )

    print("\n" + "=" * 60)
    print("盤前預測結果")
    print("=" * 60)
    print(result['analysis_text'])
