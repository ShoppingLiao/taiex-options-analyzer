"""
每日報告的第一人稱 AI 交易員分析
結合學習系統，提供個人化的市場洞察
"""

from typing import Dict, List
from .parser import OptionsData
from .analyzer import AnalysisResult
from .ai_learning_system import AILearningSystem, AnalysisRecord


class AIDailyAnalyzer:
    """每日報告的 AI 交易員分析器"""
    
    def __init__(self):
        self.learning_system = AILearningSystem()
        self.experience_level, self.level_icon = self.learning_system.get_experience_level()
    
    def analyze(
        self,
        analysis_result: AnalysisResult,
        options_data: OptionsData,
        sentiment: str
    ) -> Dict:
        """
        進行第一人稱 AI 交易員分析
        
        Args:
            analysis_result: 技術分析結果
            options_data: 選擇權原始數據
            sentiment: 市場情緒
            
        Returns:
            包含 AI 分析的字典
        """
        pc_ratio = analysis_result.pc_ratio_oi
        close_price = options_data.tx_close or 0  # 使用台指期貨收盤價
        
        # 獲取歷史背景
        historical_context = self.learning_system.get_historical_context(pc_ratio, sentiment)
        
        # 判斷趨勢信號
        trend_signal = self._determine_trend(analysis_result, options_data)
        
        # 生成第一人稱分析
        ai_analysis = {
            # 經驗等級
            'experience_level': self.experience_level,
            'level_icon': self.level_icon,
            'learning_summary': self.learning_system.generate_learning_summary(),
            
            # 市場觀察（第一人稱）
            'market_observation': self._generate_market_observation(
                analysis_result, options_data, sentiment, historical_context
            ),
            
            # 部位策略（第一人稱）
            'position_strategy': self._generate_position_strategy(
                analysis_result, options_data, sentiment, trend_signal
            ),
            
            # 風險評估（第一人稱）
            'risk_assessment': self._generate_risk_assessment(
                analysis_result, options_data, sentiment, historical_context
            ),
            
            # 交易計劃（第一人稱）
            'trading_plan': self._generate_trading_plan(
                analysis_result, options_data, sentiment, trend_signal
            ),
            
            # 歷史參考
            'historical_insights': historical_context.get('learned_insights', []),
            'similar_cases': len(historical_context.get('similar_situations', [])),
            
            # 關鍵數據
            'key_data': {
                'close_price': close_price,
                'pc_ratio': round(pc_ratio, 3),
                'sentiment': sentiment,
                'trend_signal': trend_signal,
                'max_call_oi': max(options_data.call_oi),
                'max_put_oi': max(options_data.put_oi),
            }
        }
        
        # 記錄這次分析（用於未來學習）
        self._save_analysis_record(
            analysis_result, options_data, sentiment, trend_signal, ai_analysis
        )
        
        return ai_analysis
    
    def _determine_trend(self, analysis_result: AnalysisResult, options_data: OptionsData) -> str:
        """判斷趨勢信號"""
        pc_ratio = analysis_result.pc_ratio_oi
        
        # 綜合判斷
        if pc_ratio < 0.8:
            return 'bullish'
        elif pc_ratio > 1.2:
            return 'bearish'
        else:
            # 看 OI 變化
            total_call_change = sum(options_data.call_oi_change)
            total_put_change = sum(options_data.put_oi_change)
            
            if total_call_change > total_put_change * 1.5:
                return 'bullish'
            elif total_put_change > total_call_change * 1.5:
                return 'bearish'
            else:
                return 'neutral'
    
    def _generate_market_observation(
        self,
        analysis_result: AnalysisResult,
        options_data: OptionsData,
        sentiment: str,
        context: Dict
    ) -> str:
        """生成市場觀察（第一人稱）"""
        pc_ratio = analysis_result.pc_ratio_oi
        close_price = options_data.tx_close or 0
        
        observations = []
        
        # 開場白
        observations.append(f"今天收盤價在 {close_price:,} 點，我仔細觀察了選擇權市場的布局。")
        
        # PC Ratio 觀察
        if pc_ratio < 0.7:
            observations.append(
                f"PC Ratio 只有 {pc_ratio:.3f}，市場明顯偏多，但我必須警惕——"
                "當大家都太樂觀時，往往就是該謹慎的時候。"
            )
        elif pc_ratio > 1.3:
            observations.append(
                f"PC Ratio 高達 {pc_ratio:.3f}，Put 的未平倉量明顯大於 Call，"
                "市場充滿恐慌。不過根據我的經驗，極度悲觀反而可能是轉機。"
            )
        else:
            observations.append(
                f"PC Ratio 在 {pc_ratio:.3f}，相對均衡。這種時候我會更依賴"
                "價格行為和成交量的變化來判斷方向。"
            )
        
        # 大量 OI 集中點
        max_call_strike = options_data.strike_prices[options_data.call_oi.index(max(options_data.call_oi))]
        max_put_strike = options_data.strike_prices[options_data.put_oi.index(max(options_data.put_oi))]
        
        observations.append(
            f"我注意到最大的 Call OI 在 {max_call_strike:,} 點，"
            f"而 Put OI 則集中在 {max_put_strike:,} 點。"
        )
        
        if abs(max_call_strike - close_price) < 200:
            observations.append("Call 方的壓力就在眼前，短線要突破不容易。")
        
        if abs(max_put_strike - close_price) < 200:
            observations.append("Put 方的支撐也很近，下檔有人護盤。")
        
        # 歷史經驗
        if context.get('learned_insights'):
            observations.append(f"\n根據我過去的經驗：{context['learned_insights'][0]}")
        
        return "\n\n".join(observations)
    
    def _generate_position_strategy(
        self,
        analysis_result: AnalysisResult,
        options_data: OptionsData,
        sentiment: str,
        trend_signal: str
    ) -> str:
        """生成部位策略（第一人稱）"""
        close_price = options_data.tx_close or 0
        pc_ratio = analysis_result.pc_ratio_oi
        
        strategies = []
        
        # 根據趨勢信號
        if trend_signal == 'bullish':
            strategies.append("我目前偏向做多，但不會盲目追高。")
            strategies.append(
                f"如果價格回測到 {int(close_price * 0.995):,} 附近，"
                "我會考慮買進 Call 或賣出 Put，設定停損在 {int(close_price * 0.99):,}。"
            )
        elif trend_signal == 'bearish':
            strategies.append("我認為下檔風險較高，會採取防守姿態。")
            strategies.append(
                f"反彈到 {int(close_price * 1.005):,} 附近時，"
                "我可能會買進 Put 來對沖，或者賣出 Call 賺取權利金。"
            )
        else:
            strategies.append("目前方向不明，我選擇觀望或做價差策略。")
            strategies.append(
                f"可以考慮賣出 {int(close_price - 200):,} 的 Put 和 "
                f"{int(close_price + 200):,} 的 Call，收取雙邊權利金。"
            )
        
        # 部位管理
        if pc_ratio < 0.7 or pc_ratio > 1.3:
            strategies.append(
                "\n由於市場情緒偏極端，我會把部位控制在平常的 60-70%，"
                "留更多現金應對可能的劇烈波動。"
            )
        else:
            strategies.append(
                "\n市場相對理性，我可以維持正常的部位大小，"
                "但仍會保留 30% 現金靈活調整。"
            )
        
        return "\n\n".join(strategies)
    
    def _generate_risk_assessment(
        self,
        analysis_result: AnalysisResult,
        options_data: OptionsData,
        sentiment: str,
        context: Dict
    ) -> str:
        """生成風險評估（第一人稱）"""
        risks = []
        
        # 風險等級
        if sentiment in ['extremely_bullish', 'extremely_bearish']:
            risk_level = "高"
            risks.append(f"⚠️ 風險等級：{risk_level}")
            risks.append(
                "市場情緒已經到極端，這是我最警惕的時候。"
                "歷史告訴我，極端情緒後常伴隨急速反轉。"
            )
        elif sentiment in ['bullish', 'bearish']:
            risk_level = "中"
            risks.append(f"⚠️ 風險等級：{risk_level}")
            risks.append("市場有方向但還不算極端，我會保持警覺但不過度恐慌。")
        else:
            risk_level = "低至中"
            risks.append(f"⚠️ 風險等級：{risk_level}")
            risks.append("目前風險相對可控，但市場隨時可能改變性格。")
        
        # 具體風險點
        risks.append("\n我特別關注以下風險：")
        
        # 從歷史學到的風險
        if context.get('risk_warnings'):
            for warning in context['risk_warnings']:
                risks.append(f"• {warning}")
        
        # OI 風險
        max_call_oi = max(options_data.call_oi)
        max_put_oi = max(options_data.put_oi)
        
        if max_call_oi > max_put_oi * 1.5:
            risks.append("• Call OI 過度集中，價格接近時可能引發劇烈調整")
        elif max_put_oi > max_call_oi * 1.5:
            risks.append("• Put OI 過度集中，跌破支撐可能加速下殺")
        
        # 流動性風險
        total_volume = sum(options_data.call_volume) + sum(options_data.put_volume)
        total_oi = sum(options_data.call_oi) + sum(options_data.put_oi)
        
        if total_volume < total_oi * 0.1:
            risks.append("• 今天成交量偏低，流動性不佳可能導致價格跳動")
        
        return "\n".join(risks)
    
    def _generate_trading_plan(
        self,
        analysis_result: AnalysisResult,
        options_data: OptionsData,
        sentiment: str,
        trend_signal: str
    ) -> str:
        """生成交易計劃（第一人稱）"""
        close_price = options_data.tx_close or 0
        
        plans = []
        plans.append("📋 我的明日交易計劃：")
        
        # 進場點
        if trend_signal == 'bullish':
            entry = int(close_price * 0.998)
            target = int(close_price * 1.01)
            stop = int(close_price * 0.992)
            
            plans.append(f"\n多方布局：")
            plans.append(f"• 進場點：{entry:,} 附近（回測進場）")
            plans.append(f"• 目標價：{target:,}（獲利 1%）")
            plans.append(f"• 停損點：{stop:,}（風險控制 0.8%）")
            
        elif trend_signal == 'bearish':
            entry = int(close_price * 1.002)
            target = int(close_price * 0.99)
            stop = int(close_price * 1.008)
            
            plans.append(f"\n空方布局：")
            plans.append(f"• 進場點：{entry:,} 附近（反彈進場）")
            plans.append(f"• 目標價：{target:,}（獲利 1%）")
            plans.append(f"• 停損點：{stop:,}（風險控制 0.8%）")
            
        else:
            plans.append(f"\n觀望策略：")
            plans.append(f"• 等待明確信號，不急著進場")
            plans.append(f"• 若突破 {int(close_price * 1.005):,}，考慮做多")
            plans.append(f"• 若跌破 {int(close_price * 0.995):,}，考慮做空")
        
        # 倉位管理
        plans.append(f"\n倉位管理：")
        if sentiment in ['extremely_bullish', 'extremely_bearish']:
            plans.append("• 降低倉位至 50-60%，保留大量現金")
            plans.append("• 分批進場，不一次性 all-in")
        else:
            plans.append("• 維持 70-80% 倉位")
            plans.append("• 保留 20-30% 靈活資金")
        
        # 應變計劃
        plans.append(f"\n應變方案：")
        plans.append("• 如果盤中出現異常大量，立即檢視部位")
        plans.append("• 重大消息公布前，減少暴險部位")
        plans.append("• 每天收盤後檢討，持續優化策略")
        
        return "\n".join(plans)
    
    def _save_analysis_record(
        self,
        analysis_result: AnalysisResult,
        options_data: OptionsData,
        sentiment: str,
        trend_signal: str,
        ai_analysis: Dict
    ):
        """儲存分析記錄供未來學習"""
        record = AnalysisRecord(
            date=analysis_result.date,
            close_price=options_data.tx_close or 0,
            pc_ratio=analysis_result.pc_ratio_oi,
            sentiment=sentiment,
            trend_signal=trend_signal,
            market_observation=ai_analysis['market_observation'],
            position_strategy=ai_analysis['position_strategy'],
            risk_assessment=ai_analysis['risk_assessment'],
            trading_plan=ai_analysis['trading_plan']
        )
        
        self.learning_system.add_record(record)
