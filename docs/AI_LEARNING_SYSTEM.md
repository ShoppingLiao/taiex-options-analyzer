# AI 學習系統說明文檔

## 概述

這個系統實現了一個**自我學習的 AI 交易員分析系統**，能夠：

1. 以第一人稱視角進行市場分析
2. 累積歷史分析記錄
3. 從過往經驗中學習並改進
4. 隨著時間推移變得更加精準

## 核心組件

### 1. AI 學習系統 (`ai_learning_system.py`)

**功能：**

- 記錄每次分析的詳細資訊
- 分析 PC Ratio 與市場走勢的相關性
- 識別成功預測的共同特徵
- 建立不同市場情境的經驗庫

**數據儲存：**

- `data/ai_learning/analysis_records.json` - 所有分析記錄
- `data/ai_learning/learned_insights.json` - 學習到的洞察

**分析記錄包含：**

```python
{
    "date": "20260109",
    "close_price": 30120.0,
    "pc_ratio": 0.885,
    "sentiment": "bullish",
    "trend_signal": "bullish",
    "market_observation": "我今天的市場觀察...",
    "position_strategy": "我的部位策略...",
    "risk_assessment": "我的風險評估...",
    "trading_plan": "我的交易計劃...",

    # 後續可以手動更新
    "next_day_price": 30250.0,  # 隔天實際價格
    "prediction_accuracy": "correct",  # 預測準確度
    "lessons_learned": "這次學到..."  # 經驗教訓
}
```

### 2. 每日 AI 交易員分析器 (`ai_daily_analyzer.py`)

**功能：**

- 以第一人稱視角生成市場分析
- 整合歷史經驗和當前市場狀況
- 提供個人化的交易策略和風險評估

**分析輸出：**

1. **市場觀察** - "我今天注意到..."
2. **部位策略** - "我打算這樣布局..."
3. **風險評估** - "我特別警惕這些風險..."
4. **交易計劃** - "明天我的計劃是..."

**經驗等級系統：**

- 🌱 新手 (< 10 筆記錄)
- 📈 學習中 (10-29 筆)
- 🎓 進階 (30-49 筆)
- ⭐ 專家 (50-99 筆)
- 👑 大師 (100+ 筆)

## 學習機制

### 階段 1：記錄累積 (前 5 筆)

- 單純記錄分析內容
- 尚未開始學習

### 階段 2：模式識別 (5+ 筆記錄)

系統開始分析：

1. **PC Ratio 模式**

   - 不同 PC Ratio 範圍與隔天漲跌的關係
   - 極端值的反轉概率

2. **成功因子**

   - 什麼樣的市場情境預測較準確
   - 哪些特徵組合可靠度高

3. **情境經驗**
   - 特定市場狀態下的最佳策略
   - 過往類似情況的結果

### 階段 3：持續改進 (30+ 筆記錄)

- 預測成功率統計
- 風險管理優化
- 策略調整建議

## 使用方式

### 1. 自動記錄

每次生成報告時，系統會自動：

```python
# 在 reporter.py 中自動執行
daily_ai_analysis = self.daily_ai_analyzer.analyze(
    analysis_result,
    options_data,
    sentiment
)
```

### 2. 手動更新驗證結果（可選）

```python
from src.ai_learning_system import AILearningSystem
import json

learning_system = AILearningSystem()

# 讀取記錄
with open('data/ai_learning/analysis_records.json', 'r') as f:
    records = json.load(f)

# 更新特定日期的記錄
for record in records:
    if record['date'] == '20260109':
        record['next_day_price'] = 30250.0  # 隔天實際價格
        record['prediction_accuracy'] = 'correct'  # 或 'partially_correct', 'incorrect'
        record['lessons_learned'] = '這次多方預測正確，PC Ratio 0.885 確實偏多'
        break

# 儲存
with open('data/ai_learning/analysis_records.json', 'w') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
```

### 3. 查看學習進度

