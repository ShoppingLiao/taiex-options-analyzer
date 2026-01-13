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
        """生成結算日看法（第一人稱）- 組合單交易員視角"""
        parts = []
        
        # 開場白 - 強調組合單交易員身份
        weekday_text = '週三' if prediction.settlement_weekday == 'wednesday' else '週五'
        parts.append(
            f"又到了 {weekday_text} 結算日，這是我一週中最重要的交易日！"
            f"今天是 {prediction.settlement_date}，我已經準備好用組合單策略來操作這次結算。"
        )
        
        # 為什麼專注結算日
        parts.append(
            "\n作為一個專注於結算日組合單的交易員，我只在週三和週五進場。"
            "這兩天的選擇權會在 13:30 自動結算歸零，讓我能精準掌握進出時機，"
            "不用擔心隔夜留倉的風險。我花了整週時間研究盤勢，就是為了今天的這一刻。"
        )
        
        # 趨勢觀察與組合單選擇
        if prediction.overall_trend == 'bullish':
            parts.append(
                f"\n從這週的數據來看，多方氣勢明顯，趨勢強度達到 {prediction.trend_strength} 顆星。"
                f"這種情況下，我會使用「多方價差組合（Bull Call Spread）」，"
                f"買進較低履約價的 Call，同時賣出較高履約價的 Call。"
                f"我預期結算價會落在 {prediction.predicted_range[0]:,} 到 {prediction.predicted_range[1]:,} 之間。"
            )
            parts.append(
                "\n這個組合的好處是：成本有限（買賣相抵），獲利潛力明確（價差），"
                "而且如果判斷錯誤，最大虧損就是淨權利金，不會無限擴大。"
            )
        elif prediction.overall_trend == 'bearish':
            parts.append(
                f"\n這週的盤勢顯示空方力道不容小覷，趨勢強度 {prediction.trend_strength} 顆星告訴我市場偏空。"
                f"我會採用「空方價差組合（Bear Put Spread）」，"
                f"買進較高履約價的 Put，同時賣出較低履約價的 Put。"
                f"我預估結算價大概率會在 {prediction.predicted_range[0]:,} 到 {prediction.predicted_range[1]:,} 之間。"
            )
            parts.append(
                "\n空方價差組合讓我能在看跌的行情中獲利，同時透過賣出低履約價 Put 來降低成本，"
                "提高整體勝率。就算方向判斷有誤，虧損也有上限。"
            )
        else:
            parts.append(
                f"\n說實話，這次的盤勢讓我有點難以判斷。多空力道拉鋸（趨勢強度 {prediction.trend_strength} 顆星），"
                f"結算價可能在 {prediction.predicted_range[0]:,} 到 {prediction.predicted_range[1]:,} 這個範圍內震盪。"
            )
            parts.append(
                "\n方向不明時，我會改用「鐵禿鷹組合（Iron Condor）」—— 同時建立 Call 和 Put 的價差組合，"
                "收取雙邊的權利金。只要結算價落在我設定的區間內，就能獲利。"
                "這是趨勢不明時，我最喜歡用的策略。"
            )
        
        # 關鍵價位觀察 - 從組合單角度
        if prediction.key_metrics.get('max_pain'):
            max_pain = prediction.key_metrics['max_pain']
            parts.append(
                f"\n我特別注意到最大痛苦點（Max Pain）在 {max_pain:,}。"
                "這是莊家最希望的結算價，因為在這個價位，選擇權買方的總虧損最大。"
                "根據我的經驗，實際結算價常常會被拉往這個方向。"
                "所以我在設計組合單時，會把這個價位納入考量。"
            )
        
        # 組合單的時間優勢
        parts.append(
            "\n結算日的時間價值（Time Decay）對我來說是最大優勢。"
            "隨著時間接近 13:30，選擇權的時間價值會快速歸零，只剩下內含價值。"
            "這代表如果我的方向判斷正確，組合單的價值會快速朝有利方向移動。"
        )
        
        # 歷史參考
        if context.get('similar_situations'):
            parts.append(
                f"\n翻看我的交易日誌，我發現過去有 {len(context['similar_situations'])} 次類似的結算日情境。"
                "這些寶貴的經驗告訴我：在結算日操作組合單，最重要的是紀律和耐心。"
                "不要因為一時的波動就改變策略，相信自己的分析和計劃。"
            )
        
        # 今天的準備狀態
        parts.append(
            "\n我已經做好充分準備：\n"
            "• 確認了要使用的組合單策略\n"
            "• 選擇了流動性充足的履約價\n"
            "• 計算好最大獲利和最大虧損\n"
            "• 設定了獲利 60% 和虧損 50% 的出場點\n"
            "• 準備好券商的「組合單下單」功能"
        )
        
        # 結語
        parts.append(
            f"\n{weekday_text}結算日，讓我們用專業的態度迎接挑戰。"
            "組合單給了我明確的風險收益比，剩下的就是耐心等待市場給我答案。"
        )
        
        return "\n".join(parts)
    
    def _generate_settlement_strategy(
        self,
        prediction: SettlementPrediction,
        context: Dict
    ) -> str:
        """生成結算日策略（第一人稱）- 組合單當沖策略"""
        parts = []
        
        # 計算關鍵價位
        predicted_center = (prediction.predicted_range[0] + prediction.predicted_range[1]) / 2
        current_price = prediction.key_metrics.get('current_price', predicted_center)
        max_pain = prediction.key_metrics.get('max_pain', predicted_center)
        
        # 策略總方針 - 組合單當沖
        parts.append("🎯 我的核心策略：結算日組合單當沖")
        parts.append(
            "\n作為一個專注於結算日操作的交易員，我只在週三和週五進行選擇權組合單交易。"
            "我的目標很明確：利用結算機制，透過組合單賺取價差利潤，當日結算自動平倉。"
        )
        
        # 根據趨勢選擇組合單策略
        if prediction.overall_trend == 'bullish' and prediction.trend_strength >= 3:
            parts.append("\n� 這次我會使用：多方價差組合（Bull Call Spread）")
            parts.append(
                f"\n組合單結構：\n"
                f"• 買進 Call {int(predicted_center - 100):,}（付權利金）\n"
                f"• 賣出 Call {int(predicted_center + 100):,}（收權利金）\n"
                f"• 最大獲利：當結算價 ≥ {int(predicted_center + 100):,} 時，賺取價差 200 點\n"
                f"• 最大虧損：當結算價 ≤ {int(predicted_center - 100):,} 時，損失淨權利金\n"
                f"• 損益兩平點：{int(predicted_center - 100):,} + 淨權利金"
            )
            parts.append(
                f"\n為什麼選這個組合？\n"
                f"• 趨勢偏多（{prediction.trend_strength} 顆星），我看好突破 {prediction.predicted_range[1]:,}\n"
                f"• 賣出高履約價 Call 降低成本，就算沒漲那麼多也能獲利\n"
                f"• 風險有限，最大虧損就是權利金，不會無限擴大"
            )
            
        elif prediction.overall_trend == 'bearish' and prediction.trend_strength >= 3:
            parts.append("\n� 這次我會使用：空方價差組合（Bear Put Spread）")
            parts.append(
                f"\n組合單結構：\n"
                f"• 買進 Put {int(predicted_center + 100):,}（付權利金）\n"
                f"• 賣出 Put {int(predicted_center - 100):,}（收權利金）\n"
                f"• 最大獲利：當結算價 ≤ {int(predicted_center - 100):,} 時，賺取價差 200 點\n"
                f"• 最大虧損：當結算價 ≥ {int(predicted_center + 100):,} 時，損失淨權利金\n"
                f"• 損益兩平點：{int(predicted_center + 100):,} - 淨權利金"
            )
            parts.append(
                f"\n為什麼選這個組合？\n"
                f"• 趨勢偏空（{prediction.trend_strength} 顆星），我預期跌破 {prediction.predicted_range[0]:,}\n"
                f"• 賣出低履約價 Put 降低成本，提高勝率\n"
                f"• 就算判斷錯誤，虧損也有上限，保護本金"
            )
            
        else:
            parts.append("\n📊 這次我會使用：鐵禿鷹組合（Iron Condor）")
            parts.append(
                f"\n組合單結構（收取權利金策略）：\n"
                f"• 賣出 Call {int(predicted_center + 200):,} + 買進 Call {int(predicted_center + 300):,}\n"
                f"• 賣出 Put {int(predicted_center - 200):,} + 買進 Put {int(predicted_center - 300):,}\n"
                f"• 最大獲利：當結算價在 {int(predicted_center - 200):,} ~ {int(predicted_center + 200):,} 區間，收取全部權利金\n"
                f"• 最大虧損：價格突破任一邊的保護腿（100點 - 淨權利金）"
            )
            parts.append(
                f"\n為什麼選這個組合？\n"
                f"• 趨勢不明確，我預期結算價會在區間震盪\n"
                f"• 收取權利金作為利潤，時間站在我這邊\n"
                f"• 雙邊保護，就算方向錯誤虧損也有限"
            )
        
        # 結算日組合單優勢
        parts.append(
            f"\n\n💡 為什麼專做結算日組合單？\n"
            f"• ⏰ 時間價值歸零：結算日選擇權只剩內含價值，方向對了就賺錢\n"
            f"• 🎯 自動平倉機制：13:30 系統自動結算，不用擔心忘記平倉\n"
            f"• 📊 風險可控：組合單的最大虧損在建倉時就確定了\n"
            f"• 💰 不需留倉：當日沖銷，晚上睡得安穩\n"
            f"• 📈 高勝率策略：根據過往經驗，把握莊家結算價位的規律"
        )
        
        # 進場時機
        parts.append(
            f"\n⏰ 我的進場時機規劃：\n"
            f"• 09:00-09:30：觀察開盤方向，確認趨勢是否符合預期\n"
            f"• 09:30-10:00：如果確認方向，開始建立組合單\n"
            f"• 10:00-12:00：主要操作時段，分批建倉（避免一次進場）\n"
            f"• 12:00-13:00：不再新開倉，專注管理現有部位\n"
            f"• 13:00-13:30：準備迎接結算，必要時提前平倉止盈/止損"
        )
        
        # 部位管理
        parts.append(
            f"\n💼 組合單部位管理原則：\n"
            f"• 單次組合不超過總資金的 30%（避免單一方向風險過大）\n"
            f"• 分 2-3 批建倉，降低進場成本\n"
            f"• 設定獲利目標 60%，達到就提前平倉鎖定利潤\n"
            f"• 如果虧損達 50%，果斷認賠，不跟市場硬拗\n"
            f"• 12:30 前評估部位，決定是否持有到結算"
        )
        
        return "\n".join(parts)
    
    def _generate_settlement_risks(
        self,
        prediction: SettlementPrediction,
        context: Dict
    ) -> str:
        """生成結算日風險評估（第一人稱）- 組合單風險"""
        parts = []
        
        # 風險等級評估
        if prediction.trend_strength <= 2:
            risk_level = "中高"
            parts.append(f"⚠️ 組合單風險等級：{risk_level}")
            parts.append(
                "趨勢不明的結算日，我會選用鐵禿鷹組合。雖然是收取權利金策略，"
                "但最擔心的就是價格突然單邊突破，讓保護腿失效。"
                "不過好在組合單的風險有限，最大虧損在建倉時就知道了。"
            )
        elif prediction.trend_strength == 3:
            risk_level = "中"
            parts.append(f"⚠️ 組合單風險等級：{risk_level}")
            parts.append(
                "趨勢有方向但力道不是很強，我會用價差組合（Bull/Bear Spread）。"
                "這種組合單的好處是，就算方向判斷錯誤，虧損也不會超過淨權利金。"
            )
        else:
            risk_level = "偏低"
            parts.append(f"⚠️ 組合單風險等級：{risk_level}")
            parts.append(
                "強勢趨勢讓我對方向比較有信心，價差組合在這種情況下勝率較高。"
                "只要結算價落在目標區間，就能獲得最大利潤。"
            )
        
        # 組合單特定風險
        parts.append("\n🎯 組合單操作我特別注意這些風險：")
        
        # 價格風險
        predicted_center = (prediction.predicted_range[0] + prediction.predicted_range[1]) / 2
        parts.append(
            f"• 📊 價格風險：如果結算價偏離預測區間 {prediction.predicted_range[0]:,}-{prediction.predicted_range[1]:,}，"
            "組合單可能無法達到最大獲利，甚至虧損"
        )
        
        # 流動性風險
        parts.append(
            "• 💧 流動性風險：結算日最後 30 分鐘，如果想提前平倉，"
            "可能會遇到買賣價差過大，無法以理想價格平倉的情況"
        )
        
        # 執行風險
        parts.append(
            "• ⚡ 執行風險：組合單需要同時成交多個履約價，"
            "如果沒有使用「組合單下單」功能，單腿成交會有巨大風險"
        )
        
        # 時間風險
        parts.append(
            "• ⏰ 時間風險：雖然時間價值歸零對我有利，"
            "但如果太早建倉，中途價格大幅波動也會影響心態"
        )
        
        # 從歷史學到的風險
        parts.append("\n📚 從過往經驗學到的教訓：")
        if context.get('risk_warnings'):
            for warning in context['risk_warnings']:
                parts.append(f"• {warning}")
        
        # 組合單特有風險
        parts.append("• 不要在流動性不足的履約價建立組合單，平倉會很痛苦")
        parts.append("• 最後 15 分鐘不要試圖調整組合，容易造成單腿風險")
        parts.append("• 如果盤中部位虧損超過 50%，要果斷認賠，不要期待奇蹟")
        
        # 最大擔憂 - Max Pain 分析
        if prediction.key_metrics.get('max_pain'):
            max_pain = prediction.key_metrics['max_pain']
            current_price = prediction.key_metrics.get('current_price', 0)
            distance = abs(current_price - max_pain)
            
            if distance > 200:
                parts.append(
                    f"\n❗ 我最擔心的情境：目前價格 {current_price:,} 離最大痛苦點 {max_pain:,} 還有 {distance:.0f} 點。"
                    f"如果莊家真的在最後時刻拉回 Max Pain，我的組合單可能會從獲利變虧損。"
                    f"這就是為什麼我會在 12:30 前評估是否要提前平倉鎖定利潤。"
                )
        
        # 應對措施
        parts.append(
            "\n🛡️ 我的風險控管措施：\n"
            "• 建倉前確認使用「組合單下單」，避免單腿風險\n"
            "• 設定獲利 60% 就平倉，不貪心等到最大利潤\n"
            "• 虧損達 50% 就認賠，保護剩餘本金\n"
            "• 12:30 前決定是否持有到結算，避免最後 30 分鐘的劇烈波動\n"
            "• 絕對不超過總資金 30% 的部位，留足夠現金應對突發狀況"
        )
        
        return "\n".join(parts)
    
    def _generate_execution_plan(
        self,
        prediction: SettlementPrediction,
        context: Dict
    ) -> str:
        """生成執行計劃（第一人稱）- 組合單當沖流程"""
        parts = []
        
        weekday_text = '週三' if prediction.settlement_weekday == 'wednesday' else '週五'
        parts.append(f"📋 我的 {weekday_text} 結算日組合單操作流程：")
        
        # 前一天準備
        parts.append(
            "\n📅 前一天晚上 (D-1)\n"
            "• 複習這週的單日報告，確認趨勢方向和強度\n"
            "• 規劃明天要使用的組合單策略（Bull Spread / Bear Spread / Iron Condor）\n"
            "• 計算預期的最大獲利和最大虧損金額\n"
            "• 設定好獲利目標（60%）和停損點（50%）\n"
            "• 準備好券商的「組合單下單」功能，確認操作流程"
        )
        
        # 開盤前
        parts.append(
            "\n🕐 08:00 - 08:45 (開盤前)\n"
            "• 檢查隔夜美股和亞洲盤表現，確認沒有重大變數\n"
            "• 最後確認組合單的履約價選擇\n"
            "• 檢查這些履約價的流動性（買賣價差、掛單量）\n"
            "• 準備好下單介面，避免開盤後手忙腳亂\n"
            "• 深呼吸，調整心態，提醒自己今天的策略"
        )
        
        # 早盤觀察
        parts.append(
            "\n🕘 08:45 - 09:30 (早盤觀察)\n"
            "• 【不進場】只觀察，看開盤方向是否符合預期\n"
            "• 注意大單流向和選擇權 Put/Call Ratio 變化\n"
            "• 觀察台指期貨的量能和波動幅度\n"
            "• 確認我規劃的組合單履約價是否在合理範圍內\n"
            "• 如果開盤方向與預期相反，重新評估是否要調整策略"
        )
        
        # 建倉時段
        parts.append(
            "\n� 09:30 - 10:30 (第一批建倉)\n"
            "• 如果確認趨勢方向，開始建立第一批組合單（50% 部位）\n"
            "• 使用券商的「組合單下單」功能，確保同時成交\n"
            "• 建倉後立即設定「獲利 60% 平倉」和「虧損 50% 停損」的條件單\n"
            "• 記錄建倉價格和時間，方便後續檢討\n"
            "• 建倉完成後，不要一直盯盤，給組合單一些發酵時間"
        )
        
        # 觀察調整
        parts.append(
            "\n🕚 10:30 - 11:30 (觀察與加碼)\n"
            "• 評估第一批組合單的損益狀況\n"
            "• 如果獲利 20-30%，可考慮建立第二批（剩餘 50% 部位）\n"
            "• 如果虧損超過 30%，開始警戒，準備停損\n"
            "• 持續觀察價格是否朝預期方向移動\n"
            "• 如果流動性變差，不要勉強加碼"
        )
        
        # 午盤管理
        parts.append(
            "\n� 11:30 - 12:30 (部位管理)\n"
            "• 這是關鍵時段，決定是否要持有到結算\n"
            "• 如果已達獲利目標 60%，考慮提前平倉落袋為安\n"
            "• 如果虧損接近 50%，果斷停損，不要等到結算\n"
            "• 如果損益在 ±20% 之間，可考慮續抱到結算\n"
            "• 12:30 前必須做出決定：全部平倉 or 持有到結算"
        )
        
        # 尾盤決策
        parts.append(
            "\n🕐 12:30 - 13:15 (結算前最後決策)\n"
            "• 如果決定持有到結算，就不再調整部位\n"
            "• 評估目前價位與預測結算價的距離\n"
            "• 如果價格突然大幅偏離，考慮緊急平倉\n"
            "• 最後 30 分鐘流動性變差，不建議新的操作\n"
            "• 如果還有部位，緊盯價格但保持冷靜"
        )
        
        # 結算時刻
        parts.append(
            "\n🕜 13:15 - 13:30 (結算倒數)\n"
            "• ⚡ 【關鍵 15 分鐘】組合單即將自動結算\n"
            "• 不要在這時候試圖調整組合，風險太大\n"
            "• 如果持有到這裡，就讓系統自動結算\n"
            "• 深呼吸，接受結果，不管獲利或虧損\n"
            "• 13:30 結算完成，組合單自動平倉"
        )
        
        # 結算後
        parts.append(
            "\n🕑 13:30 之後 (結算後檢討)\n"
            "• 查看最終結算價和實際損益\n"
            "• 記錄今天的操作過程和心得\n"
            "• 分析哪些判斷正確，哪些需要改進\n"
            "• 更新我的學習系統，累積結算日經驗\n"
            "• 不管賺賠，都要感謝市場給我的學習機會"
        )
        
        # 組合單檢查清單
        parts.append(
            "\n✅ 組合單下單檢查清單：\n"
            "□ 確認使用「組合單下單」功能（不是單腿分開下）\n"
            "□ 檢查每個履約價的流動性（成交量 > 100）\n"
            "□ 計算組合單的淨權利金收支\n"
            "□ 確認最大獲利和最大虧損金額可接受\n"
            "□ 設定好獲利 60% 和虧損 50% 的條件單\n"
            "□ 部位不超過總資金 30%"
        )
        
        # 應變方案
        parts.append(
            "\n🚨 緊急應變方案：\n"
            "• 【流動性消失】：如果買賣價差突然拉大超過 20 點，暫停操作\n"
            "• 【突發消息】：如果盤中出現重大利空/利多，立即評估是否平倉\n"
            "• 【系統故障】：準備好券商電話，確保能電話下單平倉\n"
            "• 【單腿成交】：如果組合單只成交一腿，立即補上另一腿或平倉\n"
            "• 【虧損擴大】：虧損超過 50% 立即止血，不要期待反轉"
        )
        
        # 心態調整
        parts.append(
            "\n💭 今天的操作心態：\n"
            "• 結算日組合單是我的專長，但不代表每次都會贏\n"
            "• 只要按照計劃執行，就算虧損也是好的交易\n"
            "• 獲利 60% 就夠了，不要貪心等到最大利潤\n"
            "• 虧損 50% 就認賠，保護本金才能持續交易\n"
            "• 記住：每個結算日都是學習的機會，累積經驗比單次輸贏重要"
        )
        
        # 結束語
        parts.append(
            f"\n🎯 {weekday_text}結算日，我準備好了！\n"
            "組合單策略讓我風險有限、獲利可期。\n"
            "無論今天結果如何，我都會堅持我的交易紀律。\n"
            "讓我們用專業的態度，迎接這個結算日挑戰！"
        )
        
        return "\n".join(parts)
