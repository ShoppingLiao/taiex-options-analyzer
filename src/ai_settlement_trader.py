"""
結算日 AI 交易員分析器
提供第一人稱視角的結算日交易策略與風險評估
"""

from typing import Dict, List
from .settlement_predictor import SettlementPrediction
from .ai_learning_system import AILearningSystem


class AISettlementTrader:
    """結算日 AI 交易員分析器"""
    
    def __init__(self):
        self.learning_system = AILearningSystem()
        self.experience_level, self.level_icon = self.learning_system.get_experience_level()
    
    def analyze_settlement(self, prediction: SettlementPrediction) -> Dict:
        """
        分析結算日並提供第一人稱視角的策略
        
        Args:
            prediction: 結算預測結果
            
        Returns:
            包含 AI 交易員分析的字典
        """
        # 獲取歷史背景（針對結算日）
        historical_context = self._get_settlement_context(prediction)
        
        # 生成第一人稱分析
        analysis = {
            # 經驗等級
            'experience_level': self.experience_level,
            'level_icon': self.level_icon,
            'learning_summary': self.learning_system.generate_learning_summary(),
            
            # 結算日看法（第一人稱）
            'settlement_outlook': self._generate_settlement_outlook(prediction, historical_context),
            
            # 結算日策略（第一人稱）
            'settlement_strategy': self._generate_settlement_strategy(prediction, historical_context),
            
            # 風險評估（第一人稱）
            'settlement_risks': self._generate_settlement_risks(prediction, historical_context),
            
            # 執行計劃（第一人稱）
            'execution_plan': self._generate_execution_plan(prediction, historical_context),
            
            # 歷史洞察
            'historical_insights': historical_context.get('learned_insights', []),
            'similar_cases': len(historical_context.get('similar_situations', [])),
        }
        
        return analysis
    
    def _get_settlement_context(self, prediction: SettlementPrediction) -> Dict:
        """獲取結算日歷史背景"""
        context = {
            'similar_situations': [],
            'learned_insights': [],
            'risk_warnings': []
        }
        
        # 從學習系統中尋找相似的結算日記錄
        for record in self.learning_system.records[-20:]:  # 最近 20 筆
            # 這裡可以根據實際情況擴展匹配邏輯
            if 'settlement' in record.date or '結算' in record.market_observation:
                context['similar_situations'].append({
                    'date': record.date,
                    'outcome': record.prediction_accuracy or '未驗證',
                    'lesson': record.lessons_learned or '無'
                })
        
        # 結算日特定洞察
        if prediction.trend_strength >= 4:
            context['learned_insights'].append("強勢趨勢的結算日，方向通常不會輕易改變")
        
        if prediction.overall_trend == 'neutral':
            context['learned_insights'].append("趨勢不明的結算日最難操作，觀望往往是最好的選擇")
        
        # 風險警告
        context['risk_warnings'].append("結算日最後 30 分鐘波動最劇烈")
        context['risk_warnings'].append("大額未平倉部位可能導致逼倉行情")
        
        return context
    
    def _generate_settlement_outlook(
        self,
        prediction: SettlementPrediction,
        context: Dict
    ) -> str:
        """生成結算日看法（第一人稱）"""
        parts = []
        
        # 開場白
        weekday_text = '週三' if prediction.settlement_weekday == 'wednesday' else '週五'
        parts.append(f"這次是 {prediction.settlement_date} ({weekday_text}) 的結算日，我已經仔細研究了過去幾天的盤勢。")
        
        # 趨勢觀察
        if prediction.overall_trend == 'bullish':
            parts.append(
                f"\n從技術面來看，多方氣勢明顯，趨勢強度達到 {prediction.trend_strength} 顆星。"
                f"這種情況下，我傾向於認為結算價會落在 {prediction.predicted_range[0]:,} 到 {prediction.predicted_range[1]:,} 這個區間。"
            )
        elif prediction.overall_trend == 'bearish':
            parts.append(
                f"\n空方力道不容小覷，趨勢強度 {prediction.trend_strength} 顆星告訴我市場偏空。"
                f"我預估結算價大概率會在 {prediction.predicted_range[0]:,} 到 {prediction.predicted_range[1]:,} 之間。"
            )
        else:
            parts.append(
                f"\n說實話，這次的盤勢讓我有點拿不定主意。多空力道拉鋸，"
                f"結算價可能在 {prediction.predicted_range[0]:,} 到 {prediction.predicted_range[1]:,} 這個範圍內震盪。"
            )
        
        # 關鍵價位觀察
        if prediction.key_metrics.get('max_pain'):
            max_pain = prediction.key_metrics['max_pain']
            parts.append(
                f"\n我特別注意到最大痛苦點在 {max_pain:,}，這是莊家最想要的結算價格。"
                "根據我的經驗，實際結算價常常會往這個方向靠攏。"
            )
        
        # 歷史參考
        if context.get('similar_situations'):
            parts.append(
                f"\n翻看我的交易日誌，發現過去有 {len(context['similar_situations'])} 次類似的結算日情境。"
                "這些經驗告訴我，結算日最忌諱的就是過度自信。"
            )
        
        # 市場情緒
        parts.append(
            "\n從選擇權的未平倉分布來看，大戶的布局已經很明顯了。"
            "我會緊盯這些關鍵價位，看看莊家會不會有什麼動作。"
        )
        
        return "\n".join(parts)
    
    def _generate_settlement_strategy(
        self,
        prediction: SettlementPrediction,
        context: Dict
    ) -> str:
        """生成結算日策略（第一人稱）"""
        parts = []
        
        # 策略總方針
        if prediction.overall_trend == 'bullish' and prediction.trend_strength >= 3:
            parts.append("🟢 我的策略偏向做多")
            parts.append(
                f"\n多方策略：\n"
                f"• 如果價格回測到 {int(prediction.predicted_range[0] * 0.998):,} 附近，我會考慮進場\n"
                f"• 目標設定在預測區間上緣 {prediction.predicted_range[1]:,}\n"
                f"• 停損點嚴格設在 {int(prediction.predicted_range[0] * 0.995):,}，絕不讓虧損擴大"
            )
        elif prediction.overall_trend == 'bearish' and prediction.trend_strength >= 3:
            parts.append("🔴 我的策略偏向做空")
            parts.append(
                f"\n空方策略：\n"
                f"• 反彈到 {int(prediction.predicted_range[1] * 1.002):,} 附近時，考慮進場做空\n"
                f"• 目標設定在預測區間下緣 {prediction.predicted_range[0]:,}\n"
                f"• 停損點設在 {int(prediction.predicted_range[1] * 1.005):,}，控制風險"
            )
        else:
            parts.append("⚪ 這次我選擇觀望為主")
            parts.append(
                f"\n觀望策略：\n"
                f"• 方向不明確時，我不會強行進場\n"
                f"• 如果真要做，考慮賣出價差策略，收取權利金\n"
                f"• 保留大部分現金，等待更好的機會"
            )
        
        # 結算日特殊考量
        parts.append(
            f"\n\n結算日特別注意事項：\n"
            f"• 早盤不急著進場，先觀察 30 分鐘看方向\n"
            f"• 中場（11:00-12:30）如果突破關鍵價位，可以跟進\n"
            f"• 尾盤最後 30 分鐘，我會減少操作，避免被巨量掃到"
        )
        
        # 部位管理
        parts.append(
            f"\n部位管理原則：\n"
            f"• 結算日我只會用平常 50% 的部位\n"
            f"• 分批進場，絕不一次 all-in\n"
            f"• 隨時準備認賠出場，不跟市場硬拗"
        )
        
        return "\n".join(parts)
    
    def _generate_settlement_risks(
        self,
        prediction: SettlementPrediction,
        context: Dict
    ) -> str:
        """生成結算日風險評估（第一人稱）"""
        parts = []
        
        # 風險等級評估
        if prediction.trend_strength <= 2:
            risk_level = "極高"
            parts.append(f"⚠️ 風險等級：{risk_level}")
            parts.append(
                "趨勢不明的結算日最危險！多空雙方都有機會，但也意味著隨時可能反轉。"
                "這種時候我最擔心的就是被來回掃損。"
            )
        elif prediction.trend_strength == 3:
            risk_level = "中高"
            parts.append(f"⚠️ 風險等級：{risk_level}")
            parts.append(
                "趨勢雖然有方向，但力道還不夠強。我會保持警戒，"
                "因為結算日什麼事都可能發生。"
            )
        else:
            risk_level = "中"
            parts.append(f"⚠️ 風險等級：{risk_level}")
            parts.append(
                "強勢趨勢讓我比較放心，但結算日的變數還是不能輕忽。"
            )
        
        # 具體風險點
        parts.append("\n我特別擔心這些風險：")
        
        # 從歷史學到的風險
        if context.get('risk_warnings'):
            for warning in context['risk_warnings']:
                parts.append(f"• {warning}")
        
        # 結算日特定風險
        parts.append("• 大戶可能會在最後時刻突襲，拉抬或打壓價格")
        parts.append("• 選擇權到期會造成 Gamma 風險暴增，價格波動加劇")
        parts.append("• 如果我判斷錯誤，結算價偏離預測區間，部位可能大虧")
        
        # 最大擔憂
        if prediction.key_metrics.get('max_pain'):
            max_pain = prediction.key_metrics['max_pain']
            current_price = prediction.key_metrics.get('current_price', 0)
            distance = abs(current_price - max_pain)
            
            if distance > 200:
                parts.append(
                    f"\n❗ 我最擔心的是：目前價格 {current_price:,} 離最大痛苦點 {max_pain:,} 還有 {distance:.0f} 點的距離。"
                    f"如果莊家真的要拉回 Max Pain，我的部位會很痛苦。"
                )
        
        # 流動性風險
        parts.append(
            "\n結算日的流動性風險也不能忽視。如果市場突然沒量，"
            "我可能會被困在部位裡出不來，這是我最不想看到的情況。"
        )
        
        return "\n".join(parts)
    
    def _generate_execution_plan(
        self,
        prediction: SettlementPrediction,
        context: Dict
    ) -> str:
        """生成執行計劃（第一人稱）"""
        parts = []
        
        parts.append("📋 我的結算日時間表：")
        
        # 開盤前
        parts.append(
            "\n🕐 08:30 - 08:45 (開盤前)\n"
            "• 檢查國際盤面，看美股和亞洲其他市場怎麼走\n"
            "• 確認沒有重大消息公布\n"
            "• 最後確認我的進場價位和停損點"
        )
        
        # 早盤
        parts.append(
            "\n🕘 08:45 - 09:30 (早盤)\n"
            "• 觀察開盤後的方向，不急著進場\n"
            "• 注意大單流向，看法人在做什麼\n"
            "• 如果符合我的預期，可以試單進場（小部位）"
        )
        
        # 中場
        parts.append(
            "\n🕚 10:00 - 12:30 (中場)\n"
            "• 這是我可能加碼的時段\n"
            f"• 如果價格突破關鍵價位（{prediction.predicted_range[1]:,} 或 {prediction.predicted_range[0]:,}），跟進\n"
            "• 持續監控部位，該停損就停損"
        )
        
        # 尾盤
        parts.append(
            "\n🕐 13:00 - 13:30 (尾盤前)\n"
            "• 評估部位狀況，決定是否提前了結\n"
            "• 如果已經獲利，我會考慮落袋為安\n"
            "• 如果還在虧損，也要準備認賠"
        )
        
        # 最後30分鐘
        parts.append(
            "\n🕜 13:15 - 13:45 (最後 30 分鐘)\n"
            "• ⚡ 關鍵時刻！波動最大的時候\n"
            "• 我會極度謹慎，避免新開倉位\n"
            "• 緊盯部位，隨時準備平倉\n"
            "• 絕對不跟市場對賭，順勢而為"
        )
        
        # 結算後
        parts.append(
            "\n🕑 13:45 之後 (結算後)\n"
            "• 檢討今天的操作，記錄心得\n"
            "• 不管賺賠，都要寫下來供日後參考\n"
            "• 放鬆心情，準備下一個交易日"
        )
        
        # 應變方案
        parts.append(
            "\n🚨 緊急應變：\n"
            "• 如果盤中出現異常巨量：立即檢視部位，必要時先出場觀望\n"
            "• 如果價格急劇偏離預測區間：承認判斷錯誤，果斷停損\n"
            "• 如果系統出問題無法下單：事先準備好電話下單的方式"
        )
        
        # 心態調整
        parts.append(
            "\n💭 心態提醒：\n"
            "• 結算日不是賭博，是機率遊戲\n"
            "• 保護本金比賺錢更重要\n"
            "• 如果今天沒有好機會，寧可不做\n"
            "• 市場永遠都在，不急於一時"
        )
        
        return "\n".join(parts)