```python
from src.ai_learning_system import AILearningSystem

learning_system = AILearningSystem()
print(learning_system.generate_learning_summary())

# 輸出範例：
# 📚 已累積 25 筆分析記錄
# 🎯 預測成功率: 68.2% (15/22)
# 📊 已建立 5 種 PC Ratio 模式分析
```

## 報告呈現

### 每日報告中的 AI 交易員視角標籤頁

1. **經驗徽章**

   - 顯示當前經驗等級和圖示
   - 學習進度統計

2. **關鍵數據**

   - 收盤價、PC Ratio、市場情緒、趨勢信號

3. **第一人稱分析**

   - 市場觀察：以交易員角度描述市場
   - 部位策略：具體的進出場計劃
   - 風險評估：個人化風險識別
   - 交易計劃：明確的執行步驟

4. **歷史洞察**
   - 從過去經驗學到的教訓
   - 類似案例數量

## 數據隱私與管理

### 儲存位置

```
data/
  ai_learning/
    analysis_records.json     # 完整分析記錄
    learned_insights.json     # 學習洞察
```

### 備份建議

定期備份學習數據：

```bash
cp -r data/ai_learning data/ai_learning_backup_$(date +%Y%m%d)
```

### 重置學習（慎用）

```python
# 清空所有學習記錄
import shutil
from pathlib import Path

learning_dir = Path('data/ai_learning')
if learning_dir.exists():
    shutil.rmtree(learning_dir)
    learning_dir.mkdir(parents=True, exist_ok=True)
```

## 未來擴展

### 計劃中的功能

1. **準確率追蹤儀表板**

   - 視覺化預測成功率變化
   - 不同市場條件下的表現分析

2. **自動策略優化**

   - 根據成功率自動調整進場點
   - 動態風險係數計算

3. **多維度學習**

   - 納入技術指標（RSI, MACD 等）
   - 考慮市場情緒指數
   - 整合財經新聞情緒分析

4. **協作學習**
   - 多個 AI 實例間的經驗共享
   - 集體智慧決策機制

## 最佳實踐

### 1. 定期驗證

建議每週回顧並更新 2-3 筆歷史記錄的實際結果

### 2. 誠實記錄

失敗的預測同樣寶貴，是學習的關鍵

### 3. 情境標註

在 `lessons_learned` 中記錄：

- 當時的特殊市場事件
- 預測失敗的可能原因
- 下次遇到類似情況的調整方向

### 4. 漸進式改進

不要期望立即完美，學習是累積過程

## 技術細節

### PC Ratio 分類

```python
- 極低: < 0.7 (極度樂觀)
- 偏低: 0.7 - 0.9 (偏多)
- 中性: 0.9 - 1.1 (均衡)
- 偏高: 1.1 - 1.3 (偏空)
- 極高: > 1.3 (極度悲觀)
```

### 趨勢判斷邏輯

```python
if pc_ratio < 0.8:
    trend = 'bullish'
elif pc_ratio > 1.2:
    trend = 'bearish'
else:
    # 綜合 OI 變化判斷
    if call_oi_change > put_oi_change * 1.5:
        trend = 'bullish'
    elif put_oi_change > call_oi_change * 1.5:
        trend = 'bearish'
    else:
        trend = 'neutral'
```

## 常見問題

**Q: 學習系統會自動改變分析內容嗎？**
A: 目前會根據歷史洞察調整描述，但核心邏輯仍基於當前市場數據。

**Q: 需要多少記錄才能看到學習效果？**
A: 建議至少 20-30 筆記錄，並有 10+ 筆已驗證結果。

**Q: 如何判斷預測是否準確？**
A: 建議標準：

- correct: 方向正確且幅度符合預期（誤差 < 1%）
- partially_correct: 方向正確但幅度有偏差
- incorrect: 方向錯誤

**Q: 學習數據會影響報告生成速度嗎？**
A: 影響極小，即使有數百筆記錄，查詢和分析通常 < 100ms。

## 授權與免責聲明

此 AI 學習系統僅供研究和教育用途。
所有分析內容不構成投資建議，交易有風險，投資需謹慎。

---

**版本**: 1.0
**最後更新**: 2026/01/12
**維護者**: TAIEX Options Analyzer Team
